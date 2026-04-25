import os
import zipfile
from reactor_utils import download  # Твоя функция скачивания из utils
from .face_objects import Face
from .inswap import SCRFD, ArcFaceONNX, Attribute, Landmark
from scripts.reactor_logger import logger

class ReActorFaceAnalysis:
    """
    Главный класс-оркестратор. 
    Берет картинку, находит лица, определяет пол/возраст и вычисляет эмбеддинги.
    """
    def __init__(self, name="buffalo_l", root="./models/insightface", providers=None):
        self.name = name
        self.root = root
        self.providers = providers or ["CPUExecutionProvider"]
        self.models = {}

        model_dir = os.path.join(root, "models", name)
        os.makedirs(model_dir, exist_ok=True)

        det_file = os.path.join(model_dir, "det_10g.onnx")
        rec_file = os.path.join(model_dir, "w600k_r50.onnx")
        attr_file = os.path.join(model_dir, "genderage.onnx")
        lmk2d_file = os.path.join(model_dir, "2d106det.onnx")
        lmk3d_file = os.path.join(model_dir, "1k3d68.onnx")

        # Если файлов нет - качаем архив
        if not (os.path.exists(det_file) and os.path.exists(rec_file) and os.path.exists(attr_file)):
            zip_url = "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/buffalo_l.zip"
            zip_path = os.path.join(model_dir, f"{name}.zip")

            logger.status(f"Downloading {name} models archive...")
            download(zip_url, zip_path, f"{name}.zip")

            logger.status(f"Extracting {name} models...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(model_dir)
                logger.status("Extraction completed!")
            except zipfile.BadZipFile:
                logger.error("Downloaded zip file is corrupted. Please try again.")
            finally:
                # В любом случае пытаемся удалить архив, чтобы не занимать место
                if os.path.exists(zip_path):
                    os.remove(zip_path)

        # Инициализируем только те модели, которые физически есть в папке
        if os.path.exists(det_file):
            self.models["detection"] = SCRFD(det_file, providers=self.providers)
        if os.path.exists(rec_file):
            self.models["recognition"] = ArcFaceONNX(rec_file, providers=self.providers)
        if os.path.exists(attr_file):
            self.models["attribute"] = Attribute(attr_file, providers=self.providers)
        if os.path.exists(lmk2d_file):
            self.models["landmark_2d"] = Landmark(lmk2d_file, providers=self.providers)
        if os.path.exists(lmk3d_file):
            self.models["landmark_3d"] = Landmark(lmk3d_file, providers=self.providers)

        if "detection" not in self.models:
            raise FileNotFoundError(
                f"Detection model (det_10g.onnx) not found at {det_file}. "
                "Please ensure the buffalo_l models are downloaded and extracted properly."
            )

    def prepare(self, ctx_id=0, det_size=(640, 640), det_thresh=0.5):
        self.det_size = det_size
        self.det_thresh = det_thresh

    def get(self, img, max_num=0):
        bboxes, kpss = self.models["detection"].detect(
            img, 
            det_thresh=self.det_thresh, 
            input_size=self.det_size, 
            max_num=max_num
        )
        
        if bboxes.shape[0] == 0:
            return []

        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = kpss[i] if kpss is not None else None
            
            face = Face(bbox=bbox, kps=kps, det_score=det_score)

            if "attribute" in self.models:
                self.models["attribute"].get(img, face)
            
            if "recognition" in self.models:
                self.models["recognition"].get(img, face)
            
            if "landmark_2d" in self.models:
                self.models["landmark_2d"].get(img, face)
                
            if "landmark_3d" in self.models:
                self.models["landmark_3d"].get(img, face)
                
            ret.append(face)
            
        return ret
