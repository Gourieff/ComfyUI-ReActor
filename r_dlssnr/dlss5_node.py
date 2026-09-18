import torch
import numpy as np
import os
import comfy.model_management as model_management
from scripts.reactor_logger import logger
from .dlss5_core import DLSSStandaloneManager
from r_modules.shared import state
from reactor_utils import (
    batch_tensor_to_pil, 
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
                "auto_mask": ("BOOLEAN", {"default": False, "label_off": "OFF", "label_on": "ON", "tooltip": "Smart Protection Mask"}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("enhanced_image",)
    FUNCTION = "enhance"
    CATEGORY = "🌌 ReActor"
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

        enhanced_batch = []

        pil_images = batch_tensor_to_pil(image)
        pbar = progress_bar(len(pil_images))
        
        for i in range(len(image)):

            if state.interrupted or model_management.processing_interrupted():
                logger.status("Interrupted by User")
                break

            img_np = np.ascontiguousarray(image[i].cpu().numpy().astype(np.float32))
            dest_np = np.ascontiguousarray(np.zeros_like(img_np))
            
            mask_np = None
            if mask is not None:
                mask_np = np.ascontiguousarray(mask[i].cpu().numpy().astype(np.float32))
            
            # Вызываем Host-обработчик (без CUDA конфликтов)
            self.manager.process_host(
                source=img_np,
                destination=dest_np,
                settings=settings,
                reset=True,
                mask=mask_np
            )
            
            out_tensor = torch.from_numpy(dest_np).to(self.device) 
            enhanced_batch.append(out_tensor)

            pbar.update(1)

        progress_bar_reset(pbar)
        
        return (torch.stack(enhanced_batch),)
