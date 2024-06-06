import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use('TkAgg')
from pylab import *
from PSO.PSO_net import build_case33
import pandapower.topology as top #导入包
import networkx as nx

from Environment.PowerSystem import PowerSystemEnv
env  = PowerSystemEnv()

net = build_case33(env.network,opennum=[32, 33, 34, 35, 36]) #导入原始网络
net.switch.closed = True  #让全部开关处于闭合


# 检查网络中是否含有环 （因为两个外部电网是220千伏，不允许长时间合环运行）
def is_radial(net):
    mg = top.create_nxgraph(net, multi=False) #multi=False 允许平行边
    #create_nxgraph 将pandapower网络转换为NetworkX图，这是网络拓扑的简化表示，简化为节点和边。总线用节点表示(注意:只有in_service = 1的总线出现在图中)，边表示总线之间的物理连接()。
    # mg.add_edge(0, 1) #两个外电网节点相连

    for cycle in nx.cycle_basis(mg):#遍历每一个环（包括线路环和变压器环）
        print(cycle)#打印环
print(is_radial(net))#True
# print(net.switch)
