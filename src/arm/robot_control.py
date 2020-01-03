import math
import DobotDllType as dType
import keyboard
import threading
import socket
import time
from datetime import datetime

STEP_PER_CRICLE = 360.0 / 1.8 * 10.0 * 16.0
MM_PER_CRICLE = 3.1415926535898 * 36.0
CONV_PARAM = 0.55   #converyor velocity parameter, usage: vel = float(30) * STEP_PER_CRICLE / MM_PER_CRICLE * CONV_PARAM
ARM_PARAM = 2.0 # arm velocity parameter, usage: v_arm = 30 * ARM_PARAM
INIT_X = 200
INIT_Y = 0
INIT_Z = 50

global v
v = 40

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}
"""
键盘监听控制传送带速度
"""
def speedup(x):
    global v
    a = keyboard.KeyboardEvent('down', 28, 'up')
    if x.event_type == 'down' and x.name == a.name:
        print("你按下了up键")
        v = v + 10
        vel = float(v) * STEP_PER_CRICLE / MM_PER_CRICLE * CONV_PARAM
        dType.SetEMotorEx(api, 0, 1, int(vel), 1)

def speeddown(x):
    global v
    a = keyboard.KeyboardEvent('down', 28, 'down')
    if x.event_type == 'down' and x.name == a.name:
        print("你按下了down键")
        v = v - 10
        vel = float(v) * STEP_PER_CRICLE / MM_PER_CRICLE * CONV_PARAM
        dType.SetEMotorEx(api, 0, 1, int(vel), 1)
    #当监听的事件为down键，且是按下的时候
"""
静态抓取，在固定位置抓和放
"""
def catch(api):
    #catch: move down to catch the block using a sucker
    # 设置机械臂速度
    v_arm = 50 * ARM_PARAM
    dType.SetPTPCoordinateParams(api, v_arm, 100, 20, 50, 1)
    # 设置末端执行器，并打开吸盘
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y, INIT_Z , 0, 1)
    dType.SetEndEffectorParamsEx(api, 59.7, 0, 0, 1)
    dType.SetEndEffectorSuctionCupEx(api, 1, 1)
    # 先向下移动抓取木块，然后移动到传送带外摆放
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y, INIT_Z-52, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y, INIT_Z, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X+100, INIT_Y, INIT_Z, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X+100, INIT_Y, INIT_Z-100, 0, 1)
    dType.SetEndEffectorSuctionCupEx(api, 0, 1)
    # 恢复原来的位置
    dType.SetPTPCmdEx(api, 2, INIT_X+100, INIT_Y, INIT_Z, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y, INIT_Z, 0, 1)
'''
移动传送带，用来测定机械臂和传送带的速度
'''
def move(api):
    #move: move from +y to -y
    v_arm = 50 * ARM_PARAM
    dType.SetPTPCoordinateParams(api, v_arm, 10, 20, 50, 1)
    dType.SetEndEffectorParamsEx(api, 59.7, 0, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y+100, INIT_Z, 0, 0)
    # dType.SetWAITCmdEx(api, 0.5, 1)
    dType.SetEndEffectorSuctionCupEx(api, 1, 0)
    v_arm = 50 * ARM_PARAM    #mm/s
    dType.SetPTPCoordinateParams(api, v_arm, 200, 20, 50, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y-100, INIT_Z, 0, 1)
    dType.SetEndEffectorSuctionCupEx(api, 0, 1)
'''
接收来自视觉的包
'''
def receive(TCPSocket):
    text = TCPSocket.recv(1024).decode()
    textlist = text.split()
    # data format: time, x, y
    time = float(textlist[0])
    position_x = int(float(textlist[1]))
    position_y = int(float(textlist[2]))
    return [position_x,position_y,time]
'''
弧形抓取
'''
def ArcCatch(api,v,x):
    # 打开吸盘
    dType.SetEndEffectorParamsEx(api, 59.7, 0, 0, 1)
    dType.SetEndEffectorSuctionCupEx(api, 1, 1)
    # 设置机械臂速度
    dType.SetPTPCoordinateParams(api, v * ARM_PARAM, 100, 20, 50, 1)
    # 圆弧轨迹
    cirPoint = [x, INIT_Y, INIT_Z - 55, 0]
    toPoint = [x, INIT_Y - 100, INIT_Z - 30, 0]
    dType.SetARCCmd(api, cirPoint, toPoint, 1)
    # 结束圆弧轨迹，把物体放到某个区域
    dType.SetPTPCoordinateParams(api, 50 * ARM_PARAM, 200, 20, 50, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X + 100, INIT_Y - 100, INIT_Z - 30, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X + 100, INIT_Y - 100, INIT_Z - 100, 0, 1)
    dType.SetEndEffectorSuctionCupEx(api, 0, 1)
    dType.SetPTPCmdEx(api, 2, INIT_X, INIT_Y + 100, INIT_Z - 30, 0, 1)

if __name__ == "__main__":
    api = dType.load()
    state = dType.ConnectDobot(api, "", 115200)[0]
    print("Connect status:", CON_STR[state])
    if (state == dType.DobotConnect.DobotConnect_NoError):
        # conveyor
        vel = float(v) * STEP_PER_CRICLE / MM_PER_CRICLE * CONV_PARAM  # mm/s
        dType.SetEMotorEx(api, 0, 1, 0, 1)
        dType.SetWAITCmdEx(api, 1, 1)
        # begin to move
        dType.SetEMotorEx(api, 0, 1, int(vel), 1)
        keyboard.hook(speedup)
        keyboard.hook(speeddown)
        # catch(api)
        # 通讯连接
        LocalADDR = "172.20.10.7"
        LocalPORT = 23333
        TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPSocket.connect((LocalADDR, LocalPORT))
        [x,y,t] = receive(TCPSocket)
        # 先快速移动到抓取的准备位置
        dType.SetPTPCoordinateParams(api, 50 * ARM_PARAM, 200, 20, 50, 1)
        dType.SetPTPCmdEx(api, 2, x, INIT_Y + 100, INIT_Z - 30, 0, 1)
        now = datetime.now()
        timeStamp = now.timestamp()
        #总共移动到抓取准备位置的时间
        totaltime = (y - (INIT_Y+100))/v;
        waittime = totaltime - (timeStamp - t) - v/100
        print("waittime: ",waittime)
        dType.SetWAITCmdEx(api, waittime, 1)
        # catch
        ArcCatch(api,v,x)

        keyboard.wait('esc')
        dType.SetEMotorEx(api, 0, 1, 0, 1)  #turn off the conveyor
        # TCPSocket.close()



    dType.DisconnectDobot(api)


