# https://github.com/xinntao/BasicSR
# Lazy: Originally imported all submodules eagerly (archs, data, losses,
# metrics, models, ops, etc.) which pulled in torchvision, cv2, scipy via
# transitive imports. Since ReActor only uses ARCH_REGISTRY and
# get_root_logger from r_basicsr.utils, we skip the wildcard imports to
# avoid adding ~4s to ComfyUI startup.
from .version import __gitsha__, __version__
