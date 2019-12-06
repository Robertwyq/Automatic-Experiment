import numpy as np
import cv2
from ctypes import *
import detect as dc

from datetime import datetime
import time

ImgStorageDir = "./DataSet/"
dll = cdll.LoadLibrary("JHCap2.dll")
# initialization
dll.CameraInit(0)
dll.CameraSetResolution(0, 0, 0, 0)
buflen = c_int()
width = c_int()
height = c_int()
count = 0

dll.CameraGetImageSize(0, byref(width), byref(height))
dll.CameraGetImageBufferSize(0, byref(buflen), 0x4)
inbuf = create_string_buffer(buflen.value)


detection = dc.Detect()

while(True):
    dll.CameraSetAWB(0, c_bool(True))
    # get image into buffer
    dll.CameraQueryImage(0, inbuf, byref(buflen), 0x104)
    #using opencv to display the buffer image
    arr= np.frombuffer(inbuf, np.uint8)
    img=np.reshape(arr, (height.value, width.value, 3))
    resize_img = cv2.resize(img,(int(width.value/4),int(height.value/4)),interpolation=cv2.INTER_AREA)
    # get timestamp
    now = datetime.now()
    timeStamp = now.timestamp()
    # save figure to local
    cv2.imwrite(ImgStorageDir + str(count)+".jpg",resize_img)
    count += 1
    if count == 50:
        # 50 images each folder
        break

    # calculate position
    back = detection.detect(resize_img)
    if back != None:
        x, y, w, h, cls = back
        outputlist = [timeStamp,x,y,w,h,detection.mapping[cls]]
        print(outputlist)
    else:
        continue
