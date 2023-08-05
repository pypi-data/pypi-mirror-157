import cv2
import numpy as np
import shapely.geometry
import shapely.affinity
from collections import defaultdict


class RotatedRect:
    def __init__(self, cx, cy, w, h, angle):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.angle = angle

    #  (center(x, y), (width, height), angle of rotation)
    def __init__(self, minAreaRect):
        self.cx = minAreaRect[0][0]
        self.cy = minAreaRect[0][1]
        self.w = minAreaRect[1][0]
        self.h = minAreaRect[1][1]
        self.angle = minAreaRect[2]

    def get_contour(self):
        w = self.w
        h = self.h
        c = shapely.geometry.box(-w/2.0, -h/2.0, w/2.0, h/2.0)
        rc = shapely.affinity.rotate(c, self.angle)
        return shapely.affinity.translate(rc, self.cx, self.cy)

    def intersection(self, other):
        return self.get_contour().intersection(other.get_contour())

    def union(self, other):
        return self.get_contour().union(other.get_contour())

    def iou(self, other):
        return self.intersection(other).area / self.union(other).area


class Fence:

    def __init__(self, points, w=1, h=1) -> None:
        self.contours = []
        for x, y in points:
            self.contours.append([int(w * x), int(h * y)])
        self.contours = [np.array(self.contours, dtype=np.int32)]
        self.min_rect = cv2.minAreaRect(self.contours[0])
        self.box = cv2.boxPoints(self.min_rect)
        self.fence_rect = RotatedRect(self.min_rect)

    def iou(self, other):
        return self.fence_rect.iou(other.fence_rect)

    def area(self):
        return self.fence_rect.get_contour().area

    def pointPolygonTest(self, point=(490, 125)):
        return cv2.pointPolygonTest(self.box, point, False)

    def center(self):
        return (self.fence_rect.cx, self.fence_rect.cy)


def check_object_in_fence(resp_d, fence_list, calculate_usage=False):

    new_d = []
    if calculate_usage:
        resp_d["fence_usage"] = defaultdict(int)
    for i, obj in enumerate(resp_d["data"]):
        start_x, end_x, end_y, start_y = obj["start_x"], obj["end_x"], obj["end_y"], obj["start_y"]
        width = end_x - start_x
        height = end_y - start_y
        center_x = start_x + width / 2
        center_y = start_y + height / 2
        for i, fence in enumerate(fence_list):
            if fence.pointPolygonTest((center_x, center_y)) == 1:
                obj["fence"] = i
                new_d.append(obj)
                if calculate_usage:
                    resp_d["fence_usage"][i] += width * height
                break
    resp_d["data"] = new_d
    if calculate_usage:
        for fence_idx in resp_d["fence_usage"]:
            resp_d["fence_usage"][fence_idx] = resp_d["fence_usage"][fence_idx] / \
                fence_list[fence_idx].area()
    # print(new_d, len(new_d))
    # print("---")
    # print(resp_d["data"], len(resp_d["data"]))


if __name__ == "__main__":
    h, w = 720, 1280
    points = [[0.4071, 0.4052], [0.3932, 0.4385], [0.5015, 0.5224],
              [0.5129, 0.4834], [0.5186, 0.4645], [0.4128, 0.3879]]
    fence = Fence(points, w, h)

    object = [[0.1, 0.1], [0.5, 0.1], [0.5, 0.5], [0.1, 0.5]]
    o = Fence(object, w, h)

    print(fence.iou(o), fence.area())
    print(fence.pointPolygonTest((w * 0.41, h * 0.41)) == 1)
    print(fence.pointPolygonTest(o.center()))
