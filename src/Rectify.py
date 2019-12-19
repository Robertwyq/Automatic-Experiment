class Rectify:
    def __init__(self, output):
        self.v = 0 # initial_v = 0
        self.time = output[0] #str
        self.cx = float(output[1])
        self.cy = float(output[2])
        self.w = float(output[3])
        self.h = float(output[4])
    def show(self):
        print('cx=',self.cx)
        print('cy=',self.cy)
        print('w=',self.w)
        print('h=',self.h)
    def Get_real_loc(self,parameters):
        X_pixel = (parameters[1] - parameters[0])/image.shape[1]
        Y_pixel = (parameters[3] - parameters[2])/image.shape[0]
        Real_X = X_pixel*self.cx+parameters[0]
        Real_Y = Y_pixel*self.cy+parameters[2]
        Real_W = X_pixel*self.w
        Real_H = Y_pixel*self.h
        return [Real_X,Real_Y,Real_W,Real_H]
    def Compute_V(self):
        return self.v
    # Kalman Filter
    def KF(self):
        return self.v
