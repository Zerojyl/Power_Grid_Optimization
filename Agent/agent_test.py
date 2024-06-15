from textwrap import indent
from Power_Grid_Virtual_Environment.TrainEnv import TrainEnv
import numpy as np
import time 
import json
from PPOAgent import PPOAgent


iterations = 600


np.random.seed(0) #设置随机种子
env = TrainEnv()  # 创建环境
env.env.printout = True
env.env.is_display = True
env.env.log_name = './results/agent_test.json'
agent = PPOAgent('./Agent/EEEIC_agent.zip')
sample_idx = np.random.randint(0, 10000) 
obs = env.reset(sample_idx=sample_idx)


for i in range(iterations):

    action = agent.act(obs)
    obs, reward, done, info = env.step(action)

    