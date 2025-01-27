from transformers import pipeline
from PIL import Image
import logging
import os
from reactor_utils import download

def ensure_nsfw_model(model_path):
    """Download NSFW detection model if it doesn't exist"""
    if not os.path.exists(model_path):
        os.makedirs(model_path)
        nd_urls = [
            "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/config.json",
            "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/confusion_matrix.png",
            "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/model.safetensors",
            "https://huggingface.co/AdamCodd/vit-base-nsfw-detector/resolve/main/preprocessor_config.json",
        ]
        for model_url in nd_urls:
            model_name = os.path.basename(model_url)
            model_path = os.path.join(model_path, model_name)
            download(model_url, model_path, model_name)

SCORE = 0.965 # 0.965 and less - is safety content

logging.getLogger('transformers').setLevel(logging.ERROR)

def nsfw_image(img_path: str, model_path: str):
    ensure_nsfw_model(model_path)
    with Image.open(img_path) as img:
        predict = pipeline("image-classification", model=model_path)
        result = predict(img)
        return True if result[0]["score"] > SCORE else False
