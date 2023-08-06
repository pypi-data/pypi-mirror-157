import pandas as pd
import numpy as np
from ylearn.estimator_model.deepiv import DeepIV

n = 5000

# Initialize exogenous variables; normal errors, uniformly distributed covariates and instruments
e = np.random.normal(size=(n,)) / 5
x = np.random.uniform(low=0.0, high=10.0, size=(n,))
z = np.random.uniform(low=0.0, high=10.0, size=(n,))

# Initialize treatment variable
# t = np.sqrt((x + 2) * z) + e
t = np.sqrt(2 * z + x * z + x * x + x) + e
# Show the marginal distribution of t

y = t*t / 10 +  x * x / 50 + e


data_dict = {
    'z': z,
    'w': x,
    'x': t,
    'y': y
}
data = pd.DataFrame(data_dict)
data=data.astype('float32')

div = DeepIV(is_discrete_treatment=False)
div.fit(
    data=data,
    outcome='y',
    treatment='x',
    instrument='z',
    adjustment='w',
    # covar_basis=('Poly', 2),
    # treatment_basis=('Poly', 2),
    # instrument_basis=('Poly', 1),
    device='cpu',
    batch_size=n,
    lr=0.5,
    epoch=1,
    sample_n=2,
)

n_test = 500
t = np.linspace(0,10,num = 100)
for i, x in enumerate([2, 5, 8]):
    # y_true = t*t / 10 - x*t/10
    y_true = t * t / 10 + x * x / 50

    test_data = pd.DataFrame(
        {'x': t,
         'w': np.full_like(t, x),},dtype='float32'
    )
    y_pred = div.estimate(data=test_data)