import sys
import os

repo_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, repo_dir)

# Place aside existing modules if using a1111 web ui
modules_used = [
    "modules",
    "modules.images",
    "modules.processing",
    "modules.scripts_postprocessing",
    "modules.scripts",
    "modules.shared",
]
original_webui_modules = {}
for module in modules_used:
    if module in sys.modules:
        original_webui_modules[module] = sys.modules.pop(module)

# Proceed with node setup
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# Clean up imports safely - only remove reactor-specific modules
# Don't aggressively clean sys.modules as this corrupts other nodes' imports
sys.path.remove(repo_dir)

# Restore original modules
sys.modules.update(original_webui_modules)
