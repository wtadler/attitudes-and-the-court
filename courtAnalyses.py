import getpass
import os
# user = getpass.getuser()
# os.chdir("/Users/"+user+"/GoogleDrive/NYU_GD/MLClass/project/gitVersion/")


import processing
import modeling
import matplotlib.pyplot as plt
import os
import numpy.random as random
random.seed(seed=43)
plt.ion()



data = processing.process_court_data_alone()
analysisData = data.copy()

dropCols = [c for c in analysisData.columns if c.startswith(('E_x_'))]
dropCols = dropCols + ['date','case_ID','year','month',
'case_name','casecategory','nr_Judges','cons_decision','panelvote','circuit']

analysisData = analysisData.drop(dropCols,axis=1)

y_col = analysisData.columns.get_loc('lib_decision')
x_cols = range(analysisData.shape[1])
del x_cols[y_col]

# Get train and test data and fit training data
train, test = modeling.split_train_test(analysisData)
thisModel = linear_model.SGDClassifier(loss="log", penalty="elasticnet",l1_ratio=0.9)
thisModel.fit(train[:, x_cols], train[:, y_col])

# Plot!
modeling.plot_fit(analysisData, thisModel, range(np.shape(train)[1]-1),binary=True)
plt.draw()
