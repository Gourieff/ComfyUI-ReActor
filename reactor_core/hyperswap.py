import cv2
import numpy as np
from .face_objects import BaseONNXModel

class HyperSwapper(BaseONNXModel):
    """Класс для работы с моделями семейства Hyperswap"""

    def __init__(self, model_file, providers=None):
        super().__init__(model_file, providers)

    # Функция для получения 5 ключевых точек из объекта Face
    def get_landmarks_5(self, face):
        if hasattr(face, 'landmark_5') and face.landmark_5 is not None:
            return face.landmark_5
        elif hasattr(face, 'kps') and face.kps is not None:
            return face.kps
        elif hasattr(face, 'landmark') and face.landmark is not None:
            if face.landmark.shape[0] >= 68:
                idxs = [36, 45, 30, 48, 54]
                return face.landmark[idxs]
        return None

    # Функция для вычисления аффинного преобразования
    def get_affine_transform(self, src_pts, dst_pts):
        M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
        return M
    
    # Создаём градиентную маску овальной формы без обрезки 
    def create_gradient_mask(self, crop_size=256):
        # 1. Создаём пустую маску (все пиксели = 0)
        mask = np.zeros((crop_size, crop_size), dtype=np.float32)
        
        # 2. Определяем центр и размеры эллипса
        center = (crop_size // 2, crop_size // 2)
        axes = (int(crop_size * 0.35), int(crop_size * 0.4))
        
        # 3. Рисуем эллипс (заполняем белым цветом, значение=1.0)
        cv2.ellipse(
            mask,          # Массив для рисования
            center,        # Центр эллипса
            axes,          # Полуоси (ширина, высота)
            angle=0,       # Угол поворота
            startAngle=0,  # Начальный угол дуги
            endAngle=360,  # Конечный угол дуги (360 = полный эллипс)
            color=1.0,     # Значение для заполнения (белый = 1.0)
            thickness=-1   # -1 = заполнить всю область эллипса   
        )
        
        # 4. Применяем размытие для плавных краёв
        blur_ksize = 15  # Нечётное число, чтобы ядро было симметричным
        mask = cv2.GaussianBlur(mask, (blur_ksize, blur_ksize), 0)
        
        # 5. Ограничим значения в диапазоне [0, 1]
        mask = np.clip(mask, 0, 1)
        
        return mask

    def paste_back(self, target_img, swapped_face, M, crop_size=256):
        
        # 1. Создание мягкой маски (Эрозия + Размытие)
        mask = self.create_gradient_mask(crop_size)

        # Преобразуем в трехканальную маску
        mask_3c = np.stack([mask] * 3, axis=2)

        # 2. Получаем размеры целевого изображения
        h, w = target_img.shape[:2]

        # 3. Нормализация swapped_face к float32 [0,1] для warp
        swapped_face_norm = swapped_face.astype(np.float32) / 255.0
        mask_norm = mask_3c.astype(np.float32)  # Маска уже [0,1]

        # 4. Обратное преобразование (WARP_INVERSE_MAP) для лица И маски
        # Используем BORDER_CONSTANT с borderValue=0.5 (серый, чтобы избежать синих/зеленых артефактов)
        warped_face = cv2.warpAffine(
            swapped_face_norm,
            M,
            (w, h),
            flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.5
        )
        
        # Для маски (INTER_CUBIC — плавные границы)
        warped_mask = cv2.warpAffine(
            mask_norm,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.0  # Маска: 0 за пределами
        )
        
        # 5. Обработка после warp: Clip, NaN fix
        warped_face = np.clip(warped_face, 0, 1)  # Убираем отрицательные
        warped_face = np.nan_to_num(warped_face, nan=0.5)  # NaN -> серый
        
        warped_mask = np.clip(warped_mask, 0, 1)
        warped_mask = np.nan_to_num(warped_mask, nan=0.0)
        
        # 6. Дополнительное размытие для устранения артефактов
        warped_mask = cv2.GaussianBlur(warped_mask, (3, 3), 0)

        # 7. Плавное наложение в float32
        target_float = target_img.astype(np.float32) / 255.0
        result_float = target_float * (1.0 - warped_mask) + warped_face * warped_mask
        
        # 8. Обратная нормализация к uint8
        result = (result_float * 255).clip(0, 255).astype(np.uint8)

        return result

    def visualize_points(self, img, points, color=(0, 255, 0)):
        img = img.copy()
        for p in points:
            cv2.circle(img, tuple(p.astype(int)), 3, color, -1)

    # Итоговая функция run_hyperswap (get) с аффинным преобразованием
    def get(self, img, target_face, source_face, paste_back=True):
        # 1. Подготовка эмбеддинга
        source_embedding = source_face.normed_embedding.reshape(1, -1).astype(np.float32)

        # 2. Получаем 5 точек target
        target_landmarks_5 = self.get_landmarks_5(target_face)
        # self.visualize_points(img, target_landmarks_5, (0, 255, 0)) # не для продакшена
        
        if target_landmarks_5 is None:
            return img if paste_back else (None, None)

        # 3. Определение эталонных точек для выравнивания 256x256 (FFHQ Alignment)
        std_landmarks_256 = np.array([
            [ 84.87, 105.94],  # Левый глаз
            [171.13, 105.94],  # Правый глаз
            [128.00, 146.66],  # Кончик носа
            [ 96.95, 188.64],  # Левый уголок рта
            [159.05, 188.64]   # Правый уголок рта
        ], dtype=np.float32)

        # Вычисляем аффинную матрицу
        M = self.get_affine_transform(target_landmarks_5.astype(np.float32), std_landmarks_256)
        
        # Применяем аффинное преобразование с новой матрицей M
        crop = cv2.warpAffine(img, M, (256, 256), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

        # 4. Преобразуем crop для модели
        crop_input = crop[:, :, ::-1].astype(np.float32) / 255.0  # RGB -> [0,1]
        crop_input = (crop_input - 0.5) / 0.5  # Нормализация
        crop_input = crop_input.transpose(2, 0, 1)[np.newaxis, ...].astype(np.float32)

        # 5. Инференс
        try:
            output = self.session.run(None, {'source': source_embedding, 'target': crop_input})[0][0]
        except:
            return img if paste_back else (None, None)

        if isinstance(output, np.ndarray):
            # устранение NaN и бесконечностей
            output = np.nan_to_num(output, nan=0.0, posinf=255.0, neginf=0.0)

            # если диапазон похож на [-1,1] → нормализуем в [0,255]
            if output.min() < 0.0 or output.max() <= 1.5:
                output = ((output + 1.0) / 2.0 * 255.0)
            # жёсткое ограничение диапазона и тип для OpenCV
            output = np.clip(output, 0, 255).astype(np.uint8).copy()

            # защита от повторного использования буфера (inplace CPU bug)
            try:
                output.setflags(write=True)
            except Exception:
                pass
        
        # 6. Обратная нормализация
        output = output.transpose(1, 2, 0)  # CHW -> HWC
        output = output[:, :, ::-1]  # BGR -> RGB
        
        # 7. Возвращаем результат в зависимости от флага paste_back
        if not paste_back:
            return output, M # Возвращаем только кроп лица (256x256) и матрицу M
        
        # Если нужна полная вклейка в исходное изображение:
        return self.paste_back(img, output, M, crop_size=256)
