import pandas as pd
import yaml
import torch
import joblib

load_path = 'C:/project/Electric-innovation-competition/Power_Grid_Optimization/Data/load_data/load_data.csv'
power1_path='C:/project/Electric-innovation-competition/Power_Grid_Optimization/Data/power_data/merged_power_data1.csv'
power2_path='C:/project/Electric-innovation-competition/Power_Grid_Optimization/Data/power_data/merged_power_data2.csv'
power3_path='C:/project/Electric-innovation-competition/Power_Grid_Optimization/Data/power_data/merged_power_data3.csv'
power4_path='C:/project/Electric-innovation-competition/Power_Grid_Optimization/Data/power_data/merged_power_data4.csv'

power_yaml_path = 'C:/project/Electric-innovation-competition/Power_Grid_Optimization/utils/configs/power_forecasting/lstm_power_forecasting.yaml'
load_yaml_path = 'C:/project/Electric-innovation-competition/Power_Grid_Optimization/utils/configs/load_forecasting/lstm_load_forecasting.yaml'
data_str = 'data2'

class csv2df:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path)
        self.df['time'] = pd.to_datetime(self.df['time'])
        self.df.set_index('time', inplace=True)

    def get_data(self, base_time='2019-01-03 00:00:00', point_step = 7, history_step = 4):
        base_time = pd.Timestamp(base_time)
        cur_time = base_time + pd.Timedelta(hours=point_step/4)
        time_list = [cur_time - pd.Timedelta(hours=point_step/4*i) for i in range(history_step+1, 0, -1)]
        for i in range(len(time_list)):
            assert time_list[i] in self.df.index, f'Timestamp {time_list[i]} not found in power1_df index'

        data = self.df.loc[time_list]
        return data
    
class predict_class(csv2df):
    def __init__(self, yaml_path, data_str, csv_path):
        super().__init__(csv_path)
        self.yaml_path = yaml_path
        self.data_str = data_str
        with open(yaml_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.model = self.model_load()
        self.history_step = self.config['data_config']['previous_step']
        self.forecast_step = self.config['data_config']['forecast_step']
        self.scaler_path = self.config['data_config'][self.data_str]['scaler_save_path']
        self.scaler = joblib.load(self.scaler_path)
        self.scaled_df = self.df_scale()


    def model_load(self):
        model_path = self.config['model_config'][self.data_str]['predict_model_path']
        model = torch.load(model_path)
        return model
    
    def get_data(self, point_step, base_time='2019-01-05 00:00:00', history = True):
        base_time = pd.Timestamp(base_time)
        cur_time = base_time + pd.Timedelta(hours=point_step/4)
        if history:
            time_list = [cur_time - pd.Timedelta(hours=point_step/4*i) for i in range(self.history_step+1, 0, -1)]
        else:
            time_list = [cur_time + pd.Timedelta(hours=point_step/4*i) for i in range(1, self.forecast_step+1)]
        
        for i in range(len(time_list)):
            assert time_list[i] in self.df.index, f'Timestamp {time_list[i]} not found in power1_df index'
        
        data = self.df.loc[time_list]
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
        return scaled_df
    
    # def df_inverse()
    

    def predict(self, point_step, base_time='2019-01-05 00:00:00'):
        data_pre_cur = self.get_data(point_step, base_time, history=True)
        data_pre_cur = torch.tensor(data_pre_cur.values).float()
        data_forecast = self.get_data(point_step, base_time, history=False)
        data_forecast = torch.tensor(data_forecast.values).float()
        print(data_forecast)
        if data_forecast.size()[1] != 0:
            predict_result = self.model(data_pre_cur, data_forecast)
        else:
            predict_result = self.model(data_pre_cur)
        return predict_result

# power2_class = predict_class(power_yaml_path, data_str, power2_path)
# predict_result = power2_class.predict(7)
# print(predict_result)

load1_class = predict_class(load_yaml_path, 'data1', load_path)
predict_result = load1_class.predict(7) 
print(predict_result)