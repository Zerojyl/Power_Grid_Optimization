
import pandapower as pp
import gym
import pandas as pd
import numpy as np
import datetime
import csv
import random
import networkx as nx
import matplotlib.pyplot as plt
import time
bus_vn_kv = 12.66 # 各节点额定电压

class PowerSystemEnv():
    def __init__(self):
        self.network = self.configure_power_network() # 创建自定义的电力系统网络
        self.time_flag = 0  # 时间标志
        # 读入负载数据集    
        data = pd.read_csv('./data/load_data.csv',encoding='GBK')
        load_columns = ['时间'] + ['负载{}'.format(i) for i in range(1, 33)]
        data.columns = load_columns
        self.load_data  = data.to_numpy()
        # 读入风电数据集
        data_wind_power = pd.read_csv('./data/power_data.csv',encoding='GBK')
        wind_power_columns = ['时间'] + ['风电{}'.format(i) for i in range(1, 5)]
        data_wind_power.columns = wind_power_columns
        self.power_data = data_wind_power.to_numpy()
        self.wind_k = 0.04 # 风电功率系数，最大风电功率为100MW，实际单风机一般不超过6MW

    # 重置电力系统环境
    def reset(self, sample_idx=None):

        if sample_idx is None:
            self.time_flag = random.randint(0,10000)
        else :
            self.time_flag = sample_idx

        # 初始化电网拓扑
        for i in range(0,32) :
            self.network.switch.loc[i, 'closed'] = True  # 关闭开关
        for j in range(32,37) :
            self.network.switch.at[j, 'closed'] = False # 打开开关
        
        # 负载初始化
        for i in range(0,32) :
            self.network.load.at[i,"scaling"] = self.load_data[self.time_flag, i+1]
        # 风电初始化
        for j in range(0,4) :
            self.network.gen.at[j,"p_mw"] = self.wind_k*self.power_data[self.time_flag, j+1]
        print("初始化成功！当前时间为：")    
        self.print_time(self.time_flag)

        return  self.network

    # 执行动作
    def update_powersystem(self):

        self.time_flag = self.time_flag + 1 
        # 更新负载参数
        for i in range(0,32) :
            self.network.load.at[i,"scaling"] = self.load_data[self.time_flag, i+1]
        # 更新发电机参数
        for j in range(0,4) :
            self.network.gen.at[j,"p_mw"] = self.wind_k*self.power_data[self.time_flag, j+1] 

        print("当前时间为：")
        self.print_time(self.time_flag)
        return self.network

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