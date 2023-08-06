from sklearn.datasets import fetch_california_housing

from ylearn import Why

housing = fetch_california_housing(as_frame=True)
data = housing.frame
outcome = housing.target_names[0]
data[outcome] = housing.target

why = Why()
why.fit(data, outcome, treatment=['AveBedrms', 'AveRooms'])

print(why.causal_effect())

# print(housing.DESCR)
# print('-' * 50)
