import processing
import modeling
import matplotlib.pyplot as plt
import numpy as np
import os

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
from sklearn.grid_search import GridSearchCV

# random.seed(seed=43)
plt.ion()
reload(processing)

gss = processing.preprocess_gss()

court = processing.preprocess_court_data(summing_window=1)
data, y_col, x_cols, x_cols_nocourt = processing.process_combined_data(gss, court, 'genderValue')


tuned_parameters = [{'max_features': [.5,.6,.7,.8,.9,1], 'max_depth': [1,2,3,4,5,6,7]}]
clf = GridSearchCV(DecisionTreeRegressor(), tuned_parameters, cv=3)
clf.fit(train[:, x_cols], train[:, y_col])
for params, mean_score, scores in clf.grid_scores_:
	print("%0.3f (+/-%0.03f) for %r"
	% (mean_score, scores.std() * 2, params))
clf.score(test[:, x_cols], test[:, y_col]) # .1228

tuned_parameters = [{'n_estimators': [3,6,9,12], 'max_depth': [1,2,3,4,5,6,7]}]
clf = GridSearchCV(RandomForestRegressor(), tuned_parameters, cv=3)
clf.fit(train[:, x_cols], train[:, y_col])
for params, mean_score, scores in clf.grid_scores_:
	print("%0.3f (+/-%0.03f) for %r"
	% (mean_score, scores.std() * 2, params))
clf.score(test[:, x_cols], test[:, y_col]) # .15 with max_depth=5, n_estimators=12

tuned_parameters = [{'n_estimators': [4,8,16,32], 'loss': ['linear', 'square', 'exponential']}]
clf = GridSearchCV(AdaBoostRegressor(), tuned_parameters, cv=3)
clf.fit(train[:, x_cols], train[:, y_col])
for params, mean_score, scores in clf.grid_scores_:
	print("%0.3f (+/-%0.03f) for %r"
	% (mean_score, scores.std() * 2, params))
clf.score(test[:, x_cols], test[:, y_col]) # .106



train, test = modeling.split_train_test(data)

tuned_parameters = [{'n_estimators': [3,6,9,12], 'max_depth': [1,2,3,4,5,6,7]}]
rf = GridSearchCV(RandomForestRegressor(), tuned_parameters, cv=3)
model = modeling.fit_model(train, test, y_col, x_cols, x_cols_nocourt, model=rf)

modeling.plot_fit(data, model[0], x_cols)