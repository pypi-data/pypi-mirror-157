import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from itertools import product
from sklearn.linear_model import LinearRegression, MultiTaskElasticNet, MultiTaskElasticNetCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import PolynomialFeatures

from exp_data import single_continuous_treatment, single_binary_treatment, multi_continuous_treatment
from estimator_model.double_ml import DML4CATE
from estimator_model.utils import nd_kron

train, val, treatment_effect = single_continuous_treatment()

adjustment = train.columns[:-4]
covariate = 'c_0'
outcome = 'outcome'
treatment = 'treatment'

dml = DML4CATE(
    x_model=RandomForestRegressor(),
    y_model=RandomForestRegressor(),
    cf_fold=3,
    covariate_transformer=PolynomialFeatures(degree=3),
)
dml.fit(
    train,
    outcome,
    treatment,
    adjustment,
    covariate,
)


def exp_te(x):
    return np.exp(2 * x)


dat = np.array(list(product(np.arange(0, 1, 0.01), repeat=1))).ravel()
data_test = pd.DataFrame({'c_0': dat})
true_te = np.array([exp_te(xi) for xi in data_test[covariate]])
ested_te = dml.estimate(data_test).ravel()
print(true_te)
print('-' * 50)
print(ested_te)
