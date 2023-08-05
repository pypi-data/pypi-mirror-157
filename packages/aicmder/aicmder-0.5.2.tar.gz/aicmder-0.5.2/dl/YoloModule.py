
import aicmder as cmder
from aicmder.module.module import serving, moduleinfo
import io
from PIL import Image
import json

import base64
import cv2
import numpy as np
from Yolov5_torch import Yolov5
from baili import shoot
from fence_detect import Fence, check_object_in_fence

def readb64(base64_string, save=False):
    # sbuf = StringIO()
    # sbuf.write(base64.b64decode(base64_string))
    # pimg = Image.open(sbuf)
    img_array = io.BytesIO(base64.b64decode(base64_string))
    pimg = Image.open(img_array)  # RGB
    if save:
        pimg.save('image.png', 'PNG')
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)  # BGR


@moduleinfo(name='image')
class ImagePredictor(cmder.Module):

    # https://stackoverflow.com/questions/9575409/calling-parent-class-init-with-multiple-inheritance-whats-the-right-way
    def __init__(self, **kwargs) -> None:
        # print('init', file_path)
        # Yolov5.__init__(self)
        print("init ImagePredictor", kwargs["Coin"])
        coin = kwargs["Coin"]
        imgsz = coin["imgsz"]
        weights = coin["model"]
        self.coin_yolo = Yolov5(weights=weights, imgsz=imgsz)

        if "baili" in kwargs:
            baili = kwargs["baili"]
            imgsz = baili["imgsz"]
            weights = baili["model"]
            self.baili_yolo = Yolov5(weights=weights, imgsz=imgsz)
            self.debug = 0

    # json base64
    @serving
    def predict(self, **kwargs):
        # print('receive', kwargs)
        resp_d = {}
        resp_d["data"] = []
        self.debug = 0
        try:
            img_base64 = kwargs["img"]
            # print('receive', img_base64[:100])
            img_bgr = readb64(img_base64)

            model_name = kwargs["model"]
            if "debug" in kwargs and kwargs["debug"] > 0:
                try:
                    self.debug = int(kwargs["debug"])
                except:
                    pass
                
            # print(self.debug)
            if "Coin" in model_name:
                resp_d = self.coin_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)
            elif "baili" in model_name:
                resp_d = self.baili_yolo.predict_image(img_bgr=img_bgr,  debug=self.debug)
                if "base_x" in kwargs and "base_y" in kwargs and len(resp_d["data"]) > 0:
                    base_center_x = kwargs["base_x"]
                    base_center_y = kwargs["base_y"]
                    shoot(resp_d, base_center_x, base_center_y)

            if "debug" in kwargs and kwargs["debug"] == 1:
                del resp_d["img"]

            if "fence" in kwargs:
                fences = kwargs["fence"]
                h, w, _ = img_bgr.shape
                fence_list = []
                for f in fences:
                    fence = Fence(f, w, h)
                    fence_list.append(fence)
                calculate_usage = False
                if "Cake" in model_name:
                    calculate_usage = True
                check_object_in_fence(resp_d, fence_list, calculate_usage=calculate_usage)

        except Exception as e:
            print(e)

        # for debug
        # resp_d = {"data": [{"start_x": 399, "start_y": 99, "end_x": 467, "end_y": 113, "x0": 0.5541666666666667, "x1": 0.6486111111111111, "y0": 0.2877906976744186, "y1": 0.32848837209302323, "c": 0, "label": "enermy 0.94", "conf": 0.9433093070983887}, {"start_x": 451, "start_y": 88, "end_x": 515, "end_y": 100, "x0": 0.6263888888888889, "x1": 0.7152777777777778, "y0": 0.2558139534883721, "y1": 0.29069767441860467, "c": 0, "label": "enermy 0.75", "conf": 0.7499269247055054}]}

        json_ret = json.dumps(resp_d)
        # print(json_ret)
        return json_ret


# curl -s 127.0.0.1:8099/predict -X POST -d '{"img_base64": "asdasdasddsa"}'
if __name__ == "__main__":
    import aicmder as cmder
    config = {'image': {'name': 'YoloModule', 'init_args':
                        {
                            'Coin': {
                                # /home/faith/dl_project/coin/27.pt
                                # "model": '/home/faith/android_viewer/thirdparty/yolov5/runs/train/exp27/weights/best.pt',
                                "model": '/home/faith/android_viewer/thirdparty/yolov5/runs/train/exp28/weights/best.pt',
                                "imgsz": [1280, 1280]
                            },
                            'baili': {
                                "model": '/home/faith/AI_baili_train/best5000.pt',
                                "imgsz": [768, 768]
                            }
                        }}}
    serve = cmder.serve.ServeCommand()
    serve.execute(['-w', '1', '-c', json.dumps(config),
                   '-p', '8199', '--max_connect', '1'])
