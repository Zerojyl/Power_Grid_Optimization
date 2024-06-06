import torch.nn as nn
import torch



class power_lstm_net(nn.Module):
    def __init__(self, input_dim1, hidden_dim, input_dim2, output_dim):
        super(power_lstm_net, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_dim1, hidden_dim, batch_first=True)
        self.fc = nn.Sequential(nn.Linear(hidden_dim+input_dim2, output_dim*2),
                                nn.Dropout(0.5),
                                nn.ReLU(),
                                nn.Linear(output_dim*2, output_dim))

    def forward(self, x1, x2):
        lstm_out, _ = self.lstm(x1)
        lstm_out = torch.cat((lstm_out[:, -1, :], x2), dim=1)
        out = self.fc(lstm_out)
        return out


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
    model = power_lstm_net(10, 12, 14, 16)
    print(model)
    input1 = torch.randn(1, 5, 10)
    input2 = torch.randn(1, 14)
    output = model(input1, input2)
    print(output)
    print(output.shape)
    print('done')