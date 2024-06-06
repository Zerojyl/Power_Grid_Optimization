import numpy as np
from PSO.PSO_net import build_case33

net = build_case33(opennum=[32, 33, 34, 35, 36])

cycle=[
[7, 20, 21, 11, 10, 9, 8],
[31, 30, 29, 28, 24, 23, 22, 2, 1, 18, 19, 20, 21, 11, 10, 9, 8, 14, 15, 16, 17, 32],
[7, 6, 5, 25, 26, 27, 28, 24, 23, 22, 2, 1, 18, 19, 20],
[3, 4, 5, 25, 26, 27, 28, 24, 23, 22, 2],
[13, 12, 11, 10, 9, 8, 14]
]

# print(net.switch)
switchnums=[]
for  a in range(len(cycle)):#遍历每一个环
    switchnum = []  # 存储母线编号
    for j in cycle[a]:#遍历当前环的每一条母线
        if j in net.switch.bus:
            switch=list(net.switch[net.switch.bus ==j].element)
            if len(switch)>0:
                for i in switch:
                    if i not in switchnum:
                        switchnum.append(i)
    switchnums.append(switchnum)
print(switchnums)