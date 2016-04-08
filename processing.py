import pandas as pd
import numpy as np
import functions as f
from sklearn.preprocessing import StandardScaler

# processing of gss data before bringing court and gss together
def preprocess_gss(composite = 'genderVar.csv', extra_imports=[]):
    # choose cols to import. goes very slowly if you try to import everything
    # these seem like all of the relevant categories.
    import_cols = ['id', 'year', 'age',
                   'sex', 'race', 'region', 'educ', 'relig'] \
                   + extra_imports

    gss = f.load_dta(f.data_loc('GSS7212_R2.DTA'), columns=import_cols, chunksize=None)

    def numeric_fillna_standardize(x):
        x = x.cat.codes
        x.loc[x==-1] =  x[x!=-1].mean()
        x = StandardScaler().fit_transform(x.reshape(-1, 1))

        return x

    # map sex to numeric
    gss.sex = gss.sex.map({'female': 0, 'male': 1}).astype(int)

    # Standardize age, education, year
    gss.age = numeric_fillna_standardize(gss.age)
    gss.educ = numeric_fillna_standardize(gss.educ)
    gss.insert(3, 'year_norm', StandardScaler().fit_transform(gss.year.reshape(-1, 1).astype(float)))

    for col in extra_imports:
        categories = gss[col].cat.categories
        gss[col] = numeric_fillna_standardize(gss[col])
        # check this for other types of categories
        if 'strongly support pref' in categories:
            gss[col] = -gss[col]

    # change categorical variables to one-hot encoding
    gss = pd.concat([gss, pd.get_dummies(gss['race'], prefix='race')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['region'], prefix='region')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['relig'], prefix='relig')], axis=1)
    gss = gss.drop(['race', 'region', 'relig'], axis=1)

    if composite is not None:
        # prejudiceVar.csv has weird indexing. not sure how to line it up with the GSS
        compscore = pd.read_csv("composites/{}".format(composite), index_col='idx', usecols=['idx', 'genderValue'])
        gss = pd.merge(gss, compscore, left_index=True, right_index=True)
    
    return gss


# processing of court data before bringing court and gss together
def preprocess_court_data(max_lag=5):
    aff_ac = f.load_dta(f.data_loc('Circuit Cases/affirmative_action_panel_level.dta'), chunksize=None)
    race_discr = f.load_dta(f.data_loc('Circuit Cases/race_discrimination_panel_level.dta'), chunksize=None)
    sex_discr = f.load_dta(f.data_loc('Circuit Cases/sex_discrimination_panel_level.dta'), chunksize=None)

    aff_ac['casetype'] = "aff_ac"
    race_discr['casetype'] = "race_discr"
    sex_discr['casetype'] = "sex_discr"

    # join the two datasets, convert the date
    joint = pd.concat([aff_ac, race_discr])
    joint['date'] = pd.to_datetime(joint.year.astype(int)*10000 +
                                   joint.month.astype(int)*100 +
                                   np.random.randint(1, 29, size=len(joint)),
                                   format='%Y%m%d')

    # code votes by ideology
    joint['votelib'] = joint['panelvote']
    joint['votecons'] = 3 - joint['panelvote']
    # code
    joint['votelib'] = (joint['panelvote'] > 1.5).astype(float)

    # group cases by type and year
    groupby_year_type = joint.groupby(['casetype', 'year'])
    # take sum of liberal decisions and conservative decisions for each year
    groupby_year_type = groupby_year_type.votelib.agg({'cases_lib': np.sum, 'cases_cons': lambda x: np.size(x) - np.sum(x)}).reset_index()

    # lets just take affirmative action cases for now.
    # return number of liberal and conservative decisions, yearly lags, up to 5 years
    affirm_year = groupby_year_type[groupby_year_type['casetype'] == 'aff_ac'].set_index('year')
    years = []
    lags = []
    casesums_lib = np.array([])
    casesums_cons = np.array([])
    for y in range(1985, 2005):
        for l in range(1, 1+max_lag):
            years.append(y)
            lags.append(l)
            casesums_lib = np.append(casesums_lib, affirm_year.loc[y-l, 'cases_lib'])
            casesums_cons = np.append(casesums_cons, affirm_year.loc[y-l, 'cases_cons'])
    casesums_lib = (casesums_lib - casesums_lib.mean())/casesums_lib.std()
    casesums_cons = (casesums_cons - casesums_cons.mean())/casesums_cons.std()

    affirm_5yr = pd.DataFrame({'year': years, 'lag': lags, 'casesum_lib': casesums_lib, 'casesum_cons': casesums_cons})
    affirm_5yr = affirm_5yr.set_index(['year', 'lag'])
    return affirm_5yr


def process_combined_data(gss, court, y_name):
    # drop all rows where y variable is NA.
    gss = gss[gss[y_name].notnull()]

    # drop years without court case history
    court_years = court.index.levels[0]
    gss = gss[(gss['year'] >= court_years[0]) & (gss['year'] <= court_years[-1])]
    gss = gss.reset_index()

    # # add variables for last 5 years court cases. affrmact has been asked from 1994. this tracks changes only over 10 years.
    # for year in gss['year'].unique():
    #     for l in range(1, 6):
    #         gss.loc[gss['year'] == year, 'courtlag_lib' + str(l)] = court.loc[(year, l), 'casesum_lib']
    #         gss.loc[gss['year'] == year, 'courtlag_cons' + str(l)] = court.loc[(year, l), 'casesum_cons']
    for year in gss['year'].unique():
        gss.loc[gss['year'] == year, 'court_lib'] = court.loc[(year, 1), 'casesum_lib'] + \
                                                    court.loc[(year, 2), 'casesum_lib'] + \
                                                    court.loc[(year, 3), 'casesum_lib']
        gss.loc[gss['year'] == year, 'court_cons'] = court.loc[(year, 1), 'casesum_cons'] + \
                                                     court.loc[(year, 2), 'casesum_cons'] + \
                                                     court.loc[(year, 3), 'casesum_cons']

    # add interactions with time
    columns = gss.columns.tolist()
    columns = [c for c in columns if c.startswith(('age', 'sex', 'educ', 'race_', 'region_', 'relig_'))]
    for c in columns:
        gss[c + '_X_year'] = gss[c] * gss['year_norm']

    # cross race with region and religion
    columns = gss.columns.tolist()
    columns = [c for c in columns if c.startswith(('region_', 'relig_'))]
    for c in columns:
        for race in ['white', 'black', 'other']:
            gss[race + '_X_' + c] = gss[c] * gss['race_' + race]

    # cross all columns with number of liberal/conservative decisions in 3 years prior to survey
    columns = gss.columns.tolist()
    columns = [c for c in columns if c.startswith(('age', 'sex', 'educ', 'race_', 'region_', 'relig_'))]
    for decisiontype in ['lib', 'cons']:
        # for lag in range(1,6):
        for c in columns:
            gss[c + '_X_' + decisiontype] = gss[c] * gss['court_' + decisiontype]
    
    columns = gss.columns.tolist()
    y_column = gss.columns.get_loc(y_name)

    x_columns = [i for i in range(gss.shape[1]) if columns[i] not in ['id', 'index', y_name]]
    
    return gss, y_column, x_columns