import getpass
import os
user = getpass.getuser()
os.chdir("/Users/"+user+"/GoogleDrive/NYU_GD/MLClass/project/gitVersion")
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import Imputer
from scipy import linalg
import functions as f


# Get relevant columns
import_cols = ['id', 'year', 'age','race', 'region', 'educ', 'relig','sex','fepol','fechld','fepresch','fefam','fehire','fejobaff','discaffm','meovrwrk']
# Note: fethink, fecare, discaffw , and fenewsare missing after 1995

gss = f.load_dta(f.data_loc('GSS7212_R2.DTA'), columns=import_cols, chunksize=None)
# Select only post 1995
gss = gss[gss.year>1995]


# Replace strings in age variable
gss.age = gss.age.cat.codes + 18
age_mean = gss.age.mean()
gss.age = gss.age.fillna(age_mean)

# map sex to numeric
gss.sex = gss.sex.map({'female': 0, 'male': 1}).astype(int)


# Recode attitude variables
gss.fepol = gss.fepol.map({'disagree': 0, 
						'not sure':1,
						'agree': 2},na_action='ignore')
gss.fechld = gss.fechld.map({'strongly disagree': 0, 
						'disagree': 1,
						'agree': 2,
						'strongly agree':3},na_action='ignore')
gss.fepresch = gss.fepresch.map({'strongly disagree': 0, 
						'disagree': 1,
						'agree': 2,
						'strongly agree':3},na_action='ignore')
gss.fefam = gss.fefam.map({'strongly disagree': 0, 
						'disagree': 1,
						'agree': 2,
						'strongly agree':3},na_action='ignore')

gss.fehire = gss.fehire.map({'strongly disagree': 0, 
						'disagree': 1,
						'neither agree nor disagree':2,
						'agree': 3,
						'strongly agree':4},na_action='ignore')
gss.fejobaff = gss.fejobaff.map({'strongly against': 0, 
						'against': 1,
						'for': 2,
						'strongly for':3},na_action='ignore')
gss.discaffm = gss.discaffm.map({'very unlikely': 0, 
						'somewhat unlikely': 1,
						'somewhat likely': 2,
						'very likely':3},na_action='ignore')
gss.meovrwrk = gss.meovrwrk.map({'strongly disagree': 0, 
						'disagree': 1,
						'agree': 2,
						'neither agree nor disagree':3,
						'strongly agree':4},na_action='ignore')


# Standardize columns
# print gss.groupby('year').mean()
# print gss.groupby('year').count()

gss['fepolS'] = (gss.fepol-np.nanmean(gss.fepol))/np.std(gss.fepol)
gss['fechldS'] = (gss.fechld-np.nanmean(gss.fechld))/np.std(gss.fechld)
gss['fepreschS'] = (gss.fepresch-np.nanmean(gss.fepresch))/np.std(gss.fepresch)
gss['fefamS'] = (gss.fefam-np.nanmean(gss.fefam))/np.std(gss.fefam)
gss['fejobaffS'] = (gss.fejobaff-np.nanmean(gss.fejobaff))/np.std(gss.fejobaff)
gss['fehireS'] = (gss.fehire-np.nanmean(gss.fehire))/np.std(gss.fehire)
gss['discaffmS'] = (gss.discaffm-np.nanmean(gss.discaffm))/np.std(gss.discaffm)
gss['meovrwrkS'] = (gss.meovrwrk-np.nanmean(gss.meovrwrk))/np.std(gss.meovrwrk)

varNames = np.array(['fepolS','fechldS','fepreschS','fefamS','fejobaffS','fehireS','meovrwrkS'])

# Before dropping data, let's keep the df for later.  
gssOrig = gss.copy()


# First, drop all rows that have 3 or more missing values 
gss.dropna(axis=0,thresh=3,subset=varNames,inplace=True)


# Then impute yearly mean values for remaining missing data points
for i, year in enumerate(np.unique(gss.year)):
	i_year = gss[gss.year == year].index.tolist()
	yearMeans = np.mean(gss.loc[i_year,varNames],axis=0)
	if sum(np.isnan(yearMeans)>0):
		 # Whole year is missing, so take mean of pre and post
		yearMeans['fejobaffS'] = -0.0461815
		yearMeans['fehireS'] = -0.047274999
		yearMeans['meovrwrkS'] = 0.1497375

	i_nan = ~gss.loc[i_year,varNames].notnull()

	for thisCol in varNames:
		ind = (gss.year == year) & gss[thisCol].isnull()
		gss.loc[ind,thisCol] = yearMeans[thisCol]



# Get columns from dataset
X = gss.loc[:,varNames].as_matrix()


# For others, impute missing values using column mean.... not sure if this is great. hmmm...
# print 'number of imputed missing values is: ' + str(np.sum(np.isnan(X))) + " out of "+ str(np.size(X))
# imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
# imp.fit(X)
# X= imp.transform(X) 


 # Run PCA
pca = PCA(n_components='mle')
pca.fit(X)

print np.round(pca.components_ * 100)/100
print(pca.explained_variance_ratio_) 

# Test if svd gives the same answer
# U, s, Vh = linalg.svd(X)
# print(Vh)

# Project all the data on first component
firstcomp = pca.components_[0]
data = gssOrig.loc[:,varNames].as_matrix()
data = np.nan_to_num(data)

gssOrig['genderValue'] = np.dot(data,firstcomp)

gssOrig.to_csv("composites/genderVar.csv",columns = ['id','year','genderValue'])
