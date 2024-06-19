import numpy as np
from Power_Grid_Virtual_Environment.PowerSystem import PowerSystemEnv
import gym
import yaml

config_path = './utils/configs/environment/env.yaml'
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

class TrainEnv(gym.Env):
    def __init__(self):
        self.env = PowerSystemEnv()
        self.action_space = gym.spaces.Discrete(config['action_range'])
        self.observation_space = gym.spaces.Box(low=-50, high=50, shape=(323,), dtype=np.float32)
    
    def reset(self, sample_idx=None):

        if sample_idx is None:
            obs = self.env.reset()
        else:
            obs = self.env.reset(sample_idx=sample_idx)
        return obs
    
    def step(self, action):

        # print('action:', action)
        next_obs, reward, done, info = self.env.step(action)
        
        return next_obs, reward, done, info