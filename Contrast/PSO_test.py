from modified_IEEE33bus_powersystem import PowerSystemEnv
from PSO_main import build_case33
from PSO_main import Liqun
import pandapower as pp
import numpy as np
import copy
import json
import yaml

config_path = './utils/configs/environment/env.yaml'
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

log = {
    "time_flag": [],
    "reward": [],
    "loss_kw": [],
    "load_sum_kw": [],
    "wind_power_kw": [],
    "inversely_kw": [],
    "num_switch_changes": []
      }

np.random.seed(0)
iterations = 288
env = PowerSystemEnv()
sample_idx = np.random.randint(0, 10000) 
env_network = env.reset(sample_idx=sample_idx)

last_best = [32,33,34,35,36]
for i in range(iterations):
    network = copy.deepcopy(env_network)
    li = Liqun(net= network)
    best = li.main()
    net = build_case33(network,opennum = best) #导入结果网络
    pp.runpp(net,numba = False)#潮流计算

    time_flag = env.load_data.get_data(point_step = env.time_flag, history_step = 0).index[-1].isoformat()
    loss_kw = 1000*net.res_line["pl_mw"].sum() # 线路损耗 kw
    load_sum_kw = 1000*net.res_load["p_mw"].sum() # 负荷总和 kw
    wind_power_kw = 1000*net.res_gen["p_mw"].sum() # 风电功率 kw
    inversely_kw = 1000*net.res_ext_grid["p_mw"].sum() # 倒送功率 kw
    if inversely_kw > 0:
        inversely_kw = 0
    
    reward_1 = 0
    loss = net.res_line["pl_mw"].sum()
    reward_1 = -loss 
    reward_2 = 0
    voltage = net.res_bus['vm_pu'].values
    target_range=(0.95, 1.05)
    counts = 0
    for v in voltage:
        if v >= target_range[0] and v <= target_range[1]:  # 电压在目标范围内
            counts += 1
    reward_2 = counts - 33
    reward_3 = 0
    for i in range(len(best)):
        if best[i] != last_best[i]:
            reward_3 -= 2
    reward_4 = 0
    ext_grid = net.res_ext_grid['p_mw'].sum()
    if ext_grid < 0:
        reward_4 = ext_grid
    else:
        reward_4 = 0
        
    reward = config['ratio']['loss_k'] * reward_1 + config['ratio']['stable_k'] * reward_2 \
        + config['ratio']['switch_k'] * reward_3 + config['ratio']['inverse_k'] * reward_4

    last_best = best
    log["time_flag"].append(time_flag)
    log["reward"].append(reward)
    log["loss_kw"].append(loss_kw)
    log["load_sum_kw"].append(load_sum_kw)
    log["wind_power_kw"].append(wind_power_kw)
    log["inversely_kw"].append(inversely_kw)  
    log["num_switch_changes"].append(reward_3)
    with open('./results/PSO.json', 'w') as f:
        json.dump(log, f, indent=4)
    env_network = env.update_powersystem()