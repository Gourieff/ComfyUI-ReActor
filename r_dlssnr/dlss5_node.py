import torch
import numpy as np
import os
from tqdm import tqdm
import comfy.model_management as model_management
from scripts.reactor_logger import logger
from .dlss5_core import DLSSStandaloneManager
from r_modules.shared import state
from reactor_utils import (
    progress_bar,
    progress_bar_reset
)

class DLSS5FrameEnhancer:
    def __init__(self):
        self.device = model_management.get_torch_device()
        self.manager = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "style": (["Default", "Nature", "Cinematic"],),
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "0..2, def: 1.0"}),
                "local_tone": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "0..2, def: 0.0"}),
                "local_structure": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "0..2, def: 1.0"}),
                "skin_structure": ("FLOAT", {"default": 0.5, "min": -1.0, "max": 2.0, "step": 0.05, "tooltip": "-1..2, def: 0.5"}),
                "color_strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "0..1, def: 0.5"}),
                "tone_preservation": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "0..1, def: 0.5"}),
                "face_skin_protection": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "0..1, def: 0.0"}),
                "grain_preservation": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "0..1, def: 0.0"}),
                "nr_passes": ("INT", {"default": 1, "min": 1, "max": 4, "tooltip": "0..4, def: 1"}),
                "auto_mask": ("BOOLEAN", {"default": False, "label_off": "OFF", "label_on": "ON", "tooltip": "AI Automatic masking of complex areas to prevent over-detailing"}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("enhanced_image",)
    FUNCTION = "enhance"
    CATEGORY = "🌌 ReActor/PostProcessing"
    DESCRIPTION = (
        "Requirements:\n"
        "- NVIDIA display driver >= 616.x\n"
        "- NVIDIA RTX 40/50-series GPU\n"
        "(compatibility with older RTX series is unconfirmed)\n"
        "- DLLs: neuroframe_caller.dll, neuroframe_engine.dll, nvngx_dlssnr.dll\nin custom_nodes/ComfyUI-ReActor/r_dlssnr/dll\nor custom_nodes/comfyui-reactor-node/r_dlssnr/dll\n"
        "(see README.md in dll folder for instructions)"
    )

    def load_bridge(self):
        if self.manager is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dll_dir = os.path.join(current_dir, "dll")
            self.manager = DLSSStandaloneManager(dll_dir)
            ordinal = getattr(self.device, 'index', 0) if self.device.index is not None else 0
            self.manager.initialize(ordinal)
            logger.status(f"DLSS-5 Bridge initialized on GPU {ordinal}")

    def _run_with_tiling(
        self,
        img_np: np.ndarray,
        mask_np: np.ndarray | None,
        settings: dict,
        ui_pbar=None,
        console_pbar=None,
        frame_idx: int = 0,
        batch_size: int = 1,
        max_tile: int = 4096,
        overlap: int = 64,
    ) -> np.ndarray | None:
        h, w, c = img_np.shape

        # 1. Если картинка влезает целиком — обрабатываем за 1 проход
        if h <= max_tile and w <= max_tile:
            if console_pbar is not None:
                console_pbar.set_description(f"[ReActor][DLSS-5] {'Batch ' if batch_size > 1 else ''}({w}x{h})")
            dest_np = np.ascontiguousarray(np.zeros_like(img_np))
            self.manager.process_host(
                source=img_np,
                destination=dest_np,
                settings=settings,
                reset=True,
                mask=mask_np,
            )
            if ui_pbar is not None:
                ui_pbar.update(1)
            if console_pbar is not None:
                console_pbar.update(1)
            return dest_np

        # 2. Если картинка огромная — режем на тайлы
        out_acc = np.zeros((h, w, c), dtype=np.float32)
        weight_acc = np.zeros((h, w, 1), dtype=np.float32)

        stride = max_tile - overlap
        y_steps = list(range(0, max(1, h - overlap), stride))
        x_steps = list(range(0, max(1, w - overlap), stride))
        num_tiles = len(y_steps) * len(x_steps)
        tile_idx = 0

        for y in y_steps:
            for x in x_steps:
                if state.interrupted or model_management.processing_interrupted():
                    logger.status("Interrupted by User")
                    return None

                tile_idx += 1
                if console_pbar is not None:
                    if batch_size > 1:
                        console_pbar.set_description(
                            f"[ReActor][DLSS-5] Frame {frame_idx + 1}/{batch_size} (Tile {tile_idx}/{num_tiles})"
                        )
                    else:
                        console_pbar.set_description(f"[ReActor][DLSS-5] Tiling ({w}x{h})")

                y2 = min(y + max_tile, h)
                x2 = min(x + max_tile, w)
                y1 = max(0, y2 - max_tile)
                x1 = max(0, x2 - max_tile)

                tile_in = np.ascontiguousarray(img_np[y1:y2, x1:x2, :])
                tile_out = np.ascontiguousarray(np.zeros_like(tile_in))
                tile_mask = np.ascontiguousarray(mask_np[y1:y2, x1:x2]) if mask_np is not None else None

                self.manager.process_host(
                    source=tile_in,
                    destination=tile_out,
                    settings=settings,
                    reset=True,
                    mask=tile_mask,
                )

                th, tw = tile_out.shape[:2]
                wy = np.ones(th, dtype=np.float32)
                wx = np.ones(tw, dtype=np.float32)

                if y1 > 0:
                    wy[:overlap] = np.linspace(0, 1, overlap, dtype=np.float32)
                if y2 < h:
                    wy[-overlap:] = np.linspace(1, 0, overlap, dtype=np.float32)
                if x1 > 0:
                    wx[:overlap] = np.linspace(0, 1, overlap, dtype=np.float32)
                if x2 < w:
                    wx[-overlap:] = np.linspace(1, 0, overlap, dtype=np.float32)

                weight = wy[:, None, None] * wx[None, :, None]
                out_acc[y1:y2, x1:x2, :] += tile_out * weight
                weight_acc[y1:y2, x1:x2, :] += weight

                if ui_pbar is not None:
                    ui_pbar.update(1)
                if console_pbar is not None:
                    console_pbar.update(1)

        return out_acc / np.maximum(weight_acc, 1e-6)
    
    def enhance(self, image, style, intensity, local_tone, local_structure, 
                skin_structure, color_strength, tone_preservation, 
                face_skin_protection, grain_preservation, nr_passes, auto_mask, mask=None):
        
        self.load_bridge()
        
        style_map = {"Default": 0, "Nature": 1, "Cinematic": 2}
        settings = {
            "style": style_map[style], "intensity": intensity, "local_tone": local_tone,
            "local_structure": local_structure, "skin_structure": skin_structure,
            "color_strength": color_strength, "tone_preservation": tone_preservation,
            "face_skin_protection": face_skin_protection, "grain_preservation": grain_preservation,
            "nr_passes": nr_passes, "auto_mask": auto_mask,
            "shimmer_suppression": 0.0, "prefer_nvof": False
        }

        max_tile, overlap = 4096, 64
        stride = max_tile - overlap
        batch_size = len(image)

        total_ui_steps = sum(
            1 if (img.shape[0] <= max_tile and img.shape[1] <= max_tile) else
            len(range(0, max(1, img.shape[0] - overlap), stride)) * len(range(0, max(1, img.shape[1] - overlap), stride))
            for img in image
        )

        ui_pbar = progress_bar(total_ui_steps)

        is_tiled = total_ui_steps > batch_size
        console_pbar = tqdm(
            total=total_ui_steps,
            desc="[ReActor][DLSS-5] Processing",
            unit="tile" if is_tiled else "frame",
            dynamic_ncols=True,
            leave=True,
        )

        enhanced_batch = []
        
        try:
            for i in range(batch_size):
                if state.interrupted or model_management.processing_interrupted():
                    logger.status("Interrupted by User")
                    break

                img_np = np.ascontiguousarray(image[i].cpu().numpy().astype(np.float32))
                mask_np = None
                if mask is not None:
                    mask_np = np.ascontiguousarray(mask[i].cpu().numpy().astype(np.float32))

                dest_np = self._run_with_tiling(
                    img_np=img_np,
                    mask_np=mask_np,
                    settings=settings,
                    ui_pbar=ui_pbar,
                    console_pbar=console_pbar,
                    frame_idx=i,
                    batch_size=batch_size,
                    max_tile=max_tile,
                    overlap=overlap,
                )

                if dest_np is None:
                    break

                out_tensor = torch.from_numpy(dest_np).to(self.device)
                enhanced_batch.append(out_tensor)
        finally:
            console_pbar.close()

        progress_bar_reset(ui_pbar)
        
        return (torch.stack(enhanced_batch),)
