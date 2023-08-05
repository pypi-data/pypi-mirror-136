import numpy as np
import torch.nn as nn
import torch
from sklearn import datasets

class LinearModel(nn.Module):
    '''
    Simple base linear model of neural network
    '''
    def __init__(self, input_size, output_size):
        super(LinearModel, self).__init__()
        self.linear = nn.Linear(input_size, output_size)

    def forward(self, x):
        y_predicted = torch.sigmoid(self.linear(x))
        return y_predicted

class MultipleLinearLayersModel(nn.Module):
    '''
    Linear Model With Multiple Linear Layers
    '''
    def __init__(self, input_size, hidden_size, num_classes):
        super(MultipleLinearLayersModel, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out