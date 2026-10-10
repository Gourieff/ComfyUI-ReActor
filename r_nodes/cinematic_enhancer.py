import os
import torch
import numpy as np
import cv2
import folder_paths
from pathlib import Path
from PIL import Image, ImageEnhance, ImageCms
import comfy.model_management as model_management
from scripts.reactor_logger import logger
from r_modules.shared import state
from reactor_utils import ( 
    progress_bar,
    progress_bar_reset
)
try:
    from colour.io.luts.iridas_cube import read_LUT_IridasCube
    AVAILABLE = True
except Exception as e:
    AVAILABLE = False
    logger.error(f"{e}, ReActorCinematicEnhancer is not available, please install `colour` library: `pip install colour-science`")

folder_paths.add_model_folder_path("luts", os.path.join(folder_paths.models_dir, "luts"))

# Профили для HDR (создаются один раз при импорте для экономии ресурсов)
sRGB_profile = ImageCms.createProfile('sRGB')
Lab_profile = ImageCms.createProfile('LAB')

def get_luts():
    luts = folder_paths.get_filename_list("luts")
    luts = [x for x in luts if x.lower().endswith(".cube") or x.lower().endswith(".spi1d") or x.lower().endswith(".spi3d") or x.lower().endswith(".spimtx") or x.lower().endswith(".csp")]
    luts.sort(key=str.lower)
    luts.insert(0, "none")
    return luts

class ReActorCinematicEnhancer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", ),
                # --- Global Blend ---
                "intensity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0..1, def: 0.5"}),
                # --- LUT ---
                "lut_file": (get_luts(),),
                "lut_strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1, "tooltip": "0..1, def: 0.5"}),
                "lut_gamma_correction": ("BOOLEAN", { "default": True }),
                # --- Film Effect ---
                "film_grain_method": (["advanced","fast"], {"default": "advanced"}),
                "film_grain_power": ("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.01, "tooltip": "0..1, def: 0.1"}),
                "film_grain_scale": ("FLOAT", {"default": 1, "min": 0.1, "max": 10, "step": 0.1, "tooltip": "0.1..1, def: 0.1"}),
                "film_grain_sat": ("FLOAT", {"default": 0.15, "min": 0, "max": 1, "step": 0.01, "tooltip": "(advanced only) 0..1, def: 0.15"}),
                "film_grain_shadows": ("FLOAT", {"default": 0.2, "min": 0, "max": 1, "step": 0.01, "tooltip": "(advanced only) 0..1, def: 0.2"}),
                "film_grain_highs": ("FLOAT", {"default": 0.2, "min": 0, "max": 1, "step": 0.01, "tooltip": "(advanced only) 0..1, def: 0.2"}),
                "film_blur_strength": ("INT", {"default": 1, "min": 0, "max": 256, "step": 1, "tooltip": "(by depth_map) 0..256, def: 1"}),
                "film_focal_depth": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1, "step": 0.01, "tooltip": "(by depth_map) 0..1, def: 0.9"}),
                "film_focus_spread": ("FLOAT", {"default": 2.2, "min": 0.1, "max": 8, "step": 0.1, "tooltip": "(by depth_map) 0..8, def: 2.2"}),
                "film_vignette_intensity": ("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.01, "tooltip": "0..1, def: 0.1"}),
                # --- Color Correct ---
                "cc_temperature": ("FLOAT", {"default": 0, "min": -100, "max": 100, "step": 5, "tooltip": "-100..100, def: 0"}),
                "cc_hue": ("FLOAT", {"default": 0, "min": -90, "max": 90, "step": 5, "tooltip": "-90..90, def: 0"}),
                "cc_brightness": ("FLOAT", {"default": 0, "min": -100, "max": 100, "step": 5, "tooltip": "-100..100, def: 0"}),
                "cc_contrast": ("FLOAT", {"default": 0, "min": -100, "max": 100, "step": 5, "tooltip": "-100..100, def: 0"}),
                "cc_saturation": ("FLOAT", {"default": 0, "min": -100, "max": 100, "step": 5, "tooltip": "-100..100, def: 0"}),
                "cc_gamma": ("FLOAT", {"default": 1, "min": 0.2, "max": 2.2, "step": 0.1, "tooltip": "0.2..2.2, def: 1.0"}),
                # --- HDR Effects ---
                "hdr_intensity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 5.0, "step": 0.01, "tooltip": "0..5, def: 0.5"}),
                "hdr_shadow_intensity": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0..1, def: 0.25"}),
                "hdr_highlight_intensity": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0..1, def: 0.75"}),
                "hdr_contrast": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0..1, def: 0.1"}),
                "hdr_enhance_color": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0..1, def: 0.25"}),
            },
            "optional": {
                "depth_map": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "🌌 ReActor/PostProcessing"
    DESCRIPTION = (
        "Requirements:\n"
        "- pip install colour-science\n"
        "- put LUT-files in models/luts\n"
        "depth_map is optional"
    )

    def execute(self, image, intensity, lut_file, lut_strength, lut_gamma_correction,
                film_grain_method, film_grain_power, film_grain_scale, film_grain_sat, film_grain_shadows, film_grain_highs,film_blur_strength, film_focal_depth, film_focus_spread, film_vignette_intensity,
                cc_temperature, cc_hue, cc_brightness, cc_contrast, cc_saturation, cc_gamma,
                hdr_intensity, hdr_shadow_intensity, hdr_highlight_intensity, hdr_contrast, hdr_enhance_color,
                depth_map=None):
        
        if not AVAILABLE:
            logger.error("ReActorCinematicEnhancer is not available, please install `colour` library: `pip install colour-science`")
            return (image,)
        
        # 1. Загрузка LUT

        if lut_file != "none":
            lut_file_path = folder_paths.get_full_path("luts", lut_file)
            lut = read_LUT_IridasCube(lut_file_path) if lut_file_path and Path(lut_file_path).exists() else None
            if lut:
                lut.name = lut_file
                logger.status(f"LUT {lut_file} selected")
        else:
            lut = None

        batch_size = image.shape[0]
        result_batch = []

        pbar = progress_bar(batch_size)

        logger.status(f"Enhancing...")

        for b in range(batch_size):

            if state.interrupted or model_management.processing_interrupted():
                logger.status("Interrupted by User")
                break

            # --- БАЗА: NumPy (0-1) ---
            orig_np = image[b].cpu().numpy().copy()
            img_np = orig_np.copy()
            
            # --- 1. LUT ---
            if lut:
                lut_img = img_np.copy()
                if lut_gamma_correction:
                    lut_img = np.clip(lut_img ** (1/2.2), 0, 1)
                lut_img = lut.apply(lut_img)
                if lut_gamma_correction:
                    lut_img = np.clip(lut_img ** 2.2, 0, 1)
                
                if lut_strength < 1.0:
                    img_np = lut_strength * lut_img + (1 - lut_strength) * img_np
                else:
                    img_np = lut_img

            # Подготовка маски глубины (если есть)
            depth_np = None
            if depth_map is not None:
                d_tensor = depth_map[b if depth_map.shape[0] > 1 else 0].cpu().numpy()
                if d_tensor.shape[:2] != img_np.shape[:2]:
                    d_tensor = cv2.resize(d_tensor, (img_np.shape[1], img_np.shape[0]), interpolation=cv2.INTER_LINEAR)
                # Если глубина RGB, берем один канал
                depth_np = d_tensor[:,:,0] if d_tensor.ndim == 3 else d_tensor

            # --- 2. FILM EFFECT ---
            # Виньетка (OpenCV)
            if film_vignette_intensity > 0:
                h, w = img_np.shape[:2]
                Y, X = np.ogrid[:h, :w]
                center_y, center_x = h / 2, w / 2
                dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
                max_dist = np.sqrt(center_x**2 + center_y**2)
                vignette = 1 - (dist_from_center / max_dist) * film_vignette_intensity
                img_np = np.clip(img_np * vignette[..., np.newaxis], 0, 1)

            # Глубинное размытие (пошаговая реализация)
            if film_blur_strength > 0 and depth_np is not None:
                # Нормализуем разницу глубины относительно точки фокуса
                depth_diff = np.abs(depth_np - film_focal_depth) * film_focus_spread
                depth_diff = np.clip(depth_diff, 0, 1)
                
                # Пошаговый блендинг (5 шагов для плавности)
                steps = 5
                blurred_fg = np.zeros_like(img_np)
                for step in range(steps + 1):
                    step_blur = int((film_blur_strength * step / steps) // 2 * 2 + 1)
                    if step_blur > 1:
                        blur_layer = cv2.GaussianBlur(img_np, (step_blur, step_blur), 0)
                    else:
                        blur_layer = img_np
                    
                    # Маска весов для текущего шага
                    mask = np.clip(1.0 - np.abs(depth_diff * steps - step), 0, 1)
                    blurred_fg += blur_layer * mask[..., np.newaxis]
                img_np = blurred_fg

            # --- 3. COLOR CORRECT ---
            fg_img = Image.fromarray((img_np * 255).astype(np.uint8))
            
            # Яркость и Контраст (PIL)
            if cc_brightness != 0:
                fg_img = ImageEnhance.Brightness(fg_img).enhance(1 + (cc_brightness / 100))
            if cc_contrast != 0:
                fg_img = ImageEnhance.Contrast(fg_img).enhance(1 + (cc_contrast / 100))
            
            fg_cv = np.array(fg_img).astype(np.float32) / 255.0

            # Температура
            temp_val = cc_temperature / 100
            if temp_val > 0:
                fg_cv[:, :, 0] = np.clip(fg_cv[:, :, 0] * (1 + temp_val), 0, 1)
                fg_cv[:, :, 1] = np.clip(fg_cv[:, :, 1] * (1 + temp_val * 0.4), 0, 1)
            elif temp_val < 0:
                fg_cv[:, :, 2] = np.clip(fg_cv[:, :, 2] * (1 - temp_val), 0, 1)
            
            # Гамма
            if cc_gamma != 1.0:
                fg_cv = np.clip(np.power(fg_cv, cc_gamma), 0, 1)

            # HSV для Hue и Saturation
            if cc_hue != 0 or cc_saturation != 0:
                hsv = cv2.cvtColor((fg_cv * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
                if cc_hue != 0:
                    hsv[:, :, 0] = (hsv[:, :, 0] + (cc_hue / 2)) % 180 # В OpenCV Hue до 180
                if cc_saturation != 0:
                    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + cc_saturation / 100), 0, 255)
                fg_cv = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
            
            img_np = fg_cv

            # --- 4. FILM GRAIN ---
            if film_grain_power > 0:

                # --- 4.1 ADVANCED NATIVE GRAIN ---
                if film_grain_method == "advanced":
                    # 1) Генерируем базовый цветной шум
                    noise_rgb = np.random.normal(0, film_grain_power, img_np.shape).astype(np.float32)
                    
                    # 2) Генерируем монохромный шум (усреднение по каналам)
                    noise_mono = np.mean(noise_rgb, axis=-1, keepdims=True)
                    
                    # 3) Смешиваем цветность зерна (grain_sat)
                    noise = noise_rgb * film_grain_sat + noise_mono * (1.0 - film_grain_sat)
                    
                    # 4) Масштабирование зерна
                    if film_grain_scale != 1.0:
                        h, w = img_np.shape[:2]
                        small_noise = cv2.resize(noise, (int(w / film_grain_scale), int(h / film_grain_scale)))
                        noise = cv2.resize(small_noise, (w, h), interpolation=cv2.INTER_LINEAR)
                    
                    # 5) Кинематографичная маскировка по яркости (Luminance)
                    # Вычисляем воспринимаемую яркость пикселей
                    lum = 0.299 * img_np[:,:,0] + 0.587 * img_np[:,:,1] + 0.114 * img_np[:,:,2]
                    lum = lum[..., np.newaxis]
                    
                    # Создаем карту весов шума: 
                    # Средние тона (0.5) получают вес 1.0. 
                    # Тени (0.0) получают вес film_grain_shadows.
                    # Блики (1.0) получают вес film_grain_highs.
                    grain_mask = np.where(
                        lum < 0.5,
                        film_grain_shadows + (1.0 - film_grain_shadows) * (lum * 2.0), # Плавный переход от теней к средним
                        1.0 - (1.0 - film_grain_highs) * ((lum - 0.5) * 2.0)           # Плавный переход от средних к бликам
                    )
                    
                    # Накладываем шум с учетом яркостной маски
                    img_np = np.clip(img_np + noise * grain_mask, 0, 1)

                # --- 4.2 FAST GRAIN ---
                else:
                    noise = np.random.normal(0, film_grain_power, img_np.shape).astype(np.float32)
                    # Масштабирование шума
                    if film_grain_scale != 1.0:
                        h, w = img_np.shape[:2]
                        small_noise = cv2.resize(noise, (int(w / film_grain_scale), int(h / film_grain_scale)))
                        noise = cv2.resize(small_noise, (w, h), interpolation=cv2.INTER_LINEAR)
                    img_np = np.clip(img_np + noise * 0.5, 0, 1)

            # --- 5. HDR EFFECTS ---
            if hdr_intensity > 0:
                final_pil = Image.fromarray((img_np * 255).astype(np.uint8))

                # Основная математика тонирования LAB
                img_lab = ImageCms.profileToProfile(final_pil, sRGB_profile, Lab_profile, outputMode='LAB')
                luminance, a, b = img_lab.split()
                base = np.array(luminance, dtype=np.float32)

                scaled_shadow = (hdr_shadow_intensity ** 2) * hdr_intensity
                scaled_highlight = (hdr_highlight_intensity ** 2) * hdr_intensity
                
                shadow_mask = np.clip((1 - (base / 255)) ** 2, 0, 1)
                highlight_mask = np.clip((base / 255) ** 2, 0, 1)
                
                adj_shadows = np.clip(base * (1 - shadow_mask * scaled_shadow), 0, 255)
                adj_highlights = np.clip(base + (255 - base) * highlight_mask * scaled_highlight, 0, 255)
                
                adj_lum = np.clip(adj_shadows + adj_highlights - base, 0, 255)
                final_lum = np.clip(base * (1 - hdr_intensity) + adj_lum * hdr_intensity, 0, 255).astype(np.uint8)

                merged_lab = Image.merge('LAB', (Image.fromarray(final_lum), a, b))
                final_pil = ImageCms.profileToProfile(merged_lab, Lab_profile, sRGB_profile, outputMode='RGB')
                
                if hdr_contrast > 0:
                    final_pil = ImageEnhance.Contrast(final_pil).enhance(1 + hdr_contrast)
                if hdr_enhance_color > 0:
                    final_pil = ImageEnhance.Color(final_pil).enhance(1 + hdr_enhance_color * 0.2)
                
                # Возвращаем HDR в рабочий массив для финального смешивания
                img_np = np.array(final_pil).astype(np.float32) / 255.0

            # --- 6. GLOBAL INTENSITY BLEND ---
            if intensity < 1.0:
                img_np = orig_np * (1.0 - intensity) + img_np * intensity
            
            # Возврат в тензор
            out_tensor = torch.from_numpy(img_np)
            result_batch.append(out_tensor)

            pbar.update(1)

        progress_bar_reset(pbar)

        return (torch.stack(result_batch),)
