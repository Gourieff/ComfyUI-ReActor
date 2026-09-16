import ctypes
import threading
from dataclasses import dataclass
from typing import Any
import numpy as np

# --- КОНСТАНТЫ ---
BRIDGE_ABI_VERSION = 6
MEMORY_HOST = 0
MEMORY_CUDA = 1
MEMORY_NONE = 2

class NeuralBridgeError(Exception):
    pass

# --- C-СТРУКТУРЫ ДЛЯ ВЗАИМОДЕЙСТВИЯ С DLL ---

class RenderParameters(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("style", ctypes.c_int32),
        ("intensity", ctypes.c_float),
        ("tone", ctypes.c_float),
        ("structure", ctypes.c_float),
        ("skin", ctypes.c_float),
        ("automask", ctypes.c_int32),
        ("reset", ctypes.c_int32),
        ("color_strength", ctypes.c_float),
        ("tone_preservation", ctypes.c_float),
        ("mask_memory_type", ctypes.c_uint32),
        ("mask_width", ctypes.c_uint32),
        ("mask_height", ctypes.c_uint32),
        ("mask_stride", ctypes.c_uint32),
        ("mask_plane", ctypes.c_uint64),          # Из-за uint64 здесь будет 4 байта системного отступа
        ("face_skin_protection", ctypes.c_float),
        ("grain_preservation", ctypes.c_float),
        ("nr_passes", ctypes.c_int32),
        ("shimmer_suppression", ctypes.c_float),
        ("prefer_nvof", ctypes.c_int32),
    ]


class DLSSStandaloneManager:
    def __init__(self, dll_dir: str):
        self._lock = threading.RLock()
        self._library = None
        self.dll_dir = dll_dir

    def initialize(self, ordinal: int):
        with self._lock:
            if self._library is not None:
                return True
                
            import os
            
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(self.dll_dir)
                
            engine_path = os.path.join(self.dll_dir, "neuroframe_engine.dll")
            if not os.path.exists(engine_path):
                raise NeuralBridgeError(f"Missing DLL: {engine_path}")
            
            loader = getattr(ctypes, "WinDLL", ctypes.CDLL)
            try:
                self._library = loader(engine_path)
            except OSError as exc:
                raise NeuralBridgeError(f"DLL load failed: {exc}")
                
            # Сигнатура инициализации
            self._library.dlss5nr_init.argtypes = [
                ctypes.c_int, ctypes.c_wchar_p, ctypes.c_char_p, ctypes.c_int
            ]
            self._library.dlss5nr_init.restype = ctypes.c_int
            
            # Сигнатура HOST-рендера (process_v6 вместо process_cuda_v6)
            c_float_p = ctypes.POINTER(ctypes.c_float)
            self._library.dlss5nr_process_v6.argtypes = [
                c_float_p, c_float_p, ctypes.c_int, ctypes.c_int,
                ctypes.POINTER(RenderParameters), ctypes.c_char_p, ctypes.c_int
            ]
            self._library.dlss5nr_process_v6.restype = ctypes.c_int

            try:
                self._library.dlss5nr_frame_abi_version.argtypes = []
                self._library.dlss5nr_frame_abi_version.restype = ctypes.c_uint32
                self.actual_abi = self._library.dlss5nr_frame_abi_version()
            except Exception:
                self.actual_abi = BRIDGE_ABI_VERSION

            error = ctypes.create_string_buffer(4096)
            ok = self._library.dlss5nr_init(ordinal, self.dll_dir, error, len(error))
            
            if not ok:
                err_msg = error.value.decode('utf-8', errors='ignore')
                raise NeuralBridgeError(f"Bridge initialization failed: {err_msg}")
            
            return True

    def process_host(self, source: np.ndarray, destination: np.ndarray, settings: dict, reset: bool, mask: np.ndarray = None):
        with self._lock:
            error = ctypes.create_string_buffer(4096)
            
            params = RenderParameters()
            params.struct_size = ctypes.sizeof(RenderParameters)
            params.abi_version = getattr(self, "actual_abi", BRIDGE_ABI_VERSION)
            
            params.style = int(settings.get("style"))
            params.intensity = float(settings.get("intensity"))
            params.tone = float(settings.get("local_tone"))
            params.structure = float(settings.get("local_structure"))
            params.skin = float(settings.get("skin_structure"))
            params.automask = int(bool(settings.get("auto_mask")))
            params.reset = int(bool(reset))
            params.color_strength = float(settings.get("color_strength"))
            params.tone_preservation = float(settings.get("tone_preservation"))
            params.face_skin_protection = float(settings.get("face_skin_protection"))
            params.grain_preservation = float(settings.get("grain_preservation"))
            params.nr_passes = int(settings.get("nr_passes"))
            params.shimmer_suppression = float(settings.get("shimmer_suppression", 0.0))
            params.prefer_nvof = int(bool(settings.get("prefer_nvof", False)))
            
            # Обработка маски через HOST память
            params.mask_memory_type = MEMORY_NONE
            if mask is not None:
                params.mask_memory_type = MEMORY_HOST
                params.mask_width = int(mask.shape[1])
                params.mask_height = int(mask.shape[0])
                params.mask_stride = int(mask.strides[0])
                params.mask_plane = int(mask.ctypes.data) # Передаем указатель RAM
            
            c_float_p = ctypes.POINTER(ctypes.c_float)
            
            # Вызываем HOST функцию (DLL сама разберется с видеокартой)
            ok = self._library.dlss5nr_process_v6(
                source.ctypes.data_as(c_float_p),
                destination.ctypes.data_as(c_float_p),
                source.shape[1],
                source.shape[0],
                ctypes.byref(params),
                error,
                len(error)
            )
            
            if not ok:
                err_msg = error.value.decode('utf-8', errors='ignore')
                raise NeuralBridgeError(f"DLSS-5 process failed: {err_msg}")
