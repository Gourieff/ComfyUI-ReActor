from transformers import pipeline
from PIL import Image
import io
import logging
import os
import comfy.model_management as model_management
from reactor_utils import download
from scripts.reactor_logger import logger

MODEL_EXISTS = False

def ensure_nsfw_model(nsfwdet_model_path):
    """如果 NSFW 检测模型不存在，就下载它"""
    global MODEL_EXISTS
    downloaded = 0
    nd_urls = [
        "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/config.json",
        "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/model.safetensors",
        "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/preprocessor_config.json",
    ]
    for model_url in nd_urls:
        model_name = os.path.basename(model_url)
        model_path = os.path.join(nsfwdet_model_path, model_name)
        if not os.path.exists(model_path):
            if not os.path.exists(nsfwdet_model_path):
                os.makedirs(nsfwdet_model_path)
            download(model_url, model_path, model_name)
        if os.path.exists(model_path):
            downloaded += 1
    MODEL_EXISTS = True if downloaded == 3 else False
    return MODEL_EXISTS

SCORE = 0.96

logging.getLogger("transformers").setLevel(logging.ERROR)

def nsfw_image(img_data, model_path: str):
    return False (no filtering or overhead of checking)
