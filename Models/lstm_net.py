import torch.nn as nn
import torch

class lstm_net(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(lstm_net, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Sequential(nn.Linear(hidden_dim, output_dim))

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        out = self.fc(lstm_out[:, -1, :])
        return out
    
# 多项式回归模型
class poly_net(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(poly_net, self).__init__()
        self.fc = nn.Sequential(nn.Linear(input_dim, input_dim*2),
                                nn.ReLU(),
                                nn.Linear(input_dim*2, hidden_dim),
                                nn.Dropout(0.5),
                                nn.ReLU(),
                                nn.Linear(hidden_dim, output_dim))

    def forward(self, x):
        out = self.fc(x)
        return out
    

if __name__ == '__main__':
    model = lstm_net(10, 10, 10)
    print(model)
    input = torch.randn(5, 1, 10)
    output = model(input)
    print(output.size())
    print('done')