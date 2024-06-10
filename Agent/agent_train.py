import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from Power_Grid_Virtual_Environment.TrainEnv import TrainEnv
import torch
print(torch.cuda.is_available())
import os
tensorboard_log_dir = os.path.abspath('./tensorboard_log')
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
    num_cpu = 4 # 多进程数量
    env = SubprocVecEnv([make_env() for _ in range(num_cpu)]) # 创建多进程环境
    tensorboard_log = tensorboard_log_dir # tensorboard日志文件的绝对路径,TensorBoard是一个可视化工具，用于展示模型训练过程中的各种指标。
    policy_kwargs = dict(activation_fn=torch.nn.Tanh, net_arch=dict(pi=[256, 256], vf=[256, 256])) # 包含了神经网络的激活函数和网络结构。
    # 激活函数是torch.nn.Tanh，网络结构是一个列表，包含一个字典，该字典定义了策略网络（pi）和价值网络（vf）的隐藏层结构，都是两个256节点的隐藏层。
    model = PPO("MlpPolicy", env, policy_kwargs = policy_kwargs, learning_rate= 0.0007, verbose = 1, batch_size= 768, n_steps = 64, n_epochs = 20, gamma = 0.92, tensorboard_log = tensorboard_log)
    model.learn(total_timesteps = train_sample)
    model.save("EEEIC_agent")


if __name__ == "__main__":
    start_time = time.time()
    agent_train(50000)
    end_time = time.time()
    print('训练耗时:', end_time - start_time)



