import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from Power_Grid_Virtual_Environment.TrainEnv import TrainEnv
import torch
import yaml

config_path = './utils/configs/agent/ppo_agent.yaml'
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def make_env(seed=0):
    """
    Utility function for multiprocessed env.
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = TrainEnv()
        return env
    return _init


def agent_train(train_sample):
    num_cpu = config['train']['num_workers'] # 多进程数量
    n_steps = config['train']['n_steps']
    env = SubprocVecEnv([make_env() for _ in range(num_cpu)]) # 创建多进程环境
    tensorboard_log = config['tensorboard_save']['tensorboard_train_dir'] # tensorboard日志文件的绝对路径,TensorBoard是一个可视化工具，用于展示模型训练过程中的各种指标。
    policy_kwargs = dict(activation_fn=torch.nn.Tanh, net_arch=dict(pi=[256, 256], vf=[256, 256])) # 包含了神经网络的激活函数和网络结构。
    # 激活函数是torch.nn.Tanh，网络结构是一个列表，包含一个字典，该字典定义了策略网络（pi）和价值网络（vf）的隐藏层结构，都是两个256节点的隐藏层。
    model = PPO("MlpPolicy", env, policy_kwargs = policy_kwargs, learning_rate= config['train']['learning_rate'], verbose = 1, batch_size= n_steps * num_cpu , n_steps = n_steps, n_epochs = config['train']['n_epochs'], gamma = config['train']['gamma'], tensorboard_log = tensorboard_log)
    model.learn(total_timesteps = train_sample)
    model.save("./Agent/EEEIC_agent")


if __name__ == "__main__":
    start_time = time.time()
    agent_train(config['train']['train_sample'])
    end_time = time.time()
    print('训练耗时:', end_time - start_time)



