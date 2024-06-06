# 导入相关包
import torch
import yaml
import joblib
from torch import nn
import torch.optim as optim
from datetime import datetime
from Models.lstm_net import power_lstm_net
from utils.data_process.power_data_process import power_process
from torch.utils.tensorboard import SummaryWriter


def power_forecast_training(data_str='data1', writer=None, config_path='utils/configs/power_forecasting/lstm_power_forecasting.yaml'):
    
    with open(config_path) as file:
        config = yaml.safe_load(file)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if writer is None:
        writer = SummaryWriter(log_dir=config['tensorboard_save']['tensorboard_train_dir']+'/'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    config_str = str(config)
    writer.add_text('Config Parameters', config_str, 0)
    

    load_before_training = config['model_config'][data_str]['load_before_training']
    load_model_path = config['model_config'][data_str]['load_model_path']
    save_model_dir = config['model_config'][data_str]['save_model_dir']


    hidden_dim = config['model_config']['hidden_dim']
    # dataset and dataloader
    dataset, train_dataloader, test_dataloader = power_process(yaml_path=config_path, data=data_str)
    input_dim1 = next(iter(train_dataloader))[0].shape[2]
    input_dim2 = next(iter(train_dataloader))[1].shape[1]
    output_dim = next(iter(train_dataloader))[2].shape[1]
    scaler = dataset.scaler
    scaler_save_path = config['data_config'][data_str]['scaler_save_path']
    joblib.dump(scaler, scaler_save_path)


    model = power_lstm_net(input_dim1, hidden_dim, input_dim2, output_dim).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=config['model_config']['learning_rate'])
    if load_before_training and load_model_path is not None:
        model.load_state_dict(torch.load(load_model_path))
        print("model loaded------------------")



    # 训练网络
    epochs = config['model_config']['epochs']
    train_loss = [0.0 for _ in range(epochs)]
    test_loss = [0.0 for _ in range(epochs)]
    print("start training------------------")
    for epoch in range(epochs):
        model.train()
        for train_x1, train_x2, train_y in train_dataloader:
            train_x1 = train_x1.to(device)
            train_x2 = train_x2.to(device)
            train_y = train_y.to(device)

            optimizer.zero_grad()
            outputs = model(train_x1, train_x2)
            loss = criterion(outputs, train_y)
            train_loss[epoch] += loss.item()*train_y.size(0)
            loss.backward()
            optimizer.step()
            

        model.eval()
        for test_x1, test_x2, test_y in test_dataloader:
            test_x1 = test_x1.to(device)
            test_x2 = test_x2.to(device)
            test_y = test_y.to(device)

            loss = criterion(model(test_x1, test_x2), test_y)
            test_loss[epoch] += loss.item()*test_y.size(0)

        train_loss[epoch] /= len(train_dataloader.dataset)
        test_loss[epoch] /= len(test_dataloader.dataset)

        print(f'Epoch: {epoch+1}/{epochs}, Train Loss: {train_loss[epoch]:.4f}, Test Loss: {test_loss[epoch]:.4f}')
        save_path = save_model_dir+save_model_dir.split('/')[-3]+'_epoch_'+str(epoch)+'.pth'
        torch.save(model, save_path)
        writer.add_scalar('Loss/train/'+data_str, train_loss[epoch], epoch)
        writer.add_scalar('Loss/val/'+data_str, test_loss[epoch], epoch)



    print("model saved------------------")
    # --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    config_path='utils/configs/power_forecasting/lstm_power_forecasting.yaml' 
    with open(config_path) as file:
        config = yaml.safe_load(file)

    writer = SummaryWriter(log_dir=config['tensorboard_save']['tensorboard_train_dir']+'/'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    print('data1 training------------------')
    power_forecast_training(data_str='data1', config_path=config_path, writer=writer)
    print('data2 training------------------')
    power_forecast_training(data_str='data2', config_path=config_path, writer=writer)
    print('data3 training------------------')
    power_forecast_training(data_str='data3', config_path=config_path, writer=writer)
    print('data4 training------------------')
    power_forecast_training(data_str='data4', config_path=config_path, writer=writer)

    print('done')
