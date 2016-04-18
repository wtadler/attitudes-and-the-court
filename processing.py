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

    state_info = pd.read_csv('data/gssstate7304.csv')


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

    for col in extra_imports:
        categories = gss[col].cat.categories
        gss[col] = numeric_fillna_standardize(gss[col])
        # check this for other types of categories
        if 'strongly support pref' in categories:
            gss[col] = -gss[col]

    gss = pd.merge(gss, state_info, on=["id", "year"])
    gss.relig = gss.relig.astype('category')
    gss.race = gss.race.astype('category')
    gss.region = gss.region.astype('category')

    gss.loc[gss.fipsstat.isin([23, 25, 33, 44]), "circuit"] = 1
    gss.loc[gss.fipsstat.isin([9, 36, 50]), "circuit"] = 2
    gss.loc[gss.fipsstat.isin([10, 34, 42]), "circuit"] = 3
    gss.loc[gss.fipsstat.isin([24, 37, 45, 51, 54]), "circuit"] = 4
    gss.loc[gss.fipsstat.isin([22, 28, 48]), "circuit"] = 5
    gss.loc[gss.fipsstat.isin([21, 26, 39, 47]), "circuit"] = 6
    gss.loc[gss.fipsstat.isin([17, 18, 55]), "circuit"] = 7
    gss.loc[gss.fipsstat.isin([5, 19, 27, 29, 31, 38, 46]), "circuit"] = 8
    gss.loc[gss.fipsstat.isin([2, 4, 6, 15, 16, 30, 32, 41, 53]), "circuit"] = 9
    gss.loc[gss.fipsstat.isin([8, 20, 35, 40, 49, 56]), "circuit"] = 10
    gss.loc[gss.fipsstat.isin([1, 12, 13]), "circuit"] = 11
    gss.loc[gss.fipsstat.isin([11]), "circuit"] = 12


    gss.insert(3, 'year_norm', StandardScaler().fit_transform(gss.year.reshape(-1, 1).astype(float)))


    # change categorical variables to one-hot encoding
    gss = pd.concat([gss, pd.get_dummies(gss['race'], prefix='race')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['region'], prefix='region')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['relig'], prefix='relig')], axis=1)
    gss = gss.drop(['race', 'region', 'relig'], axis=1)

    if composite is not None:
        # prejudiceVar.csv has weird indexing. not sure how to line it up with the GSS
        compscore = pd.read_csv("composites/{}".format(composite), index_col='Unnamed: 0', usecols=['Unnamed: 0', 'genderValue'])
        gss = pd.merge(gss, compscore, left_index=True, right_index=True)

    return gss


# processing of court data before bringing court and gss together
def preprocess_court_data(summing_window=5):
    # to do: parameterize court case set, get judge bio difference from expectation for each case

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
    groupby_year_type = joint.groupby(['casetype', 'circuit', 'year'])
    # take sum of liberal decisions and conservative decisions for each year
    groupby_year_type = groupby_year_type.votelib.agg({'cases_lib': np.sum, 'cases_cons': lambda x: np.size(x) - np.sum(x)}).reset_index()

    affirm_year = groupby_year_type[groupby_year_type['casetype'] == 'aff_ac'].set_index(['circuit', 'year'])

    new_index = pd.MultiIndex.from_tuples([(c,y) for c in range(1,13) for y in range(1985, 2006)], names=['circuit', 'year'])

    affirm_year = affirm_year.reindex(new_index)
    affirm_year.cases_lib.fillna(0, inplace=True)
    affirm_year.cases_cons.fillna(0, inplace=True)
    affirm_year.casetype.fillna("aff_ac", inplace=True)


    affirm_year_grouped = affirm_year.groupby(level='circuit')

    cases_cons = affirm_year_grouped.cases_cons.apply(lambda x: x.rolling(window=summing_window, center=False).sum())
    cases_lib = affirm_year_grouped.cases_lib.apply(lambda x: x.rolling(window=summing_window, center=False).sum())

    affirm_year.cases_cons = cases_cons
    affirm_year.cases_lib = cases_lib


    affirm_year = affirm_year[affirm_year.cases_cons.notnull()].reset_index()
    return affirm_year


def process_combined_data(gss, court, y_name):
    # drop all rows where y variable is NA.
    gss = gss[gss[y_name].notnull()]

    # drop years without court case history
    court_years = court.year.unique()
    gss = gss[(gss['year'] >= court_years[0]) & (gss['year'] <= court_years[-1])]
    gss = gss.reset_index()

    court = court.set_index(["circuit", "year"])
    for year in gss['year'].unique():
        for circuit in gss['circuit'].unique():
            gss.loc[(gss['year'] == year) & (gss['circuit'] == circuit), 'court_lib'] = court.loc[(circuit, year), 'cases_lib']
            gss.loc[(gss['year'] == year) & (gss['circuit'] == circuit), 'court_cons'] = court.loc[(circuit, year), 'cases_cons']

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
    columns = [c for c in columns if (c.startswith(('age', 'sex', 'educ', 'race_', 'region_', 'relig_')) and (not 'year' in c))]
    for decisiontype in ['lib', 'cons']:
        # for lag in range(1,6):
        for c in columns:
            gss[c + '_X_' + decisiontype] = gss[c] * gss['court_' + decisiontype]
    
    columns = gss.columns.tolist()
    y_column = gss.columns.get_loc(y_name)

    x_columns = [i for i in range(gss.shape[1]) if columns[i] not in ['id', 'year', 'state', 'fipsstat', 'index', y_name]]
    
    return gss, y_column, x_columns
