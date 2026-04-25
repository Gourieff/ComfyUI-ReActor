import sys
import os

# Добавляем путь расширения, чтобы Питон видел наши папки (r_facelib, scripts и т.д.)
repo_dir = os.path.dirname(os.path.realpath(__file__))
if repo_dir not in sys.path:
    sys.path.insert(0, repo_dir)

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
