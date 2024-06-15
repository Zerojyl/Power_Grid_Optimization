import pandas as pd
import numpy as np
import yaml
import torch
import joblib



class csv2df:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path)
        self.df['time'] = pd.to_datetime(self.df['time'])
        self.df.set_index('time', inplace=True)

    def get_data(self, base_time='2019-01-05 00:00:00', point_step = 7, history_step = 4):
        base_time = pd.Timestamp(base_time)
        cur_time = base_time + pd.Timedelta(hours=point_step/4)
        time_list = [cur_time - pd.Timedelta(hours=i/4) for i in range(history_step, -1, -1)]
        for i in range(len(time_list)):
            assert time_list[i] in self.df.index, f'Timestamp {time_list[i]} not found in power1_df index'
        print('check point 2', time_list)
        data = self.df.loc[time_list]
        return data
    


    
class predict_class(csv2df):
    def __init__(self, yaml_path, data_str, csv_path):
        super().__init__(csv_path)
        self.yaml_path = yaml_path
        self.data_str = data_str
        with open(yaml_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model_load().to(self.device)
        self.history_step = self.config['data_config']['previous_step']
        self.forecast_step = self.config['data_config']['forecast_step']

        self.scaler_path = self.config['data_config'][self.data_str]['scaler_save_path']
        self.scaler = joblib.load(self.scaler_path)
        self.scaled_df = self.df_scale()

        self.target_column = self.config['data_config']['target_features']
        self.target_column_index = self.scaled_df.columns.get_indexer(self.target_column)
        self.column_len = len(self.scaled_df.columns)


    def model_load(self):
        model_path = self.config['model_config'][self.data_str]['predict_model_path']
        model = torch.load(model_path)
        return model
    
    def get_data(self, point_step, base_time='2019-01-05 00:00:00', history = True):
        base_time = pd.Timestamp(base_time)
        cur_time = base_time + pd.Timedelta(hours=point_step/4)

        if history:
            time_list = [cur_time - pd.Timedelta(hours=i/4) for i in range(self.history_step, -1, -1)]
        else:
            time_list = [cur_time + pd.Timedelta(hours=i/4) for i in range(1, self.forecast_step+1)]
        
        for i in range(len(time_list)):
            assert time_list[i] in self.scaled_df.index, f'Timestamp {time_list[i]} not found in df index'
        print('check point 1', time_list)
        data = self.scaled_df.loc[time_list]
        if history:
            selected_features = self.config['data_config']['previous_features']
            drop_features = []
        else:
            selected_features = self.config['data_config']['forecast_features']
            drop_features = self.config['data_config']['target_features']
        data = data[selected_features]
        data = data.drop(drop_features, axis=1)
     
        return data

    def df_scale(self):
        values = self.df.values
        columns = self.df.columns
        values = self.scaler.transform(values)
        scaled_df = pd.DataFrame(values, columns=columns)
        scaled_df['time'] = self.df.index
        scaled_df.set_index('time', inplace=True)
        return scaled_df
    
    def predict_inverse(self, predicted_data):
        predicted_data = predicted_data.reshape(-1, self.forecast_step, len(self.target_column_index))
        assert predicted_data.shape[0] == 1
        temp_predicted_data = np.ones((predicted_data.shape[0], self.forecast_step, self.column_len))
        for fore_index in range(self.forecast_step):
            for i, target_index in enumerate(self.target_column_index):
                temp_predicted_data[:, fore_index, target_index] = predicted_data[:, fore_index, i]
            # 反归一化
            temp_predicted_data[:, fore_index, :] = self.scaler.inverse_transform(temp_predicted_data[:, fore_index, :])
        predicted_data_inver_tran = temp_predicted_data[:, :, self.target_column_index]
        predicted_data_inver_tran = predicted_data_inver_tran.reshape(self.forecast_step, len(self.target_column_index))
        return predicted_data_inver_tran

    def predict(self, point_step, base_time='2019-01-05 00:00:00'):
        data_pre_cur = self.get_data(point_step, base_time, history=True)
        # print('check point 3', data_pre_cur.shape)
        data_pre_cur = torch.tensor(data_pre_cur.values).float().to(self.device)
        data_pre_cur = data_pre_cur.unsqueeze(0)
        # print('check point 4', data_pre_cur.size())
        # print(data_pre_cur.size())
        data_forecast = self.get_data(point_step, base_time, history=False)
        data_forecast = torch.tensor(data_forecast.values).float().to(self.device)
        # print(data_forecast)
        if data_forecast.size()[1] != 0:
            # print('check point 5', data_forecast.size())
            data_forecast = data_forecast.reshape(1, -1)
            # print('check point 6', data_forecast.size())
            predict_result = self.model(data_pre_cur, data_forecast)
            predict_result = predict_result.reshape(self.forecast_step, len(self.target_column_index))
        else:
            predict_result = self.model(data_pre_cur)
            predict_result = predict_result.reshape(self.forecast_step, len(self.target_column_index))
        predict_result_inv = self.predict_inverse(predict_result.detach().cpu().numpy())
        return predict_result_inv
    

if __name__ == '__main__':
    # change the path to your own path
    # load_path = './Data/load_data/load_data.csv'
    load_path = './Data/load_data/load_data.csv'
  
    # 将下面的路径都改为相对路径
    
    power1_path = './Data/power_data/merged_power_data1.csv'
    power2_path='./Data/power_data/merged_power_data2.csv'
    power3_path='./Data/power_data/merged_power_data3.csv'
    power4_path='./Data/power_data/merged_power_data4.csv'


    power_yaml_path = './utils/configs/power_forecasting/lstm_power_forecasting.yaml'
    load_yaml_path = './utils/configs/load_forecasting/lstm_load_forecasting.yaml'
    data_str = 'data2'
    
    # # 读取特定时间点的数据
    # original_data = csv2df(load_path)
    # data_read = original_data.get_data(point_step = 10, history_step = 0)
    # print(data_read)

    # # 调用模型进行预测
    # load1_class = predict_class(load_yaml_path, 'data1', load_path)
    # predict_result = load1_class.predict(point_step = 10) 
    # print('predicted result(scaled): ', predict_result)
    # print('predicted result(scaled) shape: ', predict_result.shape)
    # predict_result_inv = load1_class.predict_inverse(predict_result)
    # print('predicted result(after inverse transform) shape: ', predict_result_inv.shape)

    # 读取特定时间点的数据
    original_data = csv2df(power2_path)
    data_read = original_data.get_data(point_step = 262, history_step = 5)
    print(data_read['power'])

    # 调用模型进行预测
    load1_class = predict_class(power_yaml_path, 'data2', power2_path)
    predict_result = load1_class.predict(point_step = 256) 
    print('predicted result: ', predict_result)
    print('predicted result shape: ', predict_result.shape)