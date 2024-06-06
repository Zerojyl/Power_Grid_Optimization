from utils.data_process.make_dataset import make_dataset
import yaml
from torch.utils.data import DataLoader, TensorDataset
import torch

def power_process(yaml_path = 'utils/configs/power_forecasting/lstm_power_forecasting.yaml', data = 'data1'):
    with open(yaml_path) as file:
        config = yaml.safe_load(file)
    my_dataset = make_dataset(data_path=config['data_config'][data]['data_path'],
                                normalization=config['data_config']['normalization'], 
                                previous_step=config['data_config']['previous_step'], 
                                previous_drop=config['data_config']['previous_drop'],
                                forecast_step=config['data_config']['forecast_step'],
                                forecast_drop=config['data_config']['forecast_drop'], 
                                target_features=config['data_config']['target_features'],
                                dropnan=True)
    df = my_dataset.dataframe
    target_columns = my_dataset.target_columns
    y = df[target_columns]
    X = df.drop(target_columns, axis=1)
    y = y.values
    X = X.values
    X = X.reshape((X.shape[0], 1, X.shape[1]))
    y = y.reshape((y.shape[0], 1, y.shape[1]))
    validation_split = config['data_config']['validation_split']
    train_len = int(len(X) * (1-validation_split))
    X_train, X_val = X[:train_len], X[train_len:]
    y_train, y_val = y[:train_len], y[train_len:]
    # make dataloader
    X_train = torch.from_numpy(X_train).float()
    y_train = torch.from_numpy(y_train).float()
    X_val = torch.from_numpy(X_val).float()
    y_val = torch.from_numpy(y_val).float()
    
    train_dataloader = DataLoader(TensorDataset(X_train, y_train), batch_size=config['model_config']['batch_size'], shuffle=True)
    val_dataloader = DataLoader(TensorDataset(X_val, y_val), batch_size=config['model_config']['batch_size'], shuffle=False)
    return my_dataset, train_dataloader, val_dataloader

if __name__ == '__main__':
    dataset, train_dataloader, val_dataloader = power_process()
    X_train, y_train = next(iter(train_dataloader))
    X_val, y_val = next(iter(val_dataloader))
    print(X_train.shape, y_train.shape, X_val.shape, y_val.shape)
    print('done')


