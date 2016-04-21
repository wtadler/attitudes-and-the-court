import pandas as pd
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import seaborn as sns

def split_train_test(data):
    data = data.iloc[np.random.permutation(len(data))]
    traindata = data.values[:(len(data)-len(data)/10), :]
    testdata = data.values[(len(data)-len(data)/10):, :]
    return traindata, testdata

def fit_model(traindata, testdata, y_col, x_cols, x_cols_nocourt):
    court = linear_model.ElasticNetCV(l1_ratio=0.9, cv=10, max_iter = 10000)
    court.fit(traindata[:, x_cols], traindata[:, y_col])
    print "train R^2"
    print court.score(traindata[:, x_cols], traindata[:, y_col])
    print "test R^2"
    print court.score(testdata[:, x_cols], testdata[:, y_col])

    no_court = linear_model.ElasticNetCV(l1_ratio=0.9, cv=10, max_iter = 10000)
    no_court.fit(traindata[:, x_cols_nocourt], traindata[:, y_col])
    print "train R^2 - no court predictors"
    print no_court.score(traindata[:, x_cols_nocourt], traindata[:, y_col])
    print "test R^2 - no court predictors"
    print no_court.score(testdata[:, x_cols_nocourt], testdata[:, y_col])

    return court, no_court

def plot_fit(data, model, x_cols, nonzero_only=True, title=''):
    sns.set_style('darkgrid')
    results = pd.DataFrame({'param': [data.columns.tolist()[i] for i in x_cols],
                            'value': model.coef_})
    if nonzero_only:
        results = results.loc[results.value != 0]
    sns.factorplot('value', 'param', kind="bar", data=results, size=10, aspect=.7)
    plt.title(title)