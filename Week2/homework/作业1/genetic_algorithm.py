import numpy as np
from numpy.ma import cos
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D # 建模，不必需
import datetime  # 统计时间，不必需

DNA_SIZE = 24  # 编码长度
POP_SIZE = 100  # 种群大小
CROSS_RATE = 0.5  # 交叉率
MUTA_RATE = 0.15  # 变异率
Iterations = 50  # 迭代次数
X_BOUND = [0, 10]  # X区间
Y_BOUND = [0, 10]  # Y区间
 
 
def F(x, y):  # 香蕉函数
    """用于测试最优化算法的函数，具有一个全局最小值和多个局部最小值
       该函数在优化算法中常用于测试算法的性能和鲁棒性。
       目的：给算法优化方向提供指引，算法的目标是找到使F(x, y)最小的(x, y)值，即全局最优解。
       参数:
       x: 输入变量x，可以是一个数值或一个数组。
       y: 输入变量y，可以是一个数值或一个数组。
       返回值: 函数的输出值，刻画当前(x, y)偏离最优解的程度，直接传递给适应度函数的temp变量，故不额外命名。"""
    return (6.452*(x+0.125*y)*(cos(x)-cos(2*y))**2)/(0.8+(x-4.2)**2+2*(y-7)**2)+3.226*y
 
 
def getfitness(pop):  # 适应度函数
    """根据个体的基因型（编码）计算出一个数值，表示该个体在解决问题上的表现。
       适应度函数的设计直接影响到遗传算法的搜索效率和最终结果。
       目的：评估个体在种群中的优劣程度。
       参数:
       pop: 一个二维数组，表示种群中的个体，每行代表一个个体的基因型（编码），也就是一组解。
       返回值: 一个一维数组，表示每个个体的适应度值，数值越大表示个体越适应环境,在模型中意味着解更容易被保留和传递到下一代。"""
    x, y = decodeDNA(pop)
    temp = F(x, y)
    return (temp-np.min(temp))+0.0001
 
 
def decodeDNA(pop):  # 二进制转坐标，解码
    """将个体的基因型（编码）转换为实际的解空间中的坐标值。
       目的：将个体的基因型（编码）转换为实际的解空间中的坐标值。
       参数:
       pop: 同适应度函数中的pop。
       返回值: 两个一维数组，分别表示每个个体在解空间中的x和y坐标值。"""
    x_pop = pop[:, 1::2]
    y_pop = pop[:, ::2]
    # .dot()用于矩阵相乘
    x = x_pop.dot(2**np.arange(DNA_SIZE)[::-1])/float(2**DNA_SIZE-1)*(X_BOUND[1]-X_BOUND[0])+X_BOUND[0]
    y = y_pop.dot(2**np.arange(DNA_SIZE)[::-1])/float(2**DNA_SIZE-1)*(Y_BOUND[1]-Y_BOUND[0])+Y_BOUND[0]
    return x, y
 
 
def select(pop, fitness):  # 选择
    """根据个体的适应度值选择出下一代种群中的个体，通常使用轮盘赌选择、锦标赛选择等方法。
       目的：根据个体的适应度值选择出下一代种群中的个体。
       参数:
       pop: 一个二维数组，表示当前种群中的个体，每行代表一个个体的基因型（编码）。
       fitness: 一个一维数组，表示每个个体的适应度值，数值越大表示个体越适应环境。
       返回值: 一个二维数组，表示下一代种群中的个体，每行代表一个个体的基因型（编码）。"""
    temp = np.random.choice(np.arange(POP_SIZE), size=POP_SIZE, replace=True, p=fitness/(fitness.sum()))
    return pop[temp]
 
# mutation函数以及crossmuta函数均为编码过程
 
 
def mutation(temp, MUTA_RATE):  # 变异
    """对个体的基因型（编码）进行随机的修改，以引入新的基因变体，增加种群的多样性。
       目的：对个体的基因型（编码）进行随机的修改，以引入新的基因变体，增加种群的多样性。
       参数:
       temp: 一个一维数组，表示个体的基因型（编码）。
       MUTA_RATE: 变异率，表示变异的概率。
       返回值: 无。该函数直接修改输入的temp数组，进行基因变异。"""
    if np.random.rand() < MUTA_RATE:
        mutate_point = np.random.randint(0, DNA_SIZE)    # 引入随机数，随机选择一个变异点
        temp[mutate_point] = temp[mutate_point] ^ 1   # ^为异或运算
 
 
def crossmuta(pop, CROSS_RATE):  # 交叉
    """将两个个体的基因型（编码）进行组合，产生新的个体，以模拟自然界中的遗传过程。
       目的：将两个个体的基因型（编码）进行组合，产生新的个体。
       参数:
       pop: 一个二维数组，表示当前种群中的个体，每行代表一个个体的基因型（编码）。
       CROSS_RATE: 交叉率，表示交叉的概率。
       返回值: 一个二维数组，表示下一代种群中的个体，每行代表一个个体的基因型（编码）。"""
    new_pop = []
    for i in pop:
        temp = i
        if np.random.rand()<CROSS_RATE:
            j = pop[np.random.randint(POP_SIZE)]
            cpoints1 = np.random.randint(0, DNA_SIZE*2-1)
            cpoints2 = np.random.randint(cpoints1, DNA_SIZE*2)
            temp[cpoints1:cpoints2] = j[cpoints1:cpoints2]
            mutation(temp, MUTA_RATE)
        new_pop.append(temp)
    return new_pop

def print_info(pop):  # 输出最优解等
    """根据当前种群中的个体的基因型（编码）计算出最优解的信息，并打印出来。
       目的：根据当前种群中的个体的基因型（编码）计算
       参数:
       pop: 一个二维数组，表示当前种群中的个体，每行代表一个个体的基因型（编码）。
       返回值: 无。该函数直接打印出最优解的信息，包括最优的基因型、对应的(x, y)坐标以及函数值F(x, y)。"""
    fitness = getfitness(pop)
    maxfitness = np.argmax(fitness)
    print("max_fitness", fitness[maxfitness])
    x, y = decodeDNA(pop)
    print("最优的基因型:", pop[maxfitness])
    print("(x,y):", (x[maxfitness], y[maxfitness]))
    print("F(x,y)_max=", F(x[maxfitness], y[maxfitness]))
 
 
def plot_3d(ax):  # 建模
    """在三维空间中绘制出函数F(x, y)的曲面图，以可视化函数的形状和最优解的位置。
       目的：在三维空间中绘制出函数F(x, y)的曲面图。
       参数:
       ax: 三维坐标轴对象。
       返回值: 无。该函数直接在输入的三维坐标轴对象上绘制出函数F(x, y)的曲面图，并设置坐标轴标签和范围。"""
    X = np.linspace(*X_BOUND, 100)
    Y = np.linspace(*Y_BOUND, 100)
    X, Y = np.meshgrid(X, Y)
    Z = F(X, Y)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm)
    ax.set_zlim(-20,160)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
 
 
if __name__=="__main__":  # 主函数
    """主函数，执行遗传算法的主要流程，包括初始化种群、迭代优化、输出结果和绘图。
       目的：执行遗传算法的主要流程，包括初始化种群、迭代优化、输出结果和绘图。
       参数: 无。"""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    #ax = Axes3D(fig, auto_add_to_figure=False)
    # fig.add_axes(ax)
    #因为我的电脑上tcl库安装异常，无法显示窗口，所以我对源代码作了修改，将运行结果输出成图片。
    plot_3d(ax)
    pop = np.random.randint(2, size=(POP_SIZE, DNA_SIZE*2))
    start_t = datetime.datetime.now()
    for i in range(Iterations):
        print("i:", i)
        pop = np.array(crossmuta(pop, CROSS_RATE))
        fitness = getfitness(pop)
        pop = select(pop, fitness)
    end_t = datetime.datetime.now()
    print((end_t-start_t).seconds)
    print_info(pop)
    x, y = decodeDNA(pop)
    ax.scatter(x, y, F(x, y), c="black", marker='o', s=12)
    output_path = Path(__file__).with_name("genetic_algorithm_result.png")
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"最终图片已保存到: {output_path}")
