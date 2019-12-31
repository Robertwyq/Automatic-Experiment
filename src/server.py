import socket
import threading
import numpy as np
import cv2
from ctypes import *
import detect as dc
import copy
from datetime import datetime
import Rectify as rf
import time
outputstr = "" # string storing result from IMGthread
ifpass = False
def TCPLink(sock, addr):
    global outputstr
    print("connection established with ", addr)
    while True:
        # data = "1".encode()
        # if data == "exit".encode():
        #     sock.send("GoodBye!\n".encode())
        #     break
        # # if data ==
        if outputstr == "":
            print("skip")
            continue
        else:
            print("in TCP thread: ", outputstr, "if pass = ", ifpass)
            if ifpass:
                sock.send(outputstr.encode())
                time.sleep(1)
                sock.close()
                print("Connection closed with ", addr)
    # sock.close()
    # print("Connection closed with ", addr)

def ImageProcess(detection,inbuf,buflen,height,width):
    left_x=0
    right_x=260
    up_y=144
    bottom_y=333

    tx = 425
    ty = 295

    global outputstr
    global ifpass
    while True:
        # get image into buffer
        dll.CameraSetAWB(0, c_bool(True))
        dll.CameraQueryImage(0, inbuf, byref(buflen), 0x104)
        arr = np.frombuffer(inbuf, np.uint8)
        img = np.reshape(arr, (height.value, width.value, 3))
        reshapeWidth = int(width.value / 4)
        reshapeHeight = int(height.value / 4)
        # using opencv to display the buffer image
        resize_img = cv2.resize(img, (reshapeWidth, reshapeHeight), interpolation=cv2.INTER_AREA)
        # get timestamp
        now = datetime.now()
        timeStamp = now.timestamp()

        back = detection.detect(resize_img)
        if back != None:
            x, y, w, h, cls, ifpass = back

            loclist = [timeStamp, x, y, w, h, detection.mapping[cls]]
            Rec = rf.Rectify(loclist)
            parameters=left_x, right_x, up_y, bottom_y
            loc = Rec.Get_real_loc(parameters,reshapeWidth,reshapeHeight)
            xreal, yreal = tx - loc[1], ty - loc[0]
            # print(420 - loc[1],300-loc[0])
            outputlist = [timeStamp, xreal, yreal]
            # outputlist = [timeStamp, x, y, w, h, detection.mapping[cls]]
            outputstr = " ".join(list(map(lambda x: str(x), outputlist)))
            # print("Block Information: ",outputstr)
            if ifpass:
                cv2.imshow("img",resize_img)
                cv2.waitKey(1)
        else:
            print("no block found!\n")
            continue


if __name__ == "__main__":
    # TCP Socket Init
    TCPSocket = socket.socket()
    LocalADDR = ""
    LocalPORT = 23333
    TCPSocket.bind((LocalADDR,LocalPORT))
    TCPSocket.listen(5)
    # Camera Interface Init
    dll = cdll.LoadLibrary("JHCap2.dll")
    dll.CameraInit(0)
    dll.CameraSetResolution(0, 0, 0, 0)
    buflen = c_int()
    width = c_int()
    height = c_int()
    dll.CameraGetImageSize(0, byref(width), byref(height))
    dll.CameraGetImageBufferSize(0, byref(buflen), 0x4)
    inbuf = create_string_buffer(buflen.value)

    # image process thread
    detection = dc.Detect()
    IMGthread = threading.Thread(target=ImageProcess, args=(detection,inbuf,buflen,height,width))
    IMGthread.start()

    # server thread
    sock, addr = TCPSocket.accept()
    TCPthread = threading.Thread(target=TCPLink, args=(sock, addr))

    TCPthread.start()


    IMGthread.join()
    TCPthread.join()
    print("Process Finished!")

