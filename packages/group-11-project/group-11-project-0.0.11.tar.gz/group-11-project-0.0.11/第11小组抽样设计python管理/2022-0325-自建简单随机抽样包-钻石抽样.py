#不用软件自带的包 基于简单随机抽样对钻石价格-重量进行分析
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
data = pd.read_csv(r'C:\Users\Admin\Desktop\diamonds.csv')


''' 惰性求值    yield  
即：你需要时才获取，包含yield语句得函数可以用来创建生成器对象，这样得函数也称生成器函数，每次执行到yiled语句会返回一个值然后暂停或挂起后面得代码得执行，下次通过生成器对象得__next()__方法，内置函数x.next()，for 循环遍历生成器对象元素或其他方式显示“索要”数据恢复执行。'''

from random import randint
import time

def myrandint( start,end,seed=999999999 ):
    a=32310901
    b=1729
    rOld=seed   #将种子seed赋值给rOld
    m=end-start   #得到m 模数
    while True:
        rNew=int(( a*rOld+b )%m)   #开始产生随机数
        #遇到yield关键字暂时挂起后面的代码，等带next(r)的调用并返回 rNew
        yield rNew
    rOld=rNew

for i in range(500):
    now=time.time()+randint(0,5000)     #时间戳加一个随机数作为种子
    print(now)
    r=myrandint(1,10000,now)     #把时间种子作为参数调用myrandint函数
    print( "种子",now,"生成的随机数:" )
    for j in range(500):
        print( next(r),end="," )
    print()

price = data.iloc[:, 0]
carat = data.iloc[:, 1]

# price = beta_0 + beta_1 * carat + epsilon

def func(carat, beta_0, beta_1, epsilon):
    price = beta_0 + beta_1 * carat + epsilon
    return price

popt, pcov = curve_fit(func, carat, price)
dat = []
for i in range(0, 500):
    data1 = data.sample(n=5000)
    price = data1.iloc[:, 0]
    carat = data1.iloc[:, 1]
    popt, pcov = curve_fit(func, carat, price)
dat.append(popt)

dat = np.array(dat)
mean = np.average(dat[:,1], axis=0)
var = np.var(dat[:,1], axis=0)
std = np.std(dat[:,1], axis=0)
