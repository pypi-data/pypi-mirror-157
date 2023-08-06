# Helper imports
import numpy as np
from numpy.random import binomial, multivariate_normal, normal, uniform
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
import matplotlib.pyplot as plt
import pandas as pd

from estimator_model.meta_learner import SLearner, TLearner, XLearner
from estimator_model.doubly_robust import DoublyRobust


# Define DGP
def generate_data(n, d, controls_outcome, treatment_effect, propensity):
    """Generates population data for given untreated_outcome, treatment_effect and propensity functions.

    Parameters
    ----------
        n (int): population size
        d (int): number of covariates
        controls_outcome (func): untreated outcome conditional on covariates
        treatment_effect (func): treatment effect conditional on covariates
        propensity (func): probability of treatment conditional on covariates
    """
    # Generate covariates
    X = multivariate_normal(np.zeros(d), np.diag(np.ones(d)), n)
    # Generate treatment
    T = np.apply_along_axis(lambda x: binomial(1, propensity(x), 1)[0], 1, X)
    # Calculate outcome
    Y0 = np.apply_along_axis(lambda x: controls_outcome(x), 1, X)
    treat_effect = np.apply_along_axis(lambda x: treatment_effect(x), 1, X)
    Y = Y0 + treat_effect * T
    return (Y, T, X)


def generate_controls_outcome(d):
    beta = uniform(-3, 3, d)
    return lambda x: np.dot(x, beta) + normal(0, 1)


treatment_effect = lambda x: (1 if x[1] > 0.1 else 0) * 8
propensity = lambda x: (0.8 if (x[2] > -0.5 and x[2] < 0.5) else 0.2)
# DGP constants and test data
d = 5
n = 1000
n_test = 250
controls_outcome = generate_controls_outcome(d)
X_test = multivariate_normal(np.zeros(d), np.diag(np.ones(d)), n_test)
delta = 6 / n_test
X_test[:, 1] = np.arange(-3, 3, delta)

y, x, w = generate_data(n, d, controls_outcome, treatment_effect, propensity)
data_dict = {
    'outcome': y,
    'treatment': x,
}
test_dict = {}
adjustment = []
for i in range(w.shape[1]):
    data_dict[f'w_{i}'] = w[:, i].squeeze()
    test_dict[f'w_{i}'] = X_test[:, i].squeeze()
    adjustment.append(f'w_{i}')
outcome = 'outcome'
treatment = 'treatment'
data = pd.DataFrame(data_dict)
test_data = pd.DataFrame(test_dict)

s = SLearner(model=GradientBoostingRegressor())
s.fit(
    data=data,
    outcome=outcome,
    treatment=treatment,
    adjustment=adjustment,
)
s_pred = s.estimate(data=test_data, quantity=None)

print(s_pred)

print('>'*30)

s1 = SLearner(model=GradientBoostingRegressor())
s1.fit(
    data=data,
    outcome=outcome,
    treatment=treatment,
    adjustment=adjustment,
    combined_treatment=False
)
s1_pred = s1.estimate(data=test_data, quantity=None)

import os
print(os.environ)