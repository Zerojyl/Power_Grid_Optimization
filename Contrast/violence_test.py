from Power_Grid_Virtual_Environment.PowerSystem import PowerSystemEnv
import numpy as np
import time
import yaml

config_path = './utils/configs/environment/env.yaml'
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

iterations = 288

np.random.seed(0) #设置随机种子
env = PowerSystemEnv() # 创建环境
env.log_name = "./results/violence_test.json"
sample_idx = np.random.randint(0, 10000) 
env.reset(sample_idx=sample_idx)
for i in range(iterations):
    start = time.time()
    best_action = 500
    max_reward = -100000
    for action in range(0, config['action_range']):
        reward, _, _ =env.st_step(action=action)
        if reward > max_reward:
            max_reward = reward
            best_action = action
    end = time.time()
    print("Time: ", end-start)
    env.st_step(action = best_action, is_best=True)
