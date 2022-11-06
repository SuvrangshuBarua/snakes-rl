import torch
import torch.nn as nn
import torch.optim as optimizer
import torch.nn.functional as Func
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def feed_forward_network(self):
        x = Func.relu(self.linear1(x))
        x = self.linear2(x)
        return x
        
    def save(self, file_name = 'model.pth'):
        folder_path = './model'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_name = os.path.join(folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class Qtrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optimizer.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        pass