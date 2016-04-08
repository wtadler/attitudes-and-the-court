import processing
import modeling
import matplotlib.pyplot as plt

# comment out as needed
import os
# os.chdir('/Local/Users/adler/attitudes-and-the-court')
# %matplotlib qt
import numpy.random as random
random.seed(seed=43)
# plt.ion()
reload(processing)
gss = processing.preprocess_gss()
court = processing.preprocess_court_data()

data, y_col, x_cols = processing.process_combined_data(gss, court, 'genderValue')

train, test = modeling.split_train_test(data)

model = modeling.fit_model(train, test, y_col, x_cols)

modeling.plot_fit(data, model, x_cols)
