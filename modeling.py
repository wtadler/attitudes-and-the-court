import pandas as pd
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import seaborn as sns

def split_train_test(data):
    data = data.iloc[np.random.permutation(len(data))]
    # traindata = data.values[:(len(data)-2000), :]
    # testdata = data.values[(len(data)-2000):, :]
    traindata = data.values
    testdata = 0
    return traindata, testdata

def fit_model(traindata, testdata, y_col, x_cols):
    enet = linear_model.ElasticNetCV(l1_ratio=0.9, cv=10)
    enet.fit(traindata[:, x_cols], traindata[:, y_col])
    return enet

def plot_fit(data, model, x_cols):
    sns.set_style('darkgrid')
    results = pd.DataFrame({'param': [data.columns.tolist()[i] for i in x_cols],
                            'value': model.coef_})
    sns.factorplot('value', 'param', kind="bar", data=results, size=10, aspect=.7)
    plt.show()
