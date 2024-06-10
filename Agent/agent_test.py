from textwrap import indent
from Power_Grid_Virtual_Environment.TrainEnv import TrainEnv
import numpy as np
import time 
import json
from PPOAgent import PPOAgent


iterations = 96

np.random.seed(17) #设置随机种子
env = TrainEnv()  # 创建环境
env.env.printout = True
env.env.log_name = "agent_test.json"
agent = PPOAgent('EEEIC_agent.zip')
sample_idx = np.random.randint(0, 15000) 
obs = env.reset(sample_idx=sample_idx)

ep_reward = 0 # 累计奖励
loss_sum = 0 # 电力累计损失 kwh
inversely_feeding = 0 # 逆馈信息
last_action = 0  
num_switch_changes = 0 # 线路开关操作次数
last_action_actually = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

for i in range(iterations):


    action = agent.act(obs)
    obs, reward, done, info = env.step(action)

    