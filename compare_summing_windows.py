## run model with court summing windows from 1 to 10 years and plot train and
## test performance

import processing
import modeling
import matplotlib.pyplot as plt
import numpy as np

import os
# random.seed(seed=43)
plt.ion()
reload(processing)

gss = processing.preprocess_gss()
# gss = processing.preprocess_gss(composite=None, extra_imports=['affrmact'])


train_R2 = np.array([0.0] * 10)
test_R2 = np.array([0.0] * 10)
windows = range(1, 11)
n_reps = 10
for l in range(n_reps):
    # hard-code final length of data
    order = np.random.permutation(11318)
    for i in windows:
        court = processing.preprocess_court_data(summing_window=i)
        data, y_col, x_cols, x_cols_nocourt = processing.process_combined_data(gss, court, 'genderValue')
        train, test = modeling.split_train_test(data, order=order)
        model = modeling.fit_model(train, test, y_col, x_cols, x_cols_nocourt, print_fit=False)
        train_R2[i-1] = train_R2[i-1] + model[0].score(train[:, x_cols], train[:, y_col])
        test_R2[i-1] = test_R2[i-1] + model[0].score(test[:, x_cols], test[:, y_col])

train_R2 = train_R2 / n_reps
test_R2 = test_R2 / n_reps

plt.figure()
plt.plot(windows, train_R2, label="train")
plt.plot(windows, test_R2, label="test")
plt.legend()
plt.xlabel("court summing window")
plt.ylabel("R^2")
plt.savefig("summing_windows.png")
