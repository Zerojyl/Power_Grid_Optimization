# 导入相关包
import math
import torch
import yaml
import joblib
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from utils.data_process.power_data_process import power_process

from torch.utils.tensorboard import SummaryWriter


def evaluate_model(data_str='data1', writer=None, config_path='utils/configs/power_forecasting/lstm_power_forecasting.yaml'):
    """
    模型预测值与真实值处理，获取 RMSE、MAE 等评价指标信息

    """
    # 读取配置文件并导入模型
    with open(config_path) as file:
        config = yaml.safe_load(file)
    if writer is None:
        writer = SummaryWriter(log_dir=config['tensorboard_save']['tensorboard_eval_dir']+'/'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    predict_model_path = config['model_config'][data_str]['predict_model_path']
    dataset, train_dataloader, test_dataloader = power_process(yaml_path=config_path, data=data_str)
    model = torch.load(predict_model_path)

    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    scaler = joblib.load(config['data_config'][data_str]['scaler_save_path'])
    for i, (X1, X2, y) in enumerate(train_dataloader):
        X1 = X1.to(device)
        X2 = X2.to(device)
        y = y.to(device)
        y_pred = model(X1, X2)
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
    print(predicted_data.shape)
    print(true_data.shape)
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
    writer.add_scalar('RMSE/'+data_str, rmse)
    writer.add_scalar('MAE/'+data_str, mae)
    

    # 绘制预测图形
    show_start = torch.randint(0, len(predicted_data)-1000, (1,)).item()
    show_end = show_start + 12
    plt.figure(facecolor='white')
    for i in range(predict_time):   
        plt.subplot(predict_time, 1, i+1)
        plt.plot(temp_true_data[show_start:show_end,i,target_index], label='True Data')
        plt.plot(temp_predicted_data[show_start:show_end,i,target_index], label='Prediction')
        plt.title('time step:{}min'.format(i*15+15))
        plt.legend()
    plt.show()
    writer.add_figure('Prediction vs True Data ('+ data_str+ ')', plt.gcf())






if __name__ == '__main__':
    config_path='utils/configs/power_forecasting/lstm_power_forecasting.yaml' 
    with open(config_path) as file:
        config = yaml.safe_load(file)

    writer = SummaryWriter(log_dir=config['tensorboard_save']['tensorboard_eval_dir']+'/'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    print('data1 evaluating------------------')
    evaluate_model(writer=writer, config_path=config_path, data_str='data1')
    print('data2 evaluating------------------')
    evaluate_model(writer=writer, config_path=config_path, data_str='data2')
    print('data3 evaluating------------------')
    evaluate_model(writer=writer, config_path=config_path, data_str='data3')
    print('data4 evaluating------------------')
    evaluate_model(writer=writer, config_path=config_path, data_str='data4')


        





