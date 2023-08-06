# 代码法
import numpy as np
import pandas as pd

np.random.seed(2)
# 产生2500个随机数，随机数区间属于0-10000
rand = np.random.randint(0, 10000, 2500)
# 将抽取的随机数划分等级
m = []
for x in rand:
    if x <= 1256:
        m.append('D')
    else:
        if 1257 <= x <= 3072:
            m.append('E')
        else:
            if 3073 <= x <= 4841:
                m.append('F')
            else:
                if 4842 <= x <= 6934:
                    m.append('G')
                else:
                    if 6935 <= x <= 8473:
                        m.append('H')
                    else:
                        if 8474 <= x <= 9478:
                            m.append('I')
                        else:
                            m.append('J')
# 将其转换为数据框格式
m = pd.DataFrame(m)
# 计算各种颜色需要抽取的个数
m.value_counts()
# 导入数据
data = pd.read_csv("C:\\Users\\lenovo\\Desktop\\diamonds.csv")  # reading file
print(data)
# 将抽取的标签和个数存入字典中,作为分层抽样的依据
diamondsdict = {'G': 514, 'F': 451, 'E': 426, 'H': 412, 'D': 300, 'I': 278, 'J': 119}
gbr = data.groupby('color')
gbr.groups


def diamondsamling(group, diamondsdict):  # 定义分层抽样的函数
    name = group.name
    n = diamondsdict[name]
    return group.sample(n=n)


result = data.groupby(
    'color', group_keys=False
).apply(diamondsamling, diamondsdict)  # 进行抽样

# 方法2 拉希里法
data['color'].value_counts()  # 输出每种颜色的个数
# 将其存入字典当中
diamondsdict = {1: 6775, 2: 9797, 3: 9542, 4: 11292, 5: 8304, 6: 5422, 7: 2808}
m *= 11292  # 得到m*=max（mi）
N = 7

alllist = []  # 该列表用来存储所抽取的群是哪个
np.random.seed(42)
for i in range(1, 10000000000):
    a = np.random.randint(1, 11293)
    b = np.random.randint(1, 7)
    s = diamondsdict.get(b)
    if len(alllist) == 2500:  # 当列表长度=2500时，停止循环
        break
    else:
        if a > s:
            alllist.append(b)

# 将其转换为数据框格式
alllist = pd.DataFrame(alllist)
# 计算各种颜色需要抽取的个数
alllist.value_counts()
# 利用选取的个数进行抽样
diamondsdict = {'D': 689, 'E': 236, 'F': 250, 'G': 0, 'H': 462, 'I': 863, 'J': 0}
gbr = data.groupby('color')
gbr.groups


def diamondsamling(group, diamondsdict):  # 定义分层抽样的函数
    name = group.name
    n = diamondsdict[name]
    return group.sample(n=n)


np.random.seed(42)
result = data.groupby(
    'color', group_keys=False
).apply(diamondsamling, diamondsdict)  # 进行抽样
