from sklearn import preprocessing
import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader, Dataset


class make_dataset(Dataset):
    def __init__(self, data_path, normalization, previous_step, previous_features, forecast_step, forecast_features, target_features, dropnan=True):
        self.original_data = pd.read_csv(data_path, index_col=['time'])
        self.target_columns_index = self.original_data.columns.get_indexer(target_features)

        if normalization == 'standard':
            self.scaler = preprocessing.StandardScaler()# 标准化 0均值 1方差
        elif normalization == 'minmax':
            self.scaler = preprocessing.MinMaxScaler()# 最小最大值标准化
        else:
            # threw an error
            raise ValueError('normalization should be standard or minmax')
        self.scaled_data = self.df_scale(self.original_data)

        self.pre_curr_df, self.fore_df, self.target_df = series_to_supervised(self.scaled_data, target_features, previous_step, forecast_step, previous_features, forecast_features, dropnan)
        

    def df_scale(self, df):
        values = df.values
        columns = df.columns
        values = self.scaler.fit_transform(values)
        scaled_df = pd.DataFrame(values, columns=columns)
        return scaled_df
    
    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx): 
        data = self.data.iloc[idx]
        data = torch.tensor(data.values, dtype=torch.float32)
        return data
    

    


def series_to_supervised(df, target_features, previous_step = 1, forecast_step = 1, previous_features = None, forecast_features = None, dropnan = True):
    '''
    input:
        df: dataframe of data
        previous_drop: is a list of columns name to drop in previous df
        forecast_drop: is a list of columns name to drop in forecast df
        ...
    '''
    previous_df = df
    forecast_df = df
    if previous_features:
        previous_df = df[previous_features]
    if forecast_features:
        forecast_df = df[forecast_features]
    

    res_df = pd.DataFrame()
    names = []
    forecast_columns = []
    target_columns = []
    # 历史序列(t-n, ... t-1)
    for i in range(previous_step, 0, -1):
        res_df  = pd.concat([res_df, previous_df.shift(i)], axis = 1)
        names += [('%s(t-%d)' % (column, i)) for column in previous_df.columns]
    # 当前序列
    res_df = pd.concat([res_df, previous_df], axis = 1)
    names += [('%s(t)' % column) for column in previous_df.columns]
    # 预测序列 (t+1, ... t+n)
    for i in range(1, forecast_step+1):
        res_df = pd.concat([res_df, forecast_df.shift(-i)], axis = 1)
        names += [('%s(t+%d)' % (column, i)) for column in forecast_df.columns]
        forecast_columns += [('%s(t+%d)' % (column, i)) for column in forecast_features]
        target_columns += [('%s(t+%d)' % (column, i)) for column in target_features]
    # 组合起来
    res_df.columns = names
    # 丢掉NaN
    if dropnan:
        res_df.dropna(inplace=True)

    res_target_df = res_df[target_columns]
    res_fore_df = res_df[forecast_columns]
    res_fore_df = res_fore_df.drop(target_columns, axis=1)
    res_pre_curr_df = res_df.drop(forecast_columns, axis=1)


    return res_pre_curr_df, res_fore_df, res_target_df

