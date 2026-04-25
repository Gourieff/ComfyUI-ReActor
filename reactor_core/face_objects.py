import numpy as np
import onnxruntime as ort
import os

class Face(dict):
    """
    Класс-хранилище данных о лице. 
    Наследуется от dict для полной обратной совместимости с кодом, 
    который ожидает доступ по ключу (например, face['bbox']).
    """
    def __init__(self, d=None, **kwargs):
        if d is None:
            d = {}
        if kwargs:
            d.update(**kwargs)
        for k, v in d.items():
            setattr(self, k, v)
        # Инициализируем родительский словарь
        super().__init__(d)

    def __setattr__(self, name, value):
        # Если это массив, делаем копию, чтобы избежать багов с мутацией по ссылке
        if isinstance(value, (list, tuple)):
            value = [x for x in value]
        elif isinstance(value, np.ndarray):
            value = value.copy()
        
        super().__setattr__(name, value)
        super().__setitem__(name, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().__setattr__(key, value)

    @property
    def sex(self):
        """Возвращает 'M' или 'F' на основе числового значения gender"""
        gender = self.get('gender', None)
        if gender is None:
            return None
        return 'M' if gender == 1 else 'F'

    @property
    def normed_embedding(self):
        """Автоматически нормализует эмбеддинг для ArcFace / INSwapper"""
        embedding = self.get('embedding', None)
        if embedding is None:
            return None
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm


class BaseONNXModel:
    """
    Базовый класс для всех моделей (Детектор, ArcFace, INSwapper).
    Берет на себя рутину по открытию сессий и чтению входов/выходов.
    """
    def __init__(self, model_file, providers=None):
        self.model_file = model_file
        self.providers = providers or ["CPUExecutionProvider"]
        
        if not os.path.exists(self.model_file):
            raise FileNotFoundError(f"Model file not found: {self.model_file}")

        self.session = ort.InferenceSession(self.model_file, providers=self.providers)
        
        # Получаем параметры входов
        self.inputs = self.session.get_inputs()
        self.input_names = [inp.name for inp in self.inputs]
        
        # Обычно нас интересует шейп первого входа (например, батч, каналы, высота, ширина)
        self.input_shape = self.inputs[0].shape
        
        # Получаем параметры выходов
        self.outputs = self.session.get_outputs()
        self.output_names = [out.name for out in self.outputs]

    def forward(self, *args, **kwargs):
        """Этот метод будет переопределен в классах-наследниках"""
        raise NotImplementedError("Forward method must be implemented by subclasses.")
