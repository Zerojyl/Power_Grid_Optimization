pso_path = r'C:\project\Electric-innovation-competition\Power_Grid_Optimization\results\pso.json'
agent_path = r'C:\project\Electric-innovation-competition\Power_Grid_Optimization\results\agent.json'
static_path = r'C:\project\Electric-innovation-competition\Power_Grid_Optimization\results\static.json'
violence_path = r'C:\project\Electric-innovation-competition\Power_Grid_Optimization\results\violence.json'
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# read json file
def read_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['time_flag'] = df['time_flag'].apply(str)
    df['time_flag'] = df['time_flag'].str.replace('T',' ')
    df['time_flag'] = pd.to_datetime(df['time_flag'])
    df = df.set_index('time_flag')
    df['num_switch_changes'] = -df['num_switch_changes']
    # 随着时间累加
    for i in range(1, len(df)):
        df['num_switch_changes'][i] += df['num_switch_changes'][i-1]
    return df
agent_df = read_json(agent_path)
pso_df = read_json(pso_path)
static_df = read_json(static_path)
violence_df = read_json(violence_path)
static_df.head(12)

# plot the df


def plot_df(column, title, len_coef=0.5):
    plt.figure(figsize=(20,10))
    df_name = ['agent', 'pso', 'static', 'violence search']
    for i, df in enumerate([agent_df, pso_df, static_df, violence_df]):
        # len_coef = 0.5
        df_len = len(df)
        df_len = int(df_len * len_coef)
        df = df.iloc[:df_len]
        plt.plot(df.index, df[column], label=df_name[i])
    # title
    plt.title(title)
    # x label
    plt.xlabel('time')
    # y label
    plt.ylabel(title)
    # grid
    plt.grid(True)
    plt.legend()
    plt.show()

# 绘制柱状图
def plot_df2(column, title, len_coef=0.2):
    plt.figure(figsize=(20,10))
    df_name = ['agent', 'pso', 'static', 'violence search']
    for i, df in enumerate([agent_df, pso_df, static_df, violence_df]):
        # len_coef = 0.5
        df_len = len(df)
        df_len = int(df_len * len_coef)
        df = df.iloc[:df_len]
        # 根据index绘制柱状图
        width = 0.2
        x = np.arange(len(df))
        plt.bar(x + i*width, df[column], width=width, label=df_name[i])
        # plt.bar(df.index, df[column], label=df_name[i])
    plt.xticks(x + width, df.index)

    # title
    plt.title(title)
    # x label
    plt.xlabel('time')
    # y label
    plt.ylabel(title)
    # grid
    plt.grid(True)
    plt.legend()
    plt.show()

plot_df('reward','total score')
plot_df('loss_kw','grid loss(kw)')
plot_df('num_switch_changes', 'switch changes')
plot_df('inversely_kw','inversely (kw)')