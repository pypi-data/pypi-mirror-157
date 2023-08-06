from ylearn.causal_discovery.gen import gen
from ylearn.causal_discovery._discovery import func

X = gen(noise_scale=0.1)  # 输入数据，形式为(数据点的数目，节点数目)（这里是5个节点的100组数据点）
print(X.shape)

W_est = func(X.copy(), extra_layer_dim=[3])  # extra_layer_dim为中间的全连接层的尺寸结构，默认为空
print(W_est)
#
# import numpy as np
# from sklearn.linear_model import LinearRegression as LR
#
#
# def dat_gen():
#     x = np.random.random_sample(20000)
#     y = 0.7 * x + 0.1 * np.random.random_sample(20000)
#     y = y / (np.max(y) - np.min(y))  # 对数据的归一化非常重要，直接决定拟合能否奏效
#     return x, y
#
#
# x, y = dat_gen()
# print(np.max(x), np.min(x))
# print(np.max(y), np.min(y))
# lr = LR()
# lr.fit(x.reshape(-1, 1), y)
# print(lr.coef_)  # 这样算出来的权重更小，可以用来确认因果关系
# lr = LR()
# lr.fit(y.reshape(-1, 1), x)
# print(lr.coef_)
