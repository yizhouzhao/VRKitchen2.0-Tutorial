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

        # self.load_motion_net()
        self.reset_input()
        self.load_norm_stats()

    def reset_input(self):
        self.x = []
        self.z = []
        
        self.y = []

        # TODO: load normalization data

    def load_norm_stats(self):
        pass

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
        pass
        




    
    
