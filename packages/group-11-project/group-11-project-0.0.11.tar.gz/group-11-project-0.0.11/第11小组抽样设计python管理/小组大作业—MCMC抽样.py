import random


def beta_s(w, a, b):  # beta分布
    return w ** (a - 1) * (1 - w) ** (b - 1)


def random_coin(p):
    unif = random.uniform(0, 1)
    if unif >= p:
        return False
    else:
        return True


# 定义稳定于beta分布的MCMC函数
def beta_mcmc(N_hops, a, b):
    states = []
    cur = random.uniform(0, 1)
    for i in range(0, N_hops):
        states.append(cur)
        next = random.uniform(0, 1)
        ap = min(beta_s(next, a, b) / beta_s(cur, a, b), 1)  # 计算接受概率
        if random_coin(ap):
            cur = next
    return states[-1000:]  # 返回马尔科夫链上最近的1000个状态点


# 画图
import numpy as np
from matplotlib import pylab as plt
import scipy.special as ss

plt.rcParams['figure.figsize'] = (17.0, 4.0)


# 定义函数
def beta(a, b, i):
    e1 = ss.gamma(a + b)
    e2 = ss.gamma(a)
    e3 = ss.gamma(b)
    e4 = i ** (a - 1)
    e5 = (1 - i) ** (b - 1)
    return (e1 / (e2 * e3)) * e4 * e5


# 画图
def plot_beta(a, b):
    Ly = []
    Lx = []
    i_list = np.mgrid[0:1:100j]
    for i in i_list:
        Lx.append(i)
        Ly.append(beta(a, b, i))
    plt.plot(Lx, Ly, label="Real Distribution: a=" + str(a) + ", b=" + str(b))
    plt.hist(beta_mcmc(100000, a, b), density=True, bins=25,
             histtype='step', label="Simulated_MCMC: a=" + str(a) + ", b=" + str(b))
    plt.legend()
    plt.show()


plot_beta(0.1, 0.1)
plot_beta(1, 1)
plot_beta(2, 3)

from scipy.stats import norm


def norm_dist_prob(theta):
    y = norm.pdf(theta, loc=3, scale=2)
    return y


T = 5000
pi = [0 for i in range(T)]
sigma = 1
t = 0
while t < T - 1:
    t = t + 1
    pi_star = norm.rvs(loc=pi[t - 1], scale=sigma, size=1, random_state=None)  # 状态转移进行随机抽样
    alpha = min(1, (norm_dist_prob(pi_star[0]) / norm_dist_prob(pi[t - 1])))  # alpha值

    u = random.uniform(0, 1)
    if u < alpha:
        pi[t] = pi_star[0]
    else:
        pi[t] = pi[t - 1]

plt.scatter(pi, norm.pdf(pi, loc=3, scale=2), label='Target Distribution')
num_bins = 50
plt.hist(pi, num_bins, density=1, facecolor='red', alpha=0.7, label='Samples Distribution')
plt.legend()
plt.show()