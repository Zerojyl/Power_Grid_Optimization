import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm#进度条设置
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use('TkAgg')
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
from PSO_net import *
import time 
from modified_IEEE33bus_powersystem import PowerSystemEnv
import copy
switchcycle = [[7, 20, 32, 11, 34, 10, 9, 8, 33], 
             [31, 30, 29, 28, 36, 23, 22, 2, 21, 1, 17, 18, 19, 20, 32, 11, 34, 10, 9, 8, 33, 14, 15, 16, 35], 
             [7, 6, 5, 24, 25, 26, 27, 28, 36, 23, 22, 2, 21, 1, 17, 18, 19, 20, 32], 
             [3, 4, 5, 24, 25, 26, 27, 28, 36, 23, 22, 2, 21], 
             [13, 12, 11, 34, 10, 9, 8, 33, 14]] 
class Liqun:
    def __init__(self, net):
        # PSO的参数
        self.switchcycle = switchcycle   #近似等于每个独立回路上的开关
        self.w = 1  # 惯性因子，一般取1
        self.c1 = 1  # 学习因子1，一般取2
        self.c2 = 1 #学习因子2，一般取2
        self.dim = 5  # 对应5把开关编号
        self.size = 30  # 种群大小，即种群中小鸟的个数
        self.iter_num = 5  # 算法最大迭代次数
        self.max_vel = 0.5  # 限制粒子的最大速度为0.5
        self.min_vel = -0.5  # 限制粒子的最小速度为-0.5
        self.net = net

    # 初始化种群
    def init_x(self):
        """
        从每个环（母线）所连开关随机选择一个开关断开，且保证开关编号不重复
        :return: 随机生成的断开开关编号种群
        """
        X=np.zeros(shape=(self.size,self.dim))
        for i in range(len(X)):#遍历每一个个体
            switchnums = []  # 存储开关编号
            for  a in range(len(self.switchcycle)):#遍历每一个环
                switchnum = np.random.choice(self.switchcycle[a], 1)[0] #从每个环里选择一条开关断开
                while switchnum  in switchnums:
                    switchnum = np.random.choice(self.switchcycle[a], 1)[0]  # 从每个环里选择一条开关断开
                switchnums.append(switchnum)
            X[i]=switchnums
        return X

    # 目标函数公式
    def calc_f(self, x):
        """计算个体粒子的的适应度值，也就是目标函数值， """
        net = build_case33(self.net,opennum=x)
        if analyze_switch_positions(net)==False:
            return 1e9
        else: 
            try:
                pp.runpp(net, numba = False)
            except:
                return 1e9
            return net.res_line["pl_mw"].sum()

    # ===粒子群速度更新公式====
    def velocity_update(self, V,X, pbest, gbest):
        """
        根据速度更新公式更新每个粒子的速度
         种群size
        :param V: 粒子当前的速度矩阵，size*dim的矩阵
        :param X: 粒子当前的位置矩阵，size*dim 的矩阵
        :param pbest: 每个粒子历史最优位置，size*dim 的矩阵
        :param gbest: 种群历史最优位置，1*dim 的矩阵
        """
        r1 = np.random.random((self.size, 1))
        r2 = np.random.random((self.size, 1))
        V = self.w * V + self.c1 * r1 * (pbest - X) + self.c2 * r2 * (gbest - X)  # 直接对照公式写就好了
        # 防止越界处理
        V[V > self.max_vel] = self.max_vel
        V[V < self.min_vel] = self.min_vel
        return V

    def position_update(self,X, V):
        """
        根据公式更新粒子的位置
        :param x: 粒子当前的位置矩阵，
        :param V: 粒子当前的速度举着，
        """
        X=np.round(X+V)
        for i in range(len(X)):#遍历每一个个体
            for  a in range(len(self.switchcycle)):#遍历每一个环
                while X[i,a] not in self.switchcycle[a]:#遍历当前个体的每一个开关
                    newswitch=np.random.choice(self.switchcycle[a], 1)[0] #从每个环里选择一条开关断开
                    #while newswitch not in X[i]:
                        #newswitch = np.random.choice(self.switchcycle[a], 1)[0]  # 从每个环里选择一条开关断开
                    X[i,a]=newswitch
        return X

    def main(self):
        X=self.init_x() #初始化群体
        # 初始化种群的各个粒子的速度
        V = np.random.uniform(-0.5, 0.5, size=(self.size,self.dim))  ##2维 表示x、y的速度
        fitneess_value_list=[] #存储最优

        # 计算种群各个粒子的初始适应度值
        p_fitness =np.zeros(shape=(self.size,1))
        for i in range(len(X)):
            p_fitness[i]=self.calc_f(X[i])
        # 计算种群的初始最优适应度值
        g_fitness = p_fitness.min()
        # 讲添加到记录中
        fitneess_value_list.append(g_fitness)
        # 初始的个体最优位置和种群最优位置
        pbest = X
        gbest = X[p_fitness.argmin()]
        # print(gbest)
        # 接下来就是不断迭代了
        # for i in tqdm(range(self.iter_num)):
        for i in range(self.iter_num):
            V = self.velocity_update(V, X, pbest, gbest)  # 更新速度
            X = self.position_update(X, V)  # 更新位置

            p_fitness2 = np.zeros(shape=(self.size,1))  # 计算各个粒子的适应度
            for j in range(len(X)):#遍历子代各个个体
                p_fitness2[j] = self.calc_f(X[j])
            #种群更新
            # 更新每个粒子的历史最优位置
            for j in range(self.size):
                if p_fitness[j] > p_fitness2[j]:
                    pbest[j] = X[j]
                    p_fitness[j] = p_fitness2[j]

            # 更新群体的最优位置
            g_fitness=p_fitness.min()
            gbest =  pbest[p_fitness.argmin()]

            # 记录最优迭代结果
            fitneess_value_list.append(g_fitness)
        #     print("i:",gbest)

        # print(gbest)
        
        # 绘图
        # plt.plot(fitneess_value_list, color='r')
        # plt.title('迭代过程')
        # plt.show()
        return gbest
    
def build_case33(net,opennum):
    net.switch.closed = True  #全部线路开关处于闭合
    for i in opennum:
        net.switch.loc[i,'closed'] = False  # 选定线路开关处于断开
    return net

if __name__ =="__main__":

    env = PowerSystemEnv()
    env_network = env.reset(17)
    network = copy.deepcopy(env_network)

    li = Liqun(net= network)
    best = li.main()
    # # 创建一个新的图形
    # fig, axs = plt.subplots(2)
    net = build_case33(network,opennum=[32, 33, 34, 35, 36]) #导入结果网络
    pp.runpp(net,numba = False)#潮流计算
    print("优化前有功功率损失",1000*net.res_line["pl_mw"].sum(),"KW")

    net = build_case33(network,opennum = best) #导入结果网络
    pp.runpp(net,numba = False)#潮流计算
    print(net.res_bus)
    print("优化后有功功率损失",1000*net.res_line["pl_mw"].sum(),"KW")
 

    for i in range(5):
        env_network = env.update_powersystem()
        network = copy.deepcopy(env_network)
        li = Liqun(net= network)
        best = li.main()
        net = build_case33(network,opennum=[32, 33, 34, 35, 36]) #导入结果网络
        pp.runpp(net,numba = False)#潮流计算
        print("优化前有功功率损失",1000*net.res_line["pl_mw"].sum(),"KW")
        net = build_case33(network,opennum = best) #导入结果网络
        pp.runpp(net,numba = False)#潮流计算
        print(net.res_bus)
        print("优化后有功功率损失",1000*net.res_line["pl_mw"].sum(),"KW")