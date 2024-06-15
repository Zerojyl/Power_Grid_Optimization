from textwrap import indent
from Power_Grid_Virtual_Environment.TrainEnv import TrainEnv
import numpy as np
import time 
import pandapower as pp
import copy
import json


iterations = 288
np.random.seed(0) #设置随机种子
env = TrainEnv()  # 创建环境
env.env.printout = False
env.env.is_display = True
env.env.log_name = "./results/st_test.json"
sample_idx = np.random.randint(0, 10000) 
obs = env.reset(sample_idx=sample_idx)


for i in range(iterations):

    action = 0
    obs, reward, done, info = env.step(action)
    
  
