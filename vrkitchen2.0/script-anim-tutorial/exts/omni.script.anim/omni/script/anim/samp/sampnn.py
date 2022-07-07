# network
import onnxruntime
import numpy as np
import torch
import time

motion_net_path = "D:/research/SAMP/Assets/OnnxModels/MotionNet.onnx"
goal_net_path = "D:/research/SAMP/Assets/OnnxModels/GoalNet.onnx"

# norm_data_folder = "D:/research/SAMP/Assets/NormData/MotionNet/"

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

class SAMPNN():
    def __init__(self):
        self.model = None

        self.x1_dim = 647
        self.x2_dim = 2048
        self.output_dim = 647
        self.zDim = 64

        self.load_motion_net()
        self.load_norm_stats()
        self.reset_input()

    def reset_input(self):
        self.x = []
        self.z = []
        
        self.pivot = -1
        self.y = []

        # TODO: load normalization data

    def load_norm_stats(self):
        """
        load normalization statistics
        """
        from .stats import X1MEAN, X1STD, X2MEAN, X2STD, YMEAN, YSTD
        self.x1mean = np.array(X1MEAN)
        self.x1std = np.array(X1STD)
        self.x2mean = np.array(X2MEAN)
        self.x2std = np.array(X2STD)
        self.ymean = np.array(YMEAN)
        self.ystd = np.array(YSTD)
        # print("x1mean: ", len(self.x1mean))
        # print("x1std: ", len(self.x1std))
        # print("x2mean: ", len(self.x2mean))
        # print("x2std: ", len(self.x2std))
        # print("ymean: ", len(self.ymean))
        # print("ystd: ", len(self.ystd))

    def load_motion_net(self, device = torch.device('cuda'), dtype = torch.float32):

        x1 = torch.randn(1, self.x1_dim, device= device , dtype=dtype)
        x2 = torch.randn(1, self.x2_dim, device=device, dtype=dtype)
        z = torch.randn(1, self.zDim , device=device, dtype=dtype)

        # self.model = onnx.load(motion_net_path)
        # print("sampnn:", onnx.shape_inference.infer_shapes(self.model))
        self.ort_session = onnxruntime.InferenceSession(motion_net_path, providers=["CUDAExecutionProvider"])

        begin_time = time.time()
        ort_inputs = {self.ort_session.get_inputs()[0].name: to_numpy(z),
                      self.ort_session.get_inputs()[1].name: to_numpy(x1),
                      self.ort_session.get_inputs()[2].name: to_numpy(x2)}

        ort_outs = self.ort_session.run(None, ort_inputs) 
        print("onnxruntime device:", onnxruntime.get_device())
        print("ONNX output shape {}".format(ort_outs[0].shape))
        print("time elapse: ", time.time() - begin_time)

    def predict(self):
        x1 = np.array(self.x[:self.x1_dim])
        x2 = np.array(self.x[self.x1_dim:])

        x1 = (x1 - self.x1mean)/ self.x1std
        x2 = (x2 - self.x2mean)/ self.x2std

        z = 0.0 * np.random.randn(self.zDim)

        x1 = x1[None,...].astype(np.float32)
        x2 = x2[None,...].astype(np.float32)
        z = z[None,...].astype(np.float32)

        # print("sampnn x1:", x1.dtype)
        # print("sampnn x2:", x2.dtype)
        # print("sampnn z:", z.dtype)

        begin_time = time.time()
        ort_inputs = {self.ort_session.get_inputs()[0].name: z,
                      self.ort_session.get_inputs()[1].name: x1,
                      self.ort_session.get_inputs()[2].name: x2}

        ort_outs = self.ort_session.run(None, ort_inputs) 
        # print("predict onnxruntime device:", onnxruntime.get_device())
        # print("predict ONNX output shape {}".format(ort_outs[0].shape))
        self.y = ort_outs[0][0] * self.ystd + self.ymean
        # print("predict y shape", self.y.shape)
        # print("predict time elapse: ", time.time() - begin_time)
        # print("self.y", len(self.y), self.y)

        
    def read(self):
        self.pivot += 1
        return self.y[self.pivot]

        

        




    
    
