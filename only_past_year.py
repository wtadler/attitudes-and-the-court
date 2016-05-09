import processing
import modeling
import matplotlib.pyplot as plt
import numpy as np

import os
# random.seed(seed=43)
plt.ion()
reload(processing)

gss = processing.preprocess_gss()

court = processing.preprocess_court_data(summing_window=1)
data, y_col, x_cols, x_cols_nocourt = processing.process_combined_data(gss, court, 'genderValue')
data_recentcase = data[(data.lib_decision_window > 0) | (data.lib_decision_window > 0)]
n_reps = 10

train_nocourt_R2 = 0.0
test_nocourt_R2 = 0.0
train_R2 = 0.0
test_R2 = 0.0
for l in range(n_reps):
    train, test = modeling.split_train_test(data)
    model = modeling.fit_model(train, test, y_col, x_cols, x_cols_nocourt, print_fit=False)
    train_R2 = train_R2 + model[0].score(train[:, x_cols], train[:, y_col])
    test_R2 = test_R2 + model[0].score(test[:, x_cols], test[:, y_col])
    train_nocourt_R2 = train_nocourt_R2 + model[1].score(train[:, x_cols_nocourt], train[:, y_col])
    test_nocourt_R2 = test_nocourt_R2 + model[1].score(test[:, x_cols_nocourt], test[:, y_col])

train_R2 = train_R2 / n_reps
test_R2 = test_R2 / n_reps
train_nocourt_R2 = train_nocourt_R2 / n_reps
test_nocourt_R2 = test_nocourt_R2 / n_reps

print "train R^2: " + str(train_R2)
print "test R^2: " + str(test_R2)

print "train R^2 no court: " + str(train_nocourt_R2)
print "test R^2 no court: " + str(test_nocourt_R2)
