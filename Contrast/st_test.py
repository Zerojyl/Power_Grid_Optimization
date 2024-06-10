from textwrap import indent
from Power_Grid_Virtual_Environment.TrainEnv import TrainEnv
import numpy as np
import time 
import pandapower as pp
import copy
import json

iterations = 288

np.random.seed(17) #设置随机种子
env = TrainEnv()  # 创建环境
env.env.printout = True
env.env.log_name = "st_test.json"
sample_idx = np.random.randint(0, 15000) 
obs = env.reset(sample_idx=sample_idx)

ep_reward = 0 # 累计奖励
loss_sum = 0 # 电力累计损失 kwh
inversely_feeding = 0 # 逆馈信息
last_action = 0  
num_switch_changes = 0 # 线路开关操作次数

for i in range(iterations):

    action = 0 
    obs, reward, done, info = env.step(action)
    
  
