import json

# 打开并读取JSON文件
with open('./results/PSO.json', 'r') as a:
    PSO_data = json.load(a)
with open('./results/st_test.json', 'r') as b:
    st_data = json.load(b)
with open('./results/agent_test.json', 'r') as c:
    agent_data = json.load(c)


# 获取键为'reward'的值
PSO_rewards = PSO_data['reward']
PSO_loss_kw = PSO_data['loss_kw']
PSO_load_sum_kw = PSO_data['load_sum_kw']
PSO_wind_power_kw = PSO_data['wind_power_kw']
PSO_inverse_kw = PSO_data['inversely_kw']
PSO_changes_num = PSO_data['num_switch_changes']

st_rewards = st_data['reward']
st_loss_kw = st_data['loss_kw']
st_load_sum_kw = st_data['load_sum_kw']
st_wind_power_kw = st_data['wind_power_kw']
st_inverse_kw = st_data['inversely_kw']
st_changes_num = st_data['num_switch_changes']

agent_rewards = agent_data['reward']
agent_loss_kw = agent_data['loss_kw']
agent_load_sum_kw = agent_data['load_sum_kw']
agent_wind_power_kw = agent_data['wind_power_kw']
agent_inverse_kw = agent_data['inversely_kw']
agent_changes_num = agent_data['num_switch_changes']

# 计算平均值
PSO_rewards_average = sum(PSO_rewards) / len(PSO_rewards)
PSO_loss_kw_average = sum(PSO_loss_kw) / len(PSO_loss_kw)
PSO_average_load_sum_kw = sum(PSO_load_sum_kw) / len(PSO_load_sum_kw)
PSO_average_wind_power_kw = sum(PSO_wind_power_kw) / len(PSO_wind_power_kw)
PSO_average_inverse_kw = sum(PSO_inverse_kw) / len(PSO_inverse_kw)
PSO_average_changes_num = sum(PSO_changes_num) / len(PSO_changes_num)

st_rewards_average = sum(st_rewards) / len(st_rewards)
st_loss_kw_average = sum(st_loss_kw) / len(st_loss_kw)
st_average_load_sum_kw = sum(st_load_sum_kw) / len(st_load_sum_kw)
st_average_wind_power_kw = sum(st_wind_power_kw) / len(st_wind_power_kw)
st_average_inverse_kw = sum(st_inverse_kw) / len(st_inverse_kw)
st_average_changes_num = sum(st_changes_num) / len(st_changes_num)

agent_rewards_average = sum(agent_rewards) / len(agent_rewards)
agent_loss_kw_average = sum(agent_loss_kw) / len(agent_loss_kw)
agent_average_load_sum_kw = sum(agent_load_sum_kw) / len(agent_load_sum_kw)
agent_average_wind_power_kw = sum(agent_wind_power_kw) / len(agent_wind_power_kw)
agent_average_inverse_kw = sum(agent_inverse_kw) / len(agent_inverse_kw)
agent_average_changes_num = sum(agent_changes_num) / len(agent_changes_num)


# 打印平均值
print("奖励平均值对比：")
print('agent_rewards_average:', agent_rewards_average)
print('st_rewards_average:', st_rewards_average)
print('PSO_rewards_average:', PSO_rewards_average)

print('网损平均值对比：')
print('agent_loss_kw_average:', agent_loss_kw_average)
print('st_loss_kw_average:', st_loss_kw_average)
print('PSO_loss_kw_average:', PSO_loss_kw_average)

print("总负荷平均值：")
print('agent_average_load_sum_kw:', agent_average_load_sum_kw)
print('st_average_load_sum_kw:', st_average_load_sum_kw)
print('PSO_average_load_sum_kw:', PSO_average_load_sum_kw)

print("风电功率平均值：")
print('agent_average_wind_power_kw:', agent_average_wind_power_kw)
print('st_average_wind_power_kw:', st_average_wind_power_kw)
print('PSO_average_wind_power_kw:', PSO_average_wind_power_kw)

print("倒送功率平均值：")
print('agent_average_inverse_kw:', agent_average_inverse_kw)
print('st_average_inverse_kw:', st_average_inverse_kw)
print('PSO_average_inverse_kw:', PSO_average_inverse_kw)

print("切换次数平均值：")
print('agent_average_changes_num:', agent_average_changes_num)
print('st_average_changes_num:', st_average_changes_num)
print('PSO_average_changes_num:', PSO_average_changes_num)




