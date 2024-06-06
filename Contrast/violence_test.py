from tracemalloc import start
from modified_IEEE33bus_powersystem import PowerSystemEnv
from PSO_main import build_case33
from PSO_main import Liqun
import pandapower as pp
import numpy as np
import copy
import json
import itertools
import time

switchcycle = [[7, 20, 32, 11, 34, 10, 9, 8, 33],
             [31, 30, 29, 28, 36, 23, 22, 2, 21, 1, 17, 18, 19, 20, 32, 11, 34, 10, 9, 8, 33, 14, 15, 16, 35],
             [7, 6, 5, 24, 25, 26, 27, 28, 36, 23, 22, 2, 21, 1, 17, 18, 19, 20, 32],
             [3, 4, 5, 24, 25, 26, 27, 28, 36, 23, 22, 2, 21],
             [13, 12, 11, 34, 10, 9, 8, 33, 14]]
def all_actions(switchcycle):
    """
    生成所有可能的动作
    :return: 所有可能的动作
    """
    # 使用itertools.product生成所有可能的组合
    all_combinations = list(itertools.product(*switchcycle))

    # 过滤掉包含重复元素的组合
    all_actions = [action for action in all_combinations if len(set(action)) == len(action)]

    return all_actions

def voltage_stabilise(voltages):
    target_range=(0.95, 1.05)
    counts = 0
    for v in voltages:
        if v >= target_range[0] and v <= target_range[1]:  # 电压在目标范围内
            counts += 1
    return counts

action_space = all_actions(switchcycle)

log = {
    "time_flag": [],
    "reward": [],
    "loss_kw": [],
    "load_sum_kw": [],
    "wind_power_kw": [],
    "inversely_kw": [],
    "num_switch_changes": []
      }

np.random.seed(17)
iterations = 16
env = PowerSystemEnv()
sample_idx = np.random.randint(0, 15000) 
env_network = env.reset(sample_idx=sample_idx)


network = copy.deepcopy(env_network)
best_action = action_space[0]
min_loss = 1e9
start = time.time()
i = 0
for action in action_space:
    i += 1
    net = build_case33(network,opennum = action) 
    pp.runpp(net,numba = False) # 潮流计算
    loss = net.res_line["pl_mw"].sum()
    voltage = net.res_bus['vm_pu'].values
    stabilise = voltage_stabilise(voltage)
    if loss < min_loss and stabilise == 33:
        min_loss = loss
        best_action = action
    print('第', i, '次迭代')
print('最小损失:', min_loss)
print('最佳动作:', best_action)
end = time.time()
print('耗时:', end - start)


# pp.runpp(net,numba = False)#潮流计算
# time_flag = env.load_data[env.time_flag,0]
# loss_kw = 1000*net.res_line["pl_mw"].sum() # 线路损耗 kw
# load_sum_kw = 1000*net.res_load["p_mw"].sum() # 负荷总和 kw
# wind_power_kw = 1000*net.res_gen["p_mw"].sum() # 风电功率 kw
# inversely_kw = 1000*net.res_ext_grid["p_mw"].sum() # 倒送功率 kw
# if inversely_kw > 0:
#     inversely_kw = 0

# reward_1 = 0
# loss = net.res_line["pl_mw"].sum()
# reward_1 = -loss
# reward_2 = 0
# voltage = net.res_bus['vm_pu'].values
# target_range=(0.95, 1.05)
# counts = 0
# for v in voltage:
#     if v >= target_range[0] and v <= target_range[1]:  # 电压在目标范围内
#         counts += 1
# reward_2 = counts - 33
# reward_3 = 0
# for i in range(len(best)):
#     if best[i] != last_best[i]:
#         reward_3 -= 2
# reward_4 = 0
# ext_grid = net.res_ext_grid['p_mw'].sum()
# if ext_grid < 0:
#     reward_4 -= ext_grid
# else:
#     reward_4 = 0
# reward = 10 * reward_1 + reward_2 + reward_3 + 5 * reward_4

# last_best = best
# log["time_flag"].append(time_flag)
# log["reward"].append(reward)
# log["loss_kw"].append(loss_kw)
# log["load_sum_kw"].append(load_sum_kw)
# log["wind_power_kw"].append(wind_power_kw)
# log["inversely_kw"].append(inversely_kw)  
# log["num_switch_changes"].append(reward_3)
# with open('PSO.json', 'w') as f:
#     json.dump(log, f, indent=4)
# env_network = env.update_powersystem()