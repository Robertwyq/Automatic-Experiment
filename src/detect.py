import numpy as np
import cv2
import sys
from datetime import datetime
import time
import matplotlib.pyplot as plt

class Detect:
    def __init__(self):
        self.Lower = np.array([
            [1, 150, 46],  # red lower bound
            [18, 100, 100],  # yellow lower bound
            [110, 80, 20],  # blue lower bound
            [50, 50, 30],  # green lower bound
        ])
        self.classes = 4
        self.Upper = np.array([
            [8, 255, 255],  # red upper bound
            [32, 200, 255],  # yellow upper bound
            [120, 255, 255],  # blue upper bound
            [70, 255, 150],  # green upper bound
        ])
        self.mapping = {1: 'red', 2: 'yellow', 3: 'blue', 4: 'green'}

    def find_bbox(self, image, lower, upper):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # import ipdb; ipdb.set_trace()
        # plt.imshow(hsv_image)
        # plt.show()
        mask = cv2.inRange(hsv_image, lower, upper)
        ret, binary = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
        kernel = np.ones((15, 15), np.uint8)
        dilation = cv2.dilate(binary, kernel, iterations=1)
        # cv2.imshow("dil",dilation)
        _,contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            boxes = [cv2.boundingRect(contour) for contour in contours]
            return np.array(boxes)
        else:
            return None


    def detect(self, image):
        height, width = image.shape[:2]
        thresh_x = width//2

        result = np.empty(shape=[0, 5])
        
        for i in range(self.classes ):
            lower = self.Lower[i]
            upper = self.Upper[i]

            bbox = self.find_bbox(image, lower, upper)
            if bbox is not None:
                for j in range(bbox.shape[0]):
                    temp = np.append(bbox[j], [i+1])
                    result = np.append(result, [temp], axis=0)

        if result.shape[0] != 0:
            
            index = np.where(result[:, 2] == result[:, 2].max())[0][0]
            result_bbox = result[index]
            x, y, w, h, cls = result_bbox[:5]
            cv2.rectangle(image, (np.int(x), np.int(y)), (np.int(x + w), np.int(y + h)), (153, 153, 0), 2)
            cx = x + w // 2
            cy = y + h // 2
            # cv2.imshow("test", image)
            # print("cls: ", self.mapping[cls])
            # cv2.waitKey(0)
            if cx > thresh_x:
                return [cx, cy, w, h, cls, True]  # return center coordinate & weight, height & class
            else:
                return [cx, cy, w, h, cls, False]
            # return [cx,cy,w,h,cls]
        else:
            return None


if __name__ == '__main__':
    # image_name = sys.argv[1]
    image_name = "test2.png"
    image = cv2.imread(image_name)
    detection = Detect()
    # timeStamp = datetime.now().timestamp()

    back = detection.detect(image)
    if back != None:
        x, y, w, h, cls = back
        # outputlist = [timeStamp, x, y, w, h, detection.mapping[cls]]
        # outputstr = " ".join(list(map(lambda x: str(x), outputlist)))
        print(x, y)


    else:
        print("no block found!\n")











