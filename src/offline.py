import socket
import numpy as np
import cv2
from ctypes import *
import detect as dc
import copy
from datetime import datetime
import Rectify as rf
import matplotlib.pyplot as plt

# cv2.namedWindow("show", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("show", (500,500))

if __name__ == "__main__":
    # Camera Interface Init
    dll = cdll.LoadLibrary("JHCap2.dll")
    dll.CameraInit(0)
    dll.CameraSetResolution(0, 0, 0, 0)
    buflen = c_int()
    width = c_int()
    height = c_int()
    awb = c_bool(True)
    dll.CameraGetImageSize(0, byref(width), byref(height))
    dll.CameraGetImageBufferSize(0, byref(buflen), 0x4)
    inbuf = create_string_buffer(buflen.value)
    # dll.CameraSetAWB(0,awb)
    # param
    left_x=0
    right_x=260
    up_y=144
    bottom_y=333

    detection = dc.Detect()

    while True:
        # get image into buffer
        # dll.CameraSetAWB(0, c_bool(True))
        dll.CameraQueryImage(0, inbuf, byref(buflen), 0x104)
        arr = np.frombuffer(inbuf, np.uint8)
        print("array shape = ",arr.shape)
        img = np.reshape(arr, (height.value, width.value, 3))
        reshapeWidth = int(width.value / 4)
        reshapeHeight = int(height.value / 4)
        # using opencv to display the buffer image
        resize_img = cv2.resize(img, (reshapeWidth, reshapeHeight), interpolation=cv2.INTER_AREA)

        # resize_img[:, :, ] = resize_img[:, :, [2,1,0]]
        
        # cv2.imwrite("./test2.png", resize_img)
        # get timestamp
        now = datetime.now()
        timeStamp = now.timestamp()
        back = detection.detect(resize_img)
       
        
        # cv2.waitKey(0)
        if back != None:
            x, y, w, h, cls = back
            outputlist = [timeStamp, x, y, w, h, detection.mapping[cls]]
            Rec = rf.Rectify(outputlist)
            parameters=left_x, right_x, up_y, bottom_y
            loc = Rec.Get_real_loc(parameters,reshapeWidth,reshapeHeight)
            print(420 - loc[1],300-loc[0])
            print("Block Real Location: ",loc)
            # outputstr = " ".join(list(map(lambda x: str(x), outputlist)))
        else:
            print("no block found!\n")
            continue