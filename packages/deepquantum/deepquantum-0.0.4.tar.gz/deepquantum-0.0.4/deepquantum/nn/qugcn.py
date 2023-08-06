import torch
import torch.nn as nn
from deepquantum.utils import *
from deepquantum.utils import encoding,dag
import numpy as np
from deepquantum import Circuit

class QuGCN(nn.Module):
    """
    Quantum Conv layer with equalized learning rate and custom learning rate multiplier.
    """

    # 2qubits
    def __init__(self, n_qubits, gain=2 ** 0.5, use_wscale=True, lrmul=1):
        super().__init__()

        he_std = gain * 5 ** (-0.5)  # He init
        if use_wscale:
            init_std = 1.0 / lrmul
            self.w_mul = he_std * lrmul
        else:
            init_std = he_std / lrmul
            self.w_mul = lrmul
        self.weight = nn.Parameter(nn.init.uniform_(torch.empty(5), a=0.0, b=2 * np.pi) * init_std)

        self.n_qubits = n_qubits

        self.linear = nn.Linear(16, 2)  # 这里的输出直接连接着sigmoid层，输出的维度应该为分类的种类数

        self.softmax = nn.Softmax(dim=1)  # 上一层全连接层输出两个维度，表示的是分类的种类数，这里根据实际的数据结构调整dim值

        # 每一条边的

    def GCN_Layer(self):
        w = self.weight * self.w_mul
        # 新增线路实例申明
        cir = Circuit(self.n_qubits)

        # 新添加门写法
        for which_q in range(0, self.n_qubits):
            # 表示对节点自身特征进行操作
            cir.rx(which_q, w[0])
            cir.ry(which_q, w[1])
            cir.rz(which_q, w[2])

        U = cir.get()
        return U

    def forward(self, edges, nodes_feature):
        model = self.GCN_Layer()

        for i in range(len(edges)):
            c = torch.cat((nodes_feature[int(edges[i, 0])], nodes_feature[int(edges[i, 1])]), 0)
            # 将输入变成量子状态
            quantum_data = encoding(c)
            if i == 0:
                output = model @ quantum_data @ dag(model)
            else:
                output2 = model @ quantum_data @ dag(model)
                #                 output = torch.cat((output,output2),0)#将得到的每组节点对的量子数据结果拼接起来
                output = output @ output2  # 4*4的大小

        output = output.view(1, 4 * 4)
        output = output.float()  # 这一步期望用某些方法将量子数据转换为经典数据
        output2 = self.linear(output)
        yorn = self.softmax(output2)
        return yorn