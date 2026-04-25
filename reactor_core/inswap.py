import cv2
import numpy as np
from .face_objects import BaseONNXModel
from .meanshape_68 import MEANSHAPE_68

# --- Математика для 3D позы ---

def estimate_affine_matrix_3d23d(X, Y):
    ''' Вычисляет аффинную матрицу трансформации 3D -> 3D '''
    X_homo = np.hstack((X, np.ones([X.shape[0], 1])))
    P = np.linalg.lstsq(X_homo, Y, rcond=None)[0].T
    return P

def P2sRt(P):
    ''' Разбивает матрицу проекции '''
    t1 = np.linalg.norm(P[:,0])
    t2 = np.linalg.norm(P[:,1])
    t3 = np.linalg.norm(P[:,2])
    s = (t1 + t2 + t3) / 3.0
    P1 = P / s
    R = P1[:, 0:3]
    t = P1[:, 3]
    return s, R, t

def matrix2angle(R):
    ''' Превращает матрицу поворота в углы Эйлера (pitch, yaw, roll) '''
    if R[2,0] != 1 and R[2,0] != -1:
        pitch = -np.arcsin(R[2,0])
        yaw = np.arctan2(R[2,1]/np.cos(pitch), R[2,2]/np.cos(pitch))
        roll = np.arctan2(R[1,0]/np.cos(pitch), R[0,0]/np.cos(pitch))
    else:
        yaw = 0
        if R[2,0] == -1:
            pitch = np.pi/2
            roll = yaw + np.arctan2(R[0,1], R[0,2])
        else:
            pitch = -np.pi/2
            roll = -yaw + np.arctan2(-R[0,1], -R[0,2])
    return pitch, yaw, roll

# --- Вспомогательные функции ---

def distance2bbox(points, distance, max_shape=None):
    x1 = points[:, 0] - distance[:, 0]
    y1 = points[:, 1] - distance[:, 1]
    x2 = points[:, 0] + distance[:, 2]
    y2 = points[:, 1] + distance[:, 3]
    if max_shape is not None:
        x1 = np.clip(x1, 0, max_shape[1])
        y1 = np.clip(y1, 0, max_shape[0])
        x2 = np.clip(x2, 0, max_shape[1])
        y2 = np.clip(y2, 0, max_shape[0])
    return np.stack([x1, y1, x2, y2], axis=-1)

def distance2kps(points, distance, max_shape=None):
    preds = []
    for i in range(0, distance.shape[1], 2):
        px = points[:, i%2] + distance[:, i]
        py = points[:, i%2+1] + distance[:, i+1]
        if max_shape is not None:
            px = np.clip(px, 0, max_shape[1])
            py = np.clip(py, 0, max_shape[0])
        preds.append(px)
        preds.append(py)
    return np.stack(preds, axis=-1)

# Стандартные точки FFHQ/ArcFace для матрицы трансформации 112x112
ARCFACE_STD_POINTS = np.array([
    [38.2946, 51.6963],
    [73.5318, 51.5014],
    [56.0252, 71.7366],
    [41.5493, 92.3655],
    [70.7299, 92.2041]
], dtype=np.float32)

def norm_crop(img, landmark, image_size=112):
    """Выравнивает и обрезает лицо (для ArcFace)"""
    M, _ = cv2.estimateAffinePartial2D(landmark, ARCFACE_STD_POINTS)
    warped = cv2.warpAffine(img, M, (image_size, image_size), borderValue=0.0)
    return warped

# --- Модели ---

class SCRFD(BaseONNXModel):
    """Детектор лиц (находит bbox и 5 ключевых точек)"""
    def __init__(self, model_file, providers=None):
        super().__init__(model_file, providers)
        self.batched = len(self.outputs[0].shape) == 3
        self.input_mean = 127.5
        self.input_std = 128.0
        self.use_kps = len(self.outputs) in [9, 15]
        self.fmc = 5 if len(self.outputs) in [10, 15] else 3
        self._feat_stride_fpn = [8, 16, 32, 64, 128][:self.fmc]
        self._num_anchors = 2 if self.fmc == 3 else 1
        self.center_cache = {}

    def forward(self, img, threshold):
        scores_list, bboxes_list, kpss_list = [], [], []
        input_size = tuple(img.shape[0:2][::-1])
        blob = cv2.dnn.blobFromImage(img, 1.0/self.input_std, input_size, 
                                     (self.input_mean, self.input_mean, self.input_mean), swapRB=True)
        
        net_outs = self.session.run(self.output_names, {self.input_names[0]: blob})
        input_height, input_width = blob.shape[2], blob.shape[3]

        for idx, stride in enumerate(self._feat_stride_fpn):
            if self.batched:
                scores = net_outs[idx][0]
                bbox_preds = net_outs[idx + self.fmc][0] * stride
                if self.use_kps:
                    kps_preds = net_outs[idx + self.fmc * 2][0] * stride
            else:
                scores = net_outs[idx]
                bbox_preds = net_outs[idx + self.fmc] * stride
                if self.use_kps:
                    kps_preds = net_outs[idx + self.fmc * 2] * stride

            height, width = input_height // stride, input_width // stride
            key = (height, width, stride)
            
            if key in self.center_cache:
                anchor_centers = self.center_cache[key]
            else:
                anchor_centers = np.stack(np.mgrid[:height, :width][::-1], axis=-1).astype(np.float32)
                anchor_centers = (anchor_centers * stride).reshape((-1, 2))
                if self._num_anchors > 1:
                    anchor_centers = np.stack([anchor_centers] * self._num_anchors, axis=1).reshape((-1, 2))
                if len(self.center_cache) < 100:
                    self.center_cache[key] = anchor_centers

            pos_inds = np.where(scores >= threshold)[0]
            bboxes = distance2bbox(anchor_centers, bbox_preds)
            
            scores_list.append(scores[pos_inds])
            bboxes_list.append(bboxes[pos_inds])
            
            if self.use_kps:
                kpss = distance2kps(anchor_centers, kps_preds)
                kpss = kpss.reshape((kpss.shape[0], -1, 2))
                kpss_list.append(kpss[pos_inds])

        return scores_list, bboxes_list, kpss_list

    def detect(self, img, det_thresh=0.5, input_size=(640, 640), max_num=0):
        im_ratio = float(img.shape[0]) / img.shape[1]
        model_ratio = float(input_size[1]) / input_size[0]
        
        if im_ratio > model_ratio:
            new_height = input_size[1]
            new_width = int(new_height / im_ratio)
        else:
            new_width = input_size[0]
            new_height = int(new_width * im_ratio)
            
        det_scale = float(new_height) / img.shape[0]
        resized_img = cv2.resize(img, (new_width, new_height))
        det_img = np.zeros((input_size[1], input_size[0], 3), dtype=np.uint8)
        det_img[:new_height, :new_width, :] = resized_img

        scores_list, bboxes_list, kpss_list = self.forward(det_img, det_thresh)

        scores = np.vstack(scores_list).ravel()
        order = scores.argsort()[::-1]
        bboxes = np.vstack(bboxes_list) / det_scale
        
        if self.use_kps:
            kpss = np.vstack(kpss_list) / det_scale

        pre_det = np.hstack((bboxes, scores[:, None])).astype(np.float32, copy=False)
        pre_det = pre_det[order, :]
        keep = self.nms(pre_det)
        
        det = pre_det[keep, :]
        kpss = kpss[order, :, :][keep, :, :] if self.use_kps else None

        if max_num > 0 and det.shape[0] > max_num:
            area = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
            img_center = img.shape[0] // 2, img.shape[1] // 2
            offsets = np.vstack([
                (det[:, 0] + det[:, 2]) / 2 - img_center[1],
                (det[:, 1] + det[:, 3]) / 2 - img_center[0]
            ])
            offset_dist_squared = np.sum(np.power(offsets, 2.0), 0)
            values = area - offset_dist_squared * 2.0
            bindex = np.argsort(values)[::-1][:max_num]
            det = det[bindex, :]
            if kpss is not None:
                kpss = kpss[bindex, :]
                
        return det, kpss

    def nms(self, dets, nms_thresh=0.4):
        x1, y1, x2, y2, scores = dets[:, 0], dets[:, 1], dets[:, 2], dets[:, 3], dets[:, 4]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= nms_thresh)[0]
            order = order[inds + 1]
        return keep


class ArcFaceONNX(BaseONNXModel):
    """Распознаватель лиц (выдает вектор/эмбеддинг)"""
    def __init__(self, model_file, providers=None):
        super().__init__(model_file, providers)
        self.input_mean = 127.5
        self.input_std = 127.5
        self.input_size = tuple(self.input_shape[2:4][::-1])

    def get(self, img, face):
        aimg = norm_crop(img, landmark=face.kps, image_size=self.input_size[0])
        blob = cv2.dnn.blobFromImage(aimg, 1.0 / self.input_std, self.input_size,
                                      (self.input_mean, self.input_mean, self.input_mean), swapRB=True)
        net_out = self.session.run(self.output_names, {self.input_names[0]: blob})[0]
        face.embedding = net_out.flatten()
        return face.embedding


class Attribute(BaseONNXModel):
    """Анализатор атрибутов (выдает пол и возраст)"""
    def __init__(self, model_file, providers=None):
        super().__init__(model_file, providers)
        self.input_mean = 127.5
        self.input_std = 128.0
        self.input_size = tuple(self.input_shape[2:4][::-1])

    def get(self, img, face):
        bbox = face.bbox
        w, h = (bbox[2] - bbox[0]), (bbox[3] - bbox[1])
        center = ((bbox[2] + bbox[0]) / 2, (bbox[3] + bbox[1]) / 2)
        _scale = self.input_size[0] / (max(w, h) * 1.5)
        
        # Простая трансформация для Attribute (не требует 5 точек, только центр и масштаб)
        M = np.array([
            [_scale, 0, self.input_size[0] * 0.5 - center[0] * _scale],
            [0, _scale, self.input_size[1] * 0.5 - center[1] * _scale]
        ], dtype=np.float32)
        
        aimg = cv2.warpAffine(img, M, self.input_size, borderValue=0.0)
        blob = cv2.dnn.blobFromImage(aimg, 1.0 / self.input_std, self.input_size, 
                                     (self.input_mean, self.input_mean, self.input_mean), swapRB=True)
        
        pred = self.session.run(self.output_names, {self.input_names[0]: blob})[0][0]
        
        # Получаем гендер и возраст
        gender = int(np.argmax(pred[:2]))
        age = int(np.round(pred[2] * 100))
        face.gender = gender
        face.age = age
        return gender, age

class INSwapper(BaseONNXModel):
    """Свопер лиц (модели inswapper_128, reswapper)"""
    def __init__(self, model_file, providers=None):
        super().__init__(model_file, providers)
        self.input_mean = 0.0
        self.input_std = 255.0
        self.input_size = tuple(self.input_shape[2:4][::-1])

        # Хак для экономии памяти: импортируем onnx только здесь,
        # читаем нужную матрицу emap и сразу выгружаем тяжелую модель из RAM.
        import onnx
        from onnx import numpy_helper
        model = onnx.load(self.model_file, load_external_data=False)
        self.emap = numpy_helper.to_array(model.graph.initializer[-1])
        del model 

    def get(self, img, target_face, source_face, paste_back=True):
        # 1. Идеальное позиционирование (1 в 1 как в оригинальном C++ Insightface)
        # ВАЖНО: Insightface центрирует лицо для INSwapper ТОЛЬКО по оси X! 
        # По оси Y оно остается прижатым выше, сохраняя оригинальные пропорции.
        ratio = float(self.input_size[0]) / 128.0
        diff_x = 8.0 * ratio
        
        src_pts = ARCFACE_STD_POINTS.copy() * ratio
        src_pts[:, 0] += diff_x  # Смещаем ТОЛЬКО координаты X!

        # 2. Вычисляем аффинную матрицу родным методом OpenCV
        M, _ = cv2.estimateAffinePartial2D(target_face.kps, src_pts)
        
        # 3. Кропаем и выравниваем лицо
        aimg = cv2.warpAffine(img, M, self.input_size, borderValue=0.0)
        blob = cv2.dnn.blobFromImage(aimg, 1.0 / self.input_std, self.input_size,
                                      (self.input_mean, self.input_mean, self.input_mean), swapRB=True)

        # 4. Подготавливаем эмбеддинг донора
        latent = source_face.normed_embedding.reshape((1, -1))
        latent = np.dot(latent, self.emap)
        latent /= np.linalg.norm(latent)

        # 5. Инференс
        pred = self.session.run(self.output_names, {
            self.input_names[0]: blob, 
            self.input_names[1]: latent.astype(np.float32)
        })[0]

        img_fake = pred.transpose((0, 2, 3, 1))[0]
        bgr_fake = np.clip(255 * img_fake, 0, 255).astype(np.uint8)[:, :, ::-1]

        if not paste_back:
            return bgr_fake, M

        # 6. Обратная вклейка (Paste Back)
        target_img = img
        fake_diff = bgr_fake.astype(np.float32) - aimg.astype(np.float32)
        fake_diff = np.abs(fake_diff).mean(axis=2)
        
        # Обрезаем края
        fake_diff[:2, :] = 0
        fake_diff[-2:, :] = 0
        fake_diff[:, :2] = 0
        fake_diff[:, -2:] = 0

        IM = cv2.invertAffineTransform(M)
        img_white = np.full((aimg.shape[0], aimg.shape[1]), 255, dtype=np.float32)

        # Возвращаем в исходную перспективу
        bgr_fake_warped = cv2.warpAffine(bgr_fake, IM, (target_img.shape[1], target_img.shape[0]), borderValue=0.0)
        img_white_warped = cv2.warpAffine(img_white, IM, (target_img.shape[1], target_img.shape[0]), borderValue=0.0)
        fake_diff_warped = cv2.warpAffine(fake_diff, IM, (target_img.shape[1], target_img.shape[0]), borderValue=0.0)

        img_white_warped[img_white_warped > 20] = 255
        fthresh = 10
        fake_diff_warped[fake_diff_warped < fthresh] = 0
        fake_diff_warped[fake_diff_warped >= fthresh] = 255

        img_mask = img_white_warped
        mask_h_inds, mask_w_inds = np.where(img_mask == 255)

        # Защита от пустой маски
        if len(mask_h_inds) > 0 and len(mask_w_inds) > 0:
            mask_h = np.max(mask_h_inds) - np.min(mask_h_inds)
            mask_w = np.max(mask_w_inds) - np.min(mask_w_inds)
            mask_size = int(np.sqrt(mask_h * mask_w))

            k = max(mask_size // 10, 10)
            kernel = np.ones((k, k), np.uint8)
            img_mask = cv2.erode(img_mask, kernel, iterations=1)

            kernel = np.ones((2, 2), np.uint8)
            fake_diff_warped = cv2.dilate(fake_diff_warped, kernel, iterations=1)

            k = max(mask_size // 20, 5)
            blur_size = (k * 2 + 1, k * 2 + 1)
            img_mask = cv2.GaussianBlur(img_mask, blur_size, 0)

            k = 5
            blur_size = (k * 2 + 1, k * 2 + 1)
            fake_diff_warped = cv2.GaussianBlur(fake_diff_warped, blur_size, 0)

        img_mask /= 255.0
        img_mask = np.reshape(img_mask, [img_mask.shape[0], img_mask.shape[1], 1])

        fake_merged = img_mask * bgr_fake_warped + (1.0 - img_mask) * target_img.astype(np.float32)
        return fake_merged.astype(np.uint8)

class Landmark(BaseONNXModel):
    """Извлекает 106 (2D) или 68 (3D) точек лица"""
    def __init__(self, model_file, providers=None):
        super().__init__(model_file, providers)
        self.input_mean = 127.5
        self.input_std = 128.0
        self.input_size = tuple(self.input_shape[2:4][::-1])
        
        output_shape = self.outputs[0].shape
        # Определяем, какая это модель (3D или 2D) по размеру выхода
        if output_shape[1] == 3309:
            self.lmk_dim = 3
            self.lmk_num = 68
            self.taskname = 'landmark_3d_68'
        else:
            self.lmk_dim = 2
            self.lmk_num = output_shape[1] // self.lmk_dim
            self.taskname = f'landmark_2d_{self.lmk_num}'

    def get(self, img, face):
        bbox = face.bbox
        w, h = (bbox[2] - bbox[0]), (bbox[3] - bbox[1])
        center = ((bbox[2] + bbox[0]) / 2, (bbox[3] + bbox[1]) / 2)
        _scale = self.input_size[0] / (max(w, h) * 1.5)
        
        # Матрица трансформации (выравнивание по центру bbox)
        M = np.array([
            [_scale, 0, self.input_size[0] * 0.5 - center[0] * _scale],
            [0, _scale, self.input_size[1] * 0.5 - center[1] * _scale]
        ], dtype=np.float32)
        
        aimg = cv2.warpAffine(img, M, self.input_size, borderValue=0.0)
        blob = cv2.dnn.blobFromImage(aimg, 1.0 / self.input_std, self.input_size, 
                                     (self.input_mean, self.input_mean, self.input_mean), swapRB=True)
        
        pred = self.session.run(self.output_names, {self.input_names[0]: blob})[0][0]
        
        if pred.shape[0] >= 3000:
            pred = pred.reshape((-1, 3))
        else:
            pred = pred.reshape((-1, 2))
            
        if self.lmk_num < pred.shape[0]:
            pred = pred[-self.lmk_num:, :]
            
        # Денормализация точек в размер модели
        pred[:, 0:2] += 1
        pred[:, 0:2] *= (self.input_size[0] // 2)
        if pred.shape[1] == 3:
            pred[:, 2] *= (self.input_size[0] // 2)

        # Обратная трансформация точек на оригинальное изображение
        IM = cv2.invertAffineTransform(M)
        pred_xy = pred[:, 0:2]
        pred_xy = np.hstack((pred_xy, np.ones((pred_xy.shape[0], 1)))) # Добавляем гомогенную координату
        pred_xy = np.dot(IM, pred_xy.T).T
        
        if pred.shape[1] == 3:
            pred = np.hstack((pred_xy, pred[:, 2:3])) # Возвращаем Z
        else:
            pred = pred_xy

        # Сохраняем в объект Face под правильным именем
        setattr(face, self.taskname, pred)
        
        # Честный расчет 3D позы
        if self.taskname == 'landmark_3d_68':
            P = estimate_affine_matrix_3d23d(MEANSHAPE_68, pred)
            _, R, _ = P2sRt(P)
            rx, ry, rz = matrix2angle(R)
            face.pose = np.array([rx, ry, rz], dtype=np.float32)
            
        return pred
