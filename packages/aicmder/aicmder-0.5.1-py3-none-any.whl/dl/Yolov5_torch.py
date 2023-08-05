import torch
import os
from models.common import DetectMultiBackend
from models.general import check_img_size, non_max_suppression, scale_coords
import cv2
import time
import numpy as np
from datasets import letterbox
import base64

def select_device(device='', batch_size=0, newline=True):
    # device = 'cpu' or '0' or '0,1,2,3'
    # s = f'YOLOv5 🚀 {git_describe() or date_modified()} torch {torch.__version__} '  # string
    device = str(device).strip().lower().replace(
        'cuda:', '')  # to string, 'cuda:0' to '0'
    cpu = device == 'cpu'
    if cpu:
        # force torch.cuda.is_available() = False
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    elif device:  # non-cpu device requested
        os.environ['CUDA_VISIBLE_DEVICES'] = device  # set environment variable
        assert torch.cuda.is_available(
        ), f'CUDA unavailable, invalid device {device} requested'  # check availability

    cuda = not cpu and torch.cuda.is_available()
    if cuda:
        # range(torch.cuda.device_count())  # i.e. 0,1,6,7
        devices = device.split(',') if device else '0'
        n = len(devices)  # device count
        if n > 1 and batch_size > 0:  # check batch_size is divisible by device_count
            assert batch_size % n == 0, f'batch-size {batch_size} not multiple of GPU count {n}'
        # space = ' ' * (len(s) + 1)
        for i, d in enumerate(devices):
            p = torch.cuda.get_device_properties(i)
            # s += f"{'' if i == 0 else space}CUDA:{d} ({p.name}, {p.total_memory / 1024 ** 2:.0f}MiB)\n"  # bytes to MB
    # else:
        # s += 'CPU\n'

    # if not newline:
    #     s = s.rstrip()
    return torch.device('cuda:0' if cuda else 'cpu')


def plot_one_box(x, im, color=(128, 128, 128), label=None, line_thickness=1):
    # Plots one bounding box on image 'im' using OpenCV
    assert im.data.contiguous, 'Image not contiguous. Apply np.ascontiguousarray(im) to plot_on_box() input image.'
    tl = line_thickness or round(0.002 * (im.shape[0] + im.shape[1]) / 2) + 1  # line/font thickness
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(im, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(im, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(im, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

        # cv2.rectangle(im, (550, 265), (555, 270), color, -1, cv2.LINE_AA)  # filled

def cv2_to_base64(image):
    return base64.b64encode(image).decode('utf8')

class Yolov5:

    def __init__(self, weights, imgsz, classes=None, conf_thres=0.55, iou_thres=0.45) -> None:
        self.imgsz = imgsz
        self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, self.max_det = conf_thres, iou_thres, classes, False, 1000
        self.device = select_device()
        self.weights = weights
        self.model = DetectMultiBackend(
            self.weights, device=self.device, dnn=False)
        self.stride, self.names, pt, jit, onnx, engine = self.model.stride, self.model.names, self.model.pt, self.model.jit, self.model.onnx, self.model.engine
        # print(self.stride, self.names, pt, jit, onnx, engine)
        self.hide_labels, self.hide_conf = False, False
        self.imgsz = check_img_size(
            self.imgsz, s=self.stride)  # check image size
        print(self.imgsz, np.array(self.names)[self.classes])
        # not using half precision
        self.half = False
        self.model.model.float()

        self.model.warmup(imgsz=(1, 3, *self.imgsz), half=self.half)  # warmup

    def predict_image(self, img_bgr, debug=0):
        img = letterbox(img_bgr, self.imgsz, stride=self.stride)[0]
        # print(img.shape, img_bgr.shape)
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img).astype(np.float32)

        im = torch.from_numpy(img).to(self.device)
        im = im.half() if self.half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        pred = self.model(im, augment=False, visualize=False)
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres,
                                   self.classes, self.agnostic_nms, max_det=self.max_det)
        resp_list = []
        h, w, _ = img_bgr.shape
        # print("shape", w, h, img_bgr.shape)
        for i, det in enumerate(pred):  # per image
            if len(det) > 0:
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], img_bgr.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    if len(xyxy) >= 4:
                        c = int(cls)  # integer class
                        label = None if self.hide_labels else (self.names[c] if self.hide_conf else f'{self.names[c]} {conf:.2f}')
                        # print(xyxy, conf, c, label)
                        start_x, start_y, end_x, end_y = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                        resp_list.append({
                            "start_x": start_x,
                            "start_y": start_y,
                            "end_x": end_x,
                            "end_y": end_y,
                            "x0": float(start_x) / w,
                            "x1": float(end_x) / w,
                            "y0": float(start_y) / h,
                            "y1": float(end_y) / h,
                            "c" : c,
                            "label": label,
                            "conf": float(conf)
                        })

                        if debug > 0:
                            plot_one_box(xyxy, img_bgr, label=label)

            
        if len(resp_list) > 0:
            resp_list = sorted(resp_list, key=lambda x: x["conf"], reverse=True)
            # print(resp_list)
        
        resp_d = {}
        resp_d["data"] = resp_list
        if debug > 0:
            cv2.imwrite('detect_torch.png', img_bgr)
            if debug > 1:
                with open('detect_torch.png',  'rb') as img_f:
                    img = img_f.read()
                    resp_d["img"] = cv2_to_base64(img)
        return resp_d


def coin():
    imgsz = [1280, 1280]
    weights = '/home/faith/android_viewer/thirdparty/yolov5/runs/train/exp26/weights/best.pt'
    yolo = Yolov5(weights=weights, imgsz=imgsz)
    image_file = "/home/faith/750.png"
    img = cv2.imread(image_file, cv2.COLOR_RGB2BGR)
    start = time.time()
    yolo.predict_image(img, save_img=True)
    end = time.time()
    print(end - start)


def people():
    # imgsz = [1280, 1280]
    # weights = '/home/faith/yolov5m6.pt'
    # yolo = Yolov5(weights=weights, imgsz=imgsz)

    imgsz = [640, 640]
    weights = '/home/faith/yolov5m.pt'
    # weights = '/home/faith/yolov5m6.pt'
    # weights = '/home/faith/yolov5l.pt'
    yolo = Yolov5(weights=weights, imgsz=imgsz, conf_thres=0.2, iou_thres=0.4)
    image_file = "/home/faith/aicmder/dl/detect_torch.png"
    img = cv2.imread(image_file, cv2.COLOR_RGB2BGR)
    start = time.time()
    resp_d = yolo.predict_image(img, debug=1)
    # if len(resp_d["data"]) > 0:
    print(resp_d)
    end = time.time()
    print(end - start)

if __name__ == "__main__":
    people()