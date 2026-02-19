# Lazy imports via __getattr__ to avoid pulling in cv2 and torchvision at
# module load time.  The original eager imports added ~4s to ComfyUI startup
# because img_util.py and img_process_util.py import cv2 and torchvision at
# their top level.

__all__ = [
    #  color_util.py
    'bgr2ycbcr',
    'rgb2ycbcr',
    'rgb2ycbcr_pt',
    'ycbcr2bgr',
    'ycbcr2rgb',
    # file_client.py
    'FileClient',
    # img_util.py
    'img2tensor',
    'tensor2img',
    'imfrombytes',
    'imwrite',
    'crop_border',
    # logger.py
    'MessageLogger',
    'AvgTimer',
    'init_tb_logger',
    'init_wandb_logger',
    'get_root_logger',
    'get_env_info',
    # misc.py
    'set_random_seed',
    'get_time_str',
    'mkdir_and_rename',
    'make_exp_dirs',
    'scandir',
    'check_resume',
    'sizeof_fmt',
    # diffjpeg
    'DiffJPEG',
    # img_process_util
    'USMSharp',
    'usm_sharp',
]

# Map each public name to (submodule, name_in_submodule).
_LAZY_IMPORTS = {
    'bgr2ycbcr': ('.color_util', 'bgr2ycbcr'),
    'rgb2ycbcr': ('.color_util', 'rgb2ycbcr'),
    'rgb2ycbcr_pt': ('.color_util', 'rgb2ycbcr_pt'),
    'ycbcr2bgr': ('.color_util', 'ycbcr2bgr'),
    'ycbcr2rgb': ('.color_util', 'ycbcr2rgb'),
    'DiffJPEG': ('.diffjpeg', 'DiffJPEG'),
    'FileClient': ('.file_client', 'FileClient'),
    'USMSharp': ('.img_process_util', 'USMSharp'),
    'usm_sharp': ('.img_process_util', 'usm_sharp'),
    'crop_border': ('.img_util', 'crop_border'),
    'imfrombytes': ('.img_util', 'imfrombytes'),
    'img2tensor': ('.img_util', 'img2tensor'),
    'imwrite': ('.img_util', 'imwrite'),
    'tensor2img': ('.img_util', 'tensor2img'),
    'AvgTimer': ('.logger', 'AvgTimer'),
    'MessageLogger': ('.logger', 'MessageLogger'),
    'get_env_info': ('.logger', 'get_env_info'),
    'get_root_logger': ('.logger', 'get_root_logger'),
    'init_tb_logger': ('.logger', 'init_tb_logger'),
    'init_wandb_logger': ('.logger', 'init_wandb_logger'),
    'check_resume': ('.misc', 'check_resume'),
    'get_time_str': ('.misc', 'get_time_str'),
    'make_exp_dirs': ('.misc', 'make_exp_dirs'),
    'mkdir_and_rename': ('.misc', 'mkdir_and_rename'),
    'scandir': ('.misc', 'scandir'),
    'set_random_seed': ('.misc', 'set_random_seed'),
    'sizeof_fmt': ('.misc', 'sizeof_fmt'),
}


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(module_path, __package__)
        value = getattr(module, attr_name)
        # Cache on the module dict so subsequent accesses are fast.
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
