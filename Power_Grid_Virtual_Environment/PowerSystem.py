import pandapower as pp
import gym
import pandas as pd
import numpy as np
import datetime
import json
import random
import networkx as nx
import matplotlib.pyplot as plt
from utils.data_process.data_read import csv2df
from utils.data_process.data_read import predict_class
from action_space import action_all
load_path = './Data/load_data/load_data.csv'
power1_path = './Data/power_data/merged_power_data1.csv'
power2_path='./Data/power_data/merged_power_data2.csv'
power3_path='./Data/power_data/merged_power_data3.csv'
power4_path='./Data/power_data/merged_power_data4.csv'
power_yaml_path = './utils/configs/power_forecasting/lstm_power_forecasting.yaml'
load_yaml_path = './utils/configs/load_forecasting/lstm_load_forecasting.yaml'
data_str = 'data2'

pd.options.mode.chained_assignment = None
bus_vn_kv = 12.66 # 各节点额定电压
line_simply = [0, 1, 2, 5, 7, 8, 11, 14, 17, 20, 21, 24, 28, 34, 32, 33, 36, 35] #简化后的线路（可控制开断的线路）
# 23个动作对应的实际动作，皆为可行的满足连通性和无环（辐射性）的拓扑结构


class PowerSystemEnv(gym.Env):
    
    def __init__(self):
        super(PowerSystemEnv, self).__init__()
        self.network = self.configure_power_network() # 创建自定义的电力系统网络
        self.time_flag = 0  # 时间标志
        self.action_last= [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        self.round = 0 
        self.rounf_max = 192 # 一天96个时间片，共2天
        # 读入负载数据集 
        self.load_data = csv2df(load_path)
        # 读入风电数据集
        self.power1_data = csv2df(power1_path)
        self.power2_data = csv2df(power2_path)
        self.power3_data = csv2df(power3_path)
        self.power4_data = csv2df(power4_path)

        self.wind_k = 0.04 # 风电功率系数，最大风电功率为100MW，实际单风机一般不超过6MW
        self.loss_k = 10 # 线路损耗奖励比例
        self.inverse_k = 5  # 逆馈信息奖励比例
        # 预测模型读入
        self.load_pre = predict_class(load_yaml_path, 'data1', load_path)
        self.power1_pre = predict_class(power_yaml_path, 'data1', power1_path)
        self.power2_pre = predict_class(power_yaml_path, 'data1', power2_path)
        self.power3_pre = predict_class(power_yaml_path, 'data1', power3_path)
        self.power4_pre = predict_class(power_yaml_path, 'data1', power4_path)
        # 实际的动作指令
        self.action_actually = action_all
        self.log = {
                "time_flag": [],
                "reward": [],
                "loss_kw": [],
                "load_sum_kw": [],
                "wind_power_kw": [],
                "inversely_kw": [],
                "num_switch_changes": [],
            }
        self.log_name = "unknow.json"
        self.printout = False
    # 重置电力系统环境
    def reset(self, sample_idx=None):

        if sample_idx is None:
            self.time_flag = random.randint(0,1000)
        else :
            self.time_flag = sample_idx
        # 初始化电网拓扑
        for i in range(0,32) :
            self.network.line.at[i,"in_service"] = True
        for j in range(32,37) :
            self.network.line.at[j,"in_service"] = False

        # 负载初始化
        for i in range(0,32) :
            self.network.load.at[i,"scaling"] = \
                self.load_data.get_data(point_step = self.time_flag, history_step = 0).values[0,i]
        # 风电初始化
        self.network.gen.at[0,"p_mw"] = self.wind_k*\
            self.power1_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        self.network.gen.at[1,"p_mw"] = self.wind_k*\
            self.power2_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        self.network.gen.at[2,"p_mw"] = self.wind_k*\
            self.power3_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        self.network.gen.at[3,"p_mw"] = self.wind_k*\
            self.power4_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        
        # 进行潮流计算
        pp.runpp(self.network,numba=False)              
        
        # 获取初始观测状态
        wind_power, load, losses, voltage, ext_grid = self.get_observation()
        load_pre, power_pre = self.get_predict_data()

        state = list(wind_power) + list(load) + list(losses) + list(voltage) + list(ext_grid) + list(load_pre) + list(power_pre)

        print("初始化成功！当前时刻为：")
        print(self.load_data.get_data(point_step = self.time_flag, history_step = 0).index[-1])
        
        return  np.array(state)

    # 执行动作
    def step(self, action):
    
        if action in range(0,100):  # 如果action在0到200之间
            for j in range(0, 18):
                 self.network.line.at[line_simply[j], "in_service"] = bool(self.action_actually[action][j])

        # 运行电网进行潮流计算    
        pp.runpp(self.network, numba=False, max_iteration=10)
        # 获取此时的电网状态，计算奖励
        wind_power, load, losses, voltage, ext_grid = self.get_observation()
        reward, reward_3 = self.compute_reward(losses, voltage, self.action_actually[action],ext_grid) # 这里输入单位均为mw级
        # print("执行动作的奖励: \n",reward,"\n")

        if self.printout:
            time_flag = self.load_data.get_data(point_step = self.time_flag, history_step = 0).index[-1].isoformat()
            loss_kw = 1000 * self.sum_losses(losses) # 线路损耗功率 kw
            load_sum_kw = 1000 * self.network.res_load['p_mw'].sum() # 负载功率 kw
            wind_power_kw = 1000 * self.network.res_gen['p_mw'].sum() # 风电功率 kw
            inversely_kw = 1000 * self.network.res_ext_grid['p_mw'].sum()
            if inversely_kw > 0:
                inversely_kw = 0

            self.log["time_flag"].append(time_flag)  
            self.log["reward"].append(reward)
            self.log["loss_kw"].append(loss_kw)
            self.log["load_sum_kw"].append(load_sum_kw)
            self.log["wind_power_kw"].append(wind_power_kw)
            self.log["inversely_kw"].append(inversely_kw)
            self.log["num_switch_changes"].append(reward_3)
            with open(self.log_name, 'w') as f:
                json.dump(self.log, f, indent=4)
        # 判断本次训练是否结束
        self.round += 1

        if self.round < self.rounf_max:
            done = True
        else:
            done = False
            self.round = 0

        # 更新self.action_last和时间参考标志
        self.action_last = self.action_actually[action]
        self.time_flag = self.time_flag + 1 
        
        # # 更新负载参数
        # for i in range(0,32) :
        #     self.network.load.at[i,"scaling"] = self.load_data[self.time_flag, i+1]
        # # 更新发电机参数
        # for j in range(0,4) :
        #     self.network.gen.at[j,"p_mw"] = self.wind_k*self.power_data[self.time_flag, j+1] 
        
        # 更新负载参数
        for i in range(0,32) :
            self.network.load.at[i,"scaling"] = \
                self.load_data.get_data(point_step = self.time_flag, history_step = 0).values[0,i]
        # 更新发电机参数
        self.network.gen.at[0,"p_mw"] = self.wind_k*\
            self.power1_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        self.network.gen.at[1,"p_mw"] = self.wind_k*\
            self.power2_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        self.network.gen.at[2,"p_mw"] = self.wind_k*\
            self.power3_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        self.network.gen.at[3,"p_mw"] = self.wind_k*\
            self.power4_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        
        # 运行电网进行潮流计算
        pp.runpp(self.network,numba=False)
        wind_power, load, losses, voltage, ext_grid  = self.get_observation()
        load_pre, power_pre = self.get_predict_data()
        next_state = list(wind_power) + list(load) + list(losses) + list(voltage) + list(ext_grid) + list(load_pre) + list(power_pre)

        # if ext_grid < 0:
        #     info = ext_grid[0] * 1000 # 倒送功率 kw
        # else:
        #     info = 0 
        info  = {} 
        return np.array(next_state), reward, done, info
    
    
    # 获取观测状态
    def get_observation(self):
        wind_power1 = self.power1_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        wind_power2 = self.power2_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        wind_power3 = self.power3_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        wind_power4 = self.power4_data.get_data(point_step = self.time_flag, history_step = 0).loc[:,'power'].values[0]
        wind_power = [wind_power1, wind_power2, wind_power3, wind_power4]
        load = self.load_data.get_data(point_step = self.time_flag, history_step = 0).values[0]
        losses = self.network.res_line['pl_mw'].values
        voltage = self.network.res_bus['vm_pu'].values
        ext_grid = self.network.res_ext_grid['p_mw'].values
        return  wind_power, load, losses, voltage, ext_grid
    # 获取预测数据git 
    def get_predict_data(self):
        load = self.load_pre.predict(point_step = self.time_flag).flatten().tolist()
        power1 = self.power1_pre.predict(point_step = self.time_flag).flatten().tolist()
        power2 = self.power2_pre.predict(point_step = self.time_flag).flatten().tolist()
        power3 = self.power3_pre.predict(point_step = self.time_flag).flatten().tolist()
        power4 = self.power4_pre.predict(point_step = self.time_flag).flatten().tolist()
        power = power1 + power2 + power3 + power4
        return load, power

    # 获取网损
    def get_losses(self):
        loss_kw = 1000 * self.network.res_line['pl_mw'].sum() # 线路损耗功率 kw
        losses_sum = loss_kw * 0.25  # 15分钟的电力损耗 kwh
        return loss_kw , losses_sum
    
    # 计算奖励。奖励函数包括四个部分：1.线路损耗；2.节点电压稳定；3.动作惩罚；4.环状网络惩罚 5.倒送功率惩罚
    def compute_reward(self, losses, voltage, action, ext_grid):
        # reward_1 line上的损耗
        loss_sum = self.sum_losses(losses) 
        reward_1 = -loss_sum #线路损耗的惩罚项 
        # print("reward_1:",reward_1)
        
        # reward_2 节点电压的稳定 GB：用户供电电压的允许偏移对于35 kV 及以上电压级为额定值的±5 % ，
        # 对于10 kV 及以下电压级为额定值的±7%
        reward_2 = 0
        number_stable = self.voltage_stabilise(voltage) # 稳定节点的个数，0-33
        # 不稳定项作为惩罚项
        reward_2 = number_stable - 33
            # print("reward_2:",reward_2)
        
        # reward_3 difference between action and action_last
        reward_3 = 0
        for i in range(0,len(action)):
            if action[i] != self.action_last[i] :
                reward_3 -= 1 # 开关动作的惩罚项
        # print("reward_3:",reward_3)
        
        # reward_4
        # 将多图转换为普通图
        Graph = nx.Graph(pp.topology.create_nxgraph(self.network))
        # 检查是否存在环状网络
        has_loops = nx.cycle_basis(Graph)
        # 打印结果
        if has_loops:
            reward_4 = -10000
            print("存在环状网络") 
        else :
            reward_4 = 0
        # print("reward_4:",reward_4)

        reward_5 = 0
        if ext_grid[0] < 0:
            reward_5 = ext_grid[0] # 倒送功率的惩罚项
        #  print("reward_5:",reward_5)
        reward = self.loss_k * reward_1 + reward_2 + reward_3 + reward_4 + self.inverse_k * reward_5
        return reward,reward_3
    # 计算网损的总和
    def sum_losses(self, losses):
        sum = 0
        for i in range(0,len(losses)):
            sum = sum + losses[i]
        return sum
    # 计算稳定节点的数目
    def voltage_stabilise(self,voltages):
        target_range=(0.95, 1.05)
        counts = 0
        for v in voltages:
            if v >= target_range[0] and v <= target_range[1]:  # 电压在目标范围内
                counts += 1
        return counts
    
    def print_time(self, time_flag):
        base_time = datetime.datetime(2019, 1, 1, 0, 0)
        delta = datetime.timedelta(minutes=15)
        days_to_add = time_flag // 96  # 96个15分钟为一天
        current_time = base_time + datetime.timedelta(days=days_to_add)
        minutes_to_add = time_flag % 96  # 96个15分钟
        current_time += datetime.timedelta(minutes=15 * minutes_to_add)
        print(current_time.strftime("%Y/%m/%d %H:%M"))

    # 配置电力系统网络
    def configure_power_network(self) :
        # 创建一个空网络
        net = pp.create_empty_network() 
        # 添加bus
        bus0 = pp.create_bus(net, name="0", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.0, min_vm_pu=1.0)
        bus1 = pp.create_bus(net, name="1", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus2 = pp.create_bus(net, name="2", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus3 = pp.create_bus(net, name="3", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus4 = pp.create_bus(net, name="4", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus5 = pp.create_bus(net, name="5", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus6 = pp.create_bus(net, name="6", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus7 = pp.create_bus(net, name="7", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus8 = pp.create_bus(net, name="8", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus9 = pp.create_bus(net, name="9", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus10= pp.create_bus(net, name="10", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus11= pp.create_bus(net, name="11", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus12= pp.create_bus(net, name="12", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus13= pp.create_bus(net, name="13", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus14= pp.create_bus(net, name="14", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus15= pp.create_bus(net, name="15", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus16= pp.create_bus(net, name="16", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus17= pp.create_bus(net, name="17", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus18= pp.create_bus(net, name="18", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus19= pp.create_bus(net, name="19", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus20= pp.create_bus(net, name="20", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus21= pp.create_bus(net, name="21", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus22= pp.create_bus(net, name="22", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus23= pp.create_bus(net, name="23", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus24= pp.create_bus(net, name="24", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus25= pp.create_bus(net, name="25", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus26= pp.create_bus(net, name="26", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus27= pp.create_bus(net, name="27", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus28= pp.create_bus(net, name="28", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus29= pp.create_bus(net, name="29", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus30= pp.create_bus(net, name="30", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus31= pp.create_bus(net, name="31", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        bus32= pp.create_bus(net, name="32", vn_kv=bus_vn_kv, type="b", max_vm_pu=1.1, min_vm_pu=0.9)
        # 添加外部网络
        pp.create_ext_grid(net, name="ext_grid",bus=bus0, vm_pu = 1.0, va_degree=0, slack_weight=1.0, max_p_mw=10.0, min_p_mw=0, max_q_mvar=10.0, min_q_mvar=-10.0)
        # 添加line
        line0 = pp.create_line_from_parameters(net, from_bus=0,  to_bus=1,  length_km=1.0, r_ohm_per_km=0.0922, x_ohm_per_km=0.0470, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line1 = pp.create_line_from_parameters(net, from_bus=1,  to_bus=2,  length_km=1.0, r_ohm_per_km=0.4930, x_ohm_per_km=0.2511, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line2 = pp.create_line_from_parameters(net, from_bus=2,  to_bus=3,  length_km=1.0, r_ohm_per_km=0.3660, x_ohm_per_km=0.1864, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line3 = pp.create_line_from_parameters(net, from_bus=3,  to_bus=4,  length_km=1.0, r_ohm_per_km=0.3811, x_ohm_per_km=0.1941, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line4 = pp.create_line_from_parameters(net, from_bus=4,  to_bus=5,  length_km=1.0, r_ohm_per_km=0.8190, x_ohm_per_km=0.7070, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line5 = pp.create_line_from_parameters(net, from_bus=5,  to_bus=6,  length_km=1.0, r_ohm_per_km=0.1872, x_ohm_per_km=0.6188, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line6 = pp.create_line_from_parameters(net, from_bus=6,  to_bus=7,  length_km=1.0, r_ohm_per_km=0.7114, x_ohm_per_km=0.2351, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line7 = pp.create_line_from_parameters(net, from_bus=7,  to_bus=8,  length_km=1.0, r_ohm_per_km=1.0300, x_ohm_per_km=0.7400, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line8 = pp.create_line_from_parameters(net, from_bus=8,  to_bus=9,  length_km=1.0, r_ohm_per_km=1.0440, x_ohm_per_km=0.7400, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line9 = pp.create_line_from_parameters(net, from_bus=9,  to_bus=10, length_km=1.0, r_ohm_per_km=0.1966, x_ohm_per_km=0.0650, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)      
        line10= pp.create_line_from_parameters(net, from_bus=10, to_bus=11, length_km=1.0, r_ohm_per_km=0.3744, x_ohm_per_km=0.1238, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line11= pp.create_line_from_parameters(net, from_bus=11, to_bus=12, length_km=1.0, r_ohm_per_km=1.4680, x_ohm_per_km=1.1550, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line12= pp.create_line_from_parameters(net, from_bus=12, to_bus=13, length_km=1.0, r_ohm_per_km=0.5416, x_ohm_per_km=0.7219, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line13= pp.create_line_from_parameters(net, from_bus=13, to_bus=14, length_km=1.0, r_ohm_per_km=0.5910, x_ohm_per_km=0.5260, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line14= pp.create_line_from_parameters(net, from_bus=14, to_bus=15, length_km=1.0, r_ohm_per_km=0.7463, x_ohm_per_km=0.5450, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line15= pp.create_line_from_parameters(net, from_bus=15, to_bus=16, length_km=1.0, r_ohm_per_km=1.2890, x_ohm_per_km=1.7210, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line16= pp.create_line_from_parameters(net, from_bus=16, to_bus=17, length_km=1.0, r_ohm_per_km=0.7320, x_ohm_per_km=0.5740, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line17= pp.create_line_from_parameters(net, from_bus=1 , to_bus=18, length_km=1.0, r_ohm_per_km=0.1640, x_ohm_per_km=0.1565, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line18= pp.create_line_from_parameters(net, from_bus=18, to_bus=19, length_km=1.0, r_ohm_per_km=1.5042, x_ohm_per_km=1.3554, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line19= pp.create_line_from_parameters(net, from_bus=19, to_bus=20, length_km=1.0, r_ohm_per_km=0.4095, x_ohm_per_km=0.4784, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line20= pp.create_line_from_parameters(net, from_bus=20, to_bus=21, length_km=1.0, r_ohm_per_km=0.7089, x_ohm_per_km=0.9373, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)      
        line21= pp.create_line_from_parameters(net, from_bus=2 , to_bus=22, length_km=1.0, r_ohm_per_km=0.4512, x_ohm_per_km=0.3083, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line22= pp.create_line_from_parameters(net, from_bus=22, to_bus=23, length_km=1.0, r_ohm_per_km=0.8980, x_ohm_per_km=0.7091, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line23= pp.create_line_from_parameters(net, from_bus=23, to_bus=24, length_km=1.0, r_ohm_per_km=0.8960, x_ohm_per_km=0.7011, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line24= pp.create_line_from_parameters(net, from_bus=5 , to_bus=25, length_km=1.0, r_ohm_per_km=0.2030, x_ohm_per_km=0.1034, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line25= pp.create_line_from_parameters(net, from_bus=25, to_bus=26, length_km=1.0, r_ohm_per_km=0.2842, x_ohm_per_km=0.1447, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line26= pp.create_line_from_parameters(net, from_bus=26, to_bus=27, length_km=1.0, r_ohm_per_km=1.0590, x_ohm_per_km=0.9337, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line27= pp.create_line_from_parameters(net, from_bus=27, to_bus=28, length_km=1.0, r_ohm_per_km=0.8042, x_ohm_per_km=0.7006, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line28= pp.create_line_from_parameters(net, from_bus=28, to_bus=29, length_km=1.0, r_ohm_per_km=0.5075, x_ohm_per_km=0.2585, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line29= pp.create_line_from_parameters(net, from_bus=29, to_bus=30, length_km=1.0, r_ohm_per_km=0.9744, x_ohm_per_km=0.9630, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line30= pp.create_line_from_parameters(net, from_bus=30, to_bus=31, length_km=1.0, r_ohm_per_km=0.3105, x_ohm_per_km=0.3619, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line31= pp.create_line_from_parameters(net, from_bus=31, to_bus=32, length_km=1.0, r_ohm_per_km=0.3410, x_ohm_per_km=0.5302, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line32= pp.create_line_from_parameters(net, from_bus=20, to_bus=7 , length_km=1.0, r_ohm_per_km=2.0000, x_ohm_per_km=2.0000, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line33= pp.create_line_from_parameters(net, from_bus=8 , to_bus=14, length_km=1.0, r_ohm_per_km=2.0000, x_ohm_per_km=2.0000, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line34= pp.create_line_from_parameters(net, from_bus=11, to_bus=21, length_km=1.0, r_ohm_per_km=2.0000, x_ohm_per_km=2.0000, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line35= pp.create_line_from_parameters(net, from_bus=17, to_bus=32, length_km=1.0, r_ohm_per_km=0.5000, x_ohm_per_km=0.5000, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        line36= pp.create_line_from_parameters(net, from_bus=24, to_bus=28, length_km=1.0, r_ohm_per_km=0.5000, x_ohm_per_km=0.5000, c_nf_per_km=0, max_i_ka=99999.0, type="ol", in_service=True, df=1.0, parallel=1, g_us_per_km=0.0, max_loading_percent=100.0)
        # 添加每根线的线路开关switch
        pp.create_switch(net, bus=0, element=line0, et="l", closed=True)
        pp.create_switch(net, bus=1, element=line1, et="l", closed=True)
        pp.create_switch(net, bus=2, element=line2, et="l", closed=True)
        pp.create_switch(net, bus=3, element=line3, et="l", closed=True)
        pp.create_switch(net, bus=4, element=line4, et="l", closed=True)
        pp.create_switch(net, bus=5, element=line5, et="l", closed=True)
        pp.create_switch(net, bus=6, element=line6, et="l", closed=True)
        pp.create_switch(net, bus=7, element=line7, et="l", closed=True)
        pp.create_switch(net, bus=8, element=line8, et="l", closed=True)
        pp.create_switch(net, bus=9, element=line9, et="l", closed=True)
        pp.create_switch(net, bus=10, element=line10, et="l", closed=True)
        pp.create_switch(net, bus=11, element=line11, et="l", closed=True)
        pp.create_switch(net, bus=12, element=line12, et="l", closed=True)
        pp.create_switch(net, bus=13, element=line13, et="l", closed=True)
        pp.create_switch(net, bus=14, element=line14, et="l", closed=True)
        pp.create_switch(net, bus=15, element=line15, et="l", closed=True)
        pp.create_switch(net, bus=16, element=line16, et="l", closed=True)
        pp.create_switch(net, bus=1, element=line17, et="l", closed=True)
        pp.create_switch(net, bus=18, element=line18, et="l", closed=True)
        pp.create_switch(net, bus=19, element=line19, et="l", closed=True)
        pp.create_switch(net, bus=20, element=line20, et="l", closed=True)
        pp.create_switch(net, bus=2, element=line21, et="l", closed=True)
        pp.create_switch(net, bus=22, element=line22, et="l", closed=True)
        pp.create_switch(net, bus=23, element=line23, et="l", closed=True)
        pp.create_switch(net, bus=5, element=line24, et="l", closed=True)
        pp.create_switch(net, bus=25, element=line25, et="l", closed=True)
        pp.create_switch(net, bus=26, element=line26, et="l", closed=True)
        pp.create_switch(net, bus=27, element=line27, et="l", closed=True)
        pp.create_switch(net, bus=28, element=line28, et="l", closed=True)
        pp.create_switch(net, bus=29, element=line29, et="l", closed=True)
        pp.create_switch(net, bus=30, element=line30, et="l", closed=True)
        pp.create_switch(net, bus=31, element=line31, et="l", closed=True)
        pp.create_switch(net, bus=20, element=line32, et="l", closed=True)
        pp.create_switch(net, bus=8, element=line33, et="l", closed=True)
        pp.create_switch(net, bus=11, element=line34, et="l", closed=True)
        pp.create_switch(net, bus=17, element=line35, et="l", closed=True)
        pp.create_switch(net, bus=24, element=line36, et="l", closed=True)

        # 添加负荷
        load1 = pp.create_load(net,bus=bus1, p_mw=0.100, q_mvar=0.060, in_service=True)
        load2 = pp.create_load(net,bus=bus2, p_mw=0.090, q_mvar=0.040, in_service=True)
        load3 = pp.create_load(net,bus=bus3, p_mw=0.120, q_mvar=0.080, in_service=True)
        load4 = pp.create_load(net,bus=bus4, p_mw=0.060, q_mvar=0.030, in_service=True)
        load5 = pp.create_load(net,bus=bus5, p_mw=0.060, q_mvar=0.020, in_service=True)
        load6 = pp.create_load(net,bus=bus6, p_mw=0.200, q_mvar=0.100, in_service=True)
        load7 = pp.create_load(net,bus=bus7, p_mw=0.200, q_mvar=0.100, in_service=True)
        load8 = pp.create_load(net,bus=bus8, p_mw=0.060, q_mvar=0.020, in_service=True)
        load9 = pp.create_load(net,bus=bus9, p_mw=0.060, q_mvar=0.020, in_service=True)
        load10= pp.create_load(net,bus=bus10, p_mw=0.045, q_mvar=0.030, in_service=True)
        load11= pp.create_load(net,bus=bus11, p_mw=0.060, q_mvar=0.035, in_service=True)
        load12= pp.create_load(net,bus=bus12, p_mw=0.060, q_mvar=0.035, in_service=True)
        load13= pp.create_load(net,bus=bus13, p_mw=0.120, q_mvar=0.080, in_service=True)
        load14= pp.create_load(net,bus=bus14, p_mw=0.060, q_mvar=0.010, in_service=True)
        load15= pp.create_load(net,bus=bus15, p_mw=0.060, q_mvar=0.020, in_service=True)
        load16= pp.create_load(net,bus=bus16, p_mw=0.060, q_mvar=0.020, in_service=True)
        load17= pp.create_load(net,bus=bus17, p_mw=0.090, q_mvar=0.040, in_service=True)
        load18= pp.create_load(net,bus=bus18, p_mw=0.090, q_mvar=0.040, in_service=True)
        load19= pp.create_load(net,bus=bus19, p_mw=0.090, q_mvar=0.040, in_service=True)
        load20= pp.create_load(net,bus=bus20, p_mw=0.090, q_mvar=0.040, in_service=True)
        load21= pp.create_load(net,bus=bus21, p_mw=0.090, q_mvar=0.040, in_service=True)
        load22= pp.create_load(net,bus=bus22, p_mw=0.090, q_mvar=0.050, in_service=True)
        load23= pp.create_load(net,bus=bus23, p_mw=0.420, q_mvar=0.200, in_service=True)
        load24= pp.create_load(net,bus=bus24, p_mw=0.420, q_mvar=0.200, in_service=True)
        load25= pp.create_load(net,bus=bus25, p_mw=0.060, q_mvar=0.025, in_service=True)
        load26= pp.create_load(net,bus=bus26, p_mw=0.060, q_mvar=0.025, in_service=True)
        load27= pp.create_load(net,bus=bus27, p_mw=0.060, q_mvar=0.020, in_service=True)
        load28= pp.create_load(net,bus=bus28, p_mw=0.120, q_mvar=0.070, in_service=True)
        load29= pp.create_load(net,bus=bus29, p_mw=0.200, q_mvar=0.600, in_service=True)
        load30= pp.create_load(net,bus=bus30, p_mw=0.150, q_mvar=0.070, in_service=True)
        load31= pp.create_load(net,bus=bus31, p_mw=0.210, q_mvar=0.100, in_service=True)
        load32= pp.create_load(net,bus=bus32, p_mw=0.060, q_mvar=0.040, in_service=True)
        # 添加风力发电机来模拟风力发电
        wind_1 = pp.create_gen(net, bus10, p_mw=0.1,  name="wind_power1")
        wind_2 = pp.create_gen(net, bus16, p_mw=0.1,  name="wind_power2")
        wind_3 = pp.create_gen(net, bus25, p_mw=0.1,  name="wind_power3")
        wind_4 = pp.create_gen(net, bus31, p_mw=0.1,  name="wind_power4")


        return net
        # 更新电力系统，用于PSO对比脚本
    
    def update_powersystem(self,open_line,last_open_line):
        
        # # 执行open_line,改变拓扑结构
        # netork = copy.deepcopy(self.network)
        self.network.switch.closed = True  #全部线路开关处于闭合
        for i in open_line:
            self.network.switch.loc[i,'closed'] = False 

        pp.runpp(self.network, numba=False, max_iteration=10)

        reward_1 = 0
        loss = self.network.res_line["pl_mw"].sum()
        reward_1 = -loss
        reward_2 = 0
        voltage = self.network.res_bus['vm_pu'].values
        print(self.network.res_bus)
        target_range=(0.95, 1.05)
        counts = 0
        for v in voltage:
            if v >= target_range[0] and v <= target_range[1]:  # 电压在目标范围内
                counts += 1
        reward_2 = counts - 33
        reward_3 = 0
        for i in range(len(open_line)):
            if open_line[i] != last_open_line[i]:
                reward_3 -= 2
        reward_4 = 0
        ext_grid = self.network.res_ext_grid['p_mw'].sum()
        if ext_grid < 0:
            reward_4 -= ext_grid
        else:
            reward_4 = 0
        reward = 10 * reward_1 + reward_2 + reward_3 + 5 * reward_4
        
        if self.printout:
            time_flag = self.load_data[self.time_flag, 0]
            loss_kw = 1000 * self.network.res_line['pl_mw'].sum() # 线路损耗功率 kw
            load_sum_kw = 1000 * self.network.res_load['p_mw'].sum() # 负载功率 kw
            wind_power_kw = 1000 * self.network.res_gen['p_mw'].sum() # 风电功率 kw
            inversely_kw = 1000 * self.network.res_ext_grid['p_mw'].sum()
            if inversely_kw > 0:
                inversely_kw = 0
            self.log["time_flag"].append(time_flag)  
            self.log["reward"].append(reward)
            self.log["loss_kw"].append(loss_kw)
            self.log["load_sum_kw"].append(load_sum_kw)
            self.log["wind_power_kw"].append(wind_power_kw)
            self.log["inversely_kw"].append(inversely_kw)
            self.log["num_switch_changes"].append(reward_3)
            with open(self.log_name, 'w') as f:
                json.dump(self.log, f, indent=4)
        
        self.time_flag = self.time_flag + 1 
        # 更新负载参数
        for i in range(0,32) :
            self.network.load.at[i,"scaling"] = self.load_data[self.time_flag, i+1]
        # 更新发电机参数
        for j in range(0,4) :
            self.network.gen.at[j,"p_mw"] = self.wind_k*self.power_data[self.time_flag, j+1] 

        return self.network, reward
if __name__ == "__main__":
    env = PowerSystemEnv()
    state = env.reset()
    print(state)