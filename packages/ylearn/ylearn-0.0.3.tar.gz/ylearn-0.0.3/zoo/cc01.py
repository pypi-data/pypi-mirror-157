import pandas as pd

from ylearn.causal_console import CausalConsole


def foo():
    data_file = 'Employee-Attrition.csv'
    data = pd.read_csv(data_file)
    outcome = 'Attrition'
    treatment = ['OverTime', 'StockOptionLevel', 'NumCompaniesWorked', 'MonthlyIncome', 'DistanceFromHome']
    adjustment = [c for c in data.columns.tolist() if c not in treatment and c != outcome]
    covariate = adjustment[:2]
    adjustment = adjustment[2:]
    c = CausalConsole()
    c.fit(data, outcome,
          treatment=treatment,
          adjustment=adjustment,
          covariate=covariate)
    e = c.causal_effect()
    print('causal effect:', e)


def bar():
    from tests import _dgp as dgp
    data, test_data, outcome, treatment, adjustment, covariate = dgp.generate_data_x2b_y1()
    cc = CausalConsole(estimator='div')
    # cc.fit(data, outcome[0], treatment=treatment, adjustment=adjustment, covariate=covariate)
    instrument = adjustment[:3]
    adjustment = adjustment[3:]
    fit_kwargs = dict(
        sample_n=2,
        lr=0.5,
        epoch=1,
        device='cpu',
        batch_size=len(data)
    )
    cc.fit(data, outcome[0], treatment=treatment, adjustment=adjustment, covariate=None, instrument=instrument,
           **fit_kwargs)

    print('-' * 30)
    e = cc.causal_effect()
    print('causal effect:', e, sep='\n')

    print('-' * 30)
    e = cc.cohort_causal_effect(test_data)
    print('cohort causal effect:', e, sep='\n')

    print('-' * 30)
    e = cc.local_causal_effect(test_data)
    print('local causal effect:', e, sep='\n')


if __name__ == '__main__':
    bar()
