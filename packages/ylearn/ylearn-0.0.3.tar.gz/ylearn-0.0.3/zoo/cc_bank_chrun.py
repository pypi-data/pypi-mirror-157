import pandas as pd
# from sklearn.preprocessing import OrdinalEncoder
from sklearn import datasets
from sklearn.model_selection import train_test_split

from ylearn import Why


# x = datasets.load_wine(as_frame=True)
# print(x.DESCR)
# df = x.frame
# print(df)
#

def foo():
    data_file = 'Employee-Attrition.csv'
    data = pd.read_csv(data_file)
    outcome = 'Attrition'
    treatment = ['OverTime', 'StockOptionLevel', 'NumCompaniesWorked', 'MonthlyIncome', 'DistanceFromHome']
    adjustment = [c for c in data.columns.tolist() if c not in treatment and c != outcome]
    covariate = adjustment[:2]
    adjustment = adjustment[2:]
    c = Why()
    c.fit(data, outcome,
          treatment=treatment,
          adjustment=adjustment,
          covariate=covariate)
    e = c.causal_effect()
    print('causal effect:', e)


def ames_house_price():
    from sklearn.datasets import fetch_openml

    ames_housing = fetch_openml(name="house_prices", as_frame=True)
    outcome = ames_housing.target_names[0]  # 'SalePrice'
    data = ames_housing.data
    data[outcome] = ames_housing.target

    train_data, test_data = train_test_split(data, test_size=0.3, random_state=123)

    cc = Why(estimator='dml', random_state=123)
    cc.fit(train_data.copy(), outcome,
           # treatment=['Total_Trans_Ct'],
           # identify_discrete_treatment=False,
           )
    r = cc.whatif(test_data, test_data['MSZoning'].map(lambda _: 'RL'), treatment='MSZoning')
    print(r)
    # ct = cc.policy_tree(test_data)
    # print(ct)
    r = cc.causal_effect()
    print(r)

    r = cc.causal_effect(test_data)
    print(r)

    r = cc.causal_effect(test_data.head(10))
    print(r)

    # print('-' * 30)
    # w2 = Why()
    # # w2.fit(train_data.copy(),target,adjustment=y.covariate_[:5],covariate=y.covariate_[5:] )
    # # w2.fit(train_data.copy(),target,adjustment=y.covariate_[:5],covariate=y.covariate_[8:],instrument=y.covariate_[5:8])
    # # w2.fit(train_data.copy(), target, instrument=cc.covariate_[:5], covariate=cc.covariate_[5:])
    # print(w2)


def bank_churn():
    data = pd.read_csv('~/notebooks/data/BankChurners.csv.zip')
    data = data[data.columns[:-2]]
    data['Credit_Limit'] = data['Credit_Limit'].map(lambda v: int(v / 2000))
    data.pop('CLIENTNUM')
    target = 'Attrition_Flag'

    train_data, test_data = train_test_split(data, test_size=0.3, stratify=data[target])
    # target = 'Avg_Open_To_Buy'
    # train_data, test_data = train_test_split(data, test_size=0.3, random_state=123)

    cc = Why(identifier='discovery', estimator='dml', random_state=123)
    # treatment = cc.identify(train_data, target)[0]
    # treatment = treatment + ['Credit_Limit']

    cc.fit(train_data.copy(), target,
           # treatment=treatment
           )

    r = cc.whatif(test_data, test_data['Gender'].map(lambda _: 'F'), treatment='Gender')
    print(r)
    # ct = cc.policy_tree(test_data)
    # print(ct)
    r = cc.causal_effect()
    print(r)

    r = cc.causal_effect(test_data)
    print(r)

    r = cc.individual_causal_effect(test_data.head(10))
    print(r)


def bank_churn2():
    data = pd.read_csv('~/notebooks/data/BankChurners.csv.zip')
    # data = data[data.columns[:-2]]
    # data['Credit_Limit'] = data['Credit_Limit'].map(lambda v: int(v / 2000))
    # data.pop('CLIENTNUM')
    # target = 'Attrition_Flag'
    # cols = ['Customer_Age', 'Gender', 'Dependent_count', 'Education_Level',
    #         'Marital_Status', 'Income_Category', 'Card_Category', 'Months_on_book',
    #         'Total_Relationship_Count',
    #         # 'Months_Inactive_12_mon', 'Contacts_Count_12_mon',
    #         'Credit_Limit',
    #         # 'Total_Revolving_Bal',
    #         # 'Avg_Open_To_Buy', 'Total_Amt_Chng_Q4_Q1',
    #         'Total_Trans_Amt',
    #         # 'Total_Trans_Ct', 'Total_Ct_Chng_Q4_Q1', 'Avg_Utilization_Ratio',
    #         ]
    cols = ['Customer_Age', 'Gender', 'Dependent_count', 'Education_Level',
            'Marital_Status', 'Income_Category', 'Card_Category', 'Months_on_book',
            'Credit_Limit',
            'Total_Trans_Amt'
            ]
    data = data[cols]
    data['Credit_Limit'] = data['Credit_Limit'].map(lambda v: v // 2000 * 2000).astype('int')
    target = 'Total_Trans_Amt'

    train_data, test_data = train_test_split(data, test_size=0.2, random_state=123)
    # target = 'Avg_Open_To_Buy'
    # train_data, test_data = train_test_split(data, test_size=0.3, random_state=123)

    # cc = Why(identifier='discovery', estimator='ml', random_state=123)
    cc = Why(identifier='discovery', random_state=123)
    # cc = Why(  random_state=123)
    # treatment = cc.identify(train_data, target)[0]
    # treatment = treatment + ['Credit_Limit']

    cc.fit(train_data.copy(), target,
           # treatment=treatment
           # treatment=['Card_Category', 'Gender', ],
           )

    #
    # #
    # r = cc.causal_effect()
    # print(r)

    ct = cc.policy_tree(test_data)
    print(ct)

    r = cc.causal_effect(test_data.head(10))
    print(r)

    r = cc.individual_causal_effect(test_data.head(10))
    print(r)

    # r = cc.whatif(test_data, test_data['Gender'].map(lambda _: 'F'), treatment='Gender')
    # print(r)


def california_housing():
    housing = datasets.fetch_california_housing(as_frame=True)
    print(housing.DESCR)
    print('-' * 50)
    data = housing.frame
    outcome = housing.target_names[0]
    # data['geohash'] = data.apply(lambda row: geohash.encode(row['Latitude'], row['Longitude'], 3), axis=1)
    data[outcome] = housing.target
    why = Why()
    why.fit(data, outcome, treatment=['AveBedrms', 'AveRooms'])
    # why.fit(data, outcome,  )
    r = why.causal_effect(return_detail=True)
    print(r)


if __name__ == '__main__':
    # bank_churn2()
    # ames_house_price()
    california_housing()
    print('done')
