import pandapower as pp
import numpy as np
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
import pandapower.topology as top #导入包
import networkx as nx
from pandapower import diagnostic

def build_case33(net,opennum):
    net.switch.closed = True  #全部线路开关处于闭合
    for i in opennum:
        net.switch.loc[i,'closed'] = False  # 选定线路开关处于断开
    return net

# 如果网络中没有孤立节点 返回True
def is_supplied(net):

    return len(top.unsupplied_buses(net)) == 0 #unsupplied_buses查找未连接到外部电网的母线。 返回True或者False

# 如果网络中没有环，网络为开式网络，返回True
def is_radial(net):
    mg = top.create_nxgraph(net, multi=False) #multi=False 允许平行边。

    for cycle in nx.cycle_basis(mg):#遍历每一个环（包括线路环和变压器环）
        if len(cycle)>1:
            return False
    return True #如果没有环

# 检查开关位置是否合理
def analyze_switch_positions(net):
 
    if is_supplied(net)==True and is_radial(net)==True  :
        return True
    else:
        return False
