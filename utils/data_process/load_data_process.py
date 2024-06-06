from utils.data_process.make_dataset import make_dataset
import yaml
from torch.utils.data import DataLoader, TensorDataset
import torch

def load_process(yaml_path = 'utils/configs/load_forecasting/lstm_load_forecasting.yaml', data = 'data1'):
    with open(yaml_path) as file:
        config = yaml.safe_load(file)
    my_dataset = make_dataset(data_path=config['data_config'][data]['data_path'],
                                normalization=config['data_config']['normalization'], 
                                previous_step=config['data_config']['previous_step'], 
                                previous_features=config['data_config']['previous_features'],
                                forecast_step=config['data_config']['forecast_step'],
                                forecast_features=config['data_config']['forecast_features'], 
                                target_features=config['data_config']['target_features'],
                                dropnan=True)
    y = my_dataset.target_df
    X1 = my_dataset.pre_curr_df
    y = y.values
    X1 = X1.values
    pre_curr_steps = config['data_config']['previous_step']+1
    X1 = X1.reshape((X1.shape[0], pre_curr_steps, -1))
    y = y.reshape((y.shape[0], y.shape[1]))
    validation_split = config['data_config']['validation_split']
    train_len = int(len(y) * (1-validation_split))
    X1_train, X1_val = X1[:train_len], X1[train_len:]
    y_train, y_val = y[:train_len], y[train_len:]
    # make dataloader
    X1_train = torch.from_numpy(X1_train).float()
    X1_val = torch.from_numpy(X1_val).float()
    y_train = torch.from_numpy(y_train).float()
    y_val = torch.from_numpy(y_val).float()
    
    train_dataloader = DataLoader(TensorDataset(X1_train, y_train), batch_size=config['model_config']['batch_size'], shuffle=True)
    val_dataloader = DataLoader(TensorDataset(X1_val, y_val), batch_size=config['model_config']['batch_size'], shuffle=False)
    return my_dataset, train_dataloader, val_dataloader

if __name__ == '__main__':
    dataset, train_dataloader, val_dataloader = load_process()
    X1_train, y_train = next(iter(train_dataloader))
    X1_val, y_val = next(iter(val_dataloader))
    print(X1_train.shape)
    print(y_train.shape)
    print('done')


