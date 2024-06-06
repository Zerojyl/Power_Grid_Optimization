# 导入相关包
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import os
import torch
from torch import nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import TensorDataset, DataLoader
import json
import yaml
import joblib
from datetime import datetime

from Models.lstm_net import lstm_net
from utils.data_process.power_data_process import power_process



def evaluate_model(data_str='data1', config_path='utils/configs/power_forecasting/lstm_power_forecasting.yaml'):
    """
    模型预测值与真实值处理，获取 RMSE、MAE 等评价指标信息

    """
    # 读取配置文件并导入模型
    with open(config_path) as file:
        config = yaml.safe_load(file)
    writer = SummaryWriter(log_dir=config['tensorboard_save']['tensorboard_eval_dir']+'/'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    predict_model_path = config['model_config']['predict_model_path']
    dataset, train_dataloader, test_dataloader = power_process(yaml_path='utils/configs/power_forecasting/lstm_power_forecasting.yaml', data=data_str)
    model = torch.load(predict_model_path)

    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    scaler = joblib.load(config['data_config'][data_str]['scaler_save_path'])
    for i, (X, y) in enumerate(train_dataloader):
        X = X.to(device)
        y = y.to(device)
        y_pred = model(X)
        if i == 0:
            predicted_data = y_pred.cpu().detach().numpy()
            true_data = y.cpu().detach().numpy()
        else:
            predicted_data = np.concatenate((predicted_data, y_pred.cpu().detach().numpy()))
            true_data = np.concatenate((true_data, y.cpu().detach().numpy()))

    # 获取目标列索引并反归一化
    target_index = dataset.target_columns_index
    original_col_len = len(dataset.original_data.columns)
    predicted_data = predicted_data.reshape(predicted_data.shape[0], -1 , len(target_index))
    true_data = true_data.reshape(true_data.shape[0], -1 , len(target_index))
    assert predicted_data.shape == true_data.shape 
    predict_time = predicted_data.shape[1]
    temp_predicted_data = np.ones((len(predicted_data), predict_time, original_col_len))
    temp_true_data = np.ones((len(predicted_data), predict_time, original_col_len))    
    for i in range(predict_time):
        for j, index in enumerate(target_index):
            temp_predicted_data[:,i,index] = predicted_data[:,i,j]
            temp_true_data[:,i,index] = true_data[:,i,j]
        # 反归一化
        temp_predicted_data[:,i,:] = scaler.inverse_transform(temp_predicted_data[:,i,:])
        temp_true_data[:,i,:] = scaler.inverse_transform(temp_true_data[:,i,:])
        
    
    # 计算 RMSE、MAE
    rmse = math.sqrt(mean_squared_error(temp_true_data[:,:,target_index].flatten(), temp_predicted_data[:,:,target_index].flatten()))
    mae = mean_absolute_error(temp_true_data[:,:,target_index].flatten(), temp_predicted_data[:,:,target_index].flatten())
    print("RMSE:{}".format(round(rmse,3)))
    print("MAE: {}".format(round(mae, 3)))
    writer.add_scalar('RMSE', rmse)
    writer.add_scalar('MAE', mae)
    

    # 绘制预测图形
    show_start = 0
    show_end = 100
    plt.figure(facecolor='white')
    for i in range(predict_time):   
        plt.subplot(predict_time, 1, i+1)
        plt.plot(temp_true_data[show_start:show_end,i,target_index], label='True Data')
        plt.plot(temp_predicted_data[show_start:show_end,i,target_index], label='Prediction')
        plt.title('time step:{}min'.format(i*15+15))
        plt.legend()
    plt.show()

    writer.add_figure('Prediction vs True Data', plt.gcf())







if __name__ == '__main__':
    evaluate_model()

        





