import pandas as pd
import numpy as np
import functions as f

# processing of gss data before bringing court and gss together
def preprocess_gss():
    # choose cols to import. goes very slowly if you try to import everything
    # these seem like all of the relevant categories.
    import_cols = ['id', 'affrmact', 'year', 'age',
                   'sex', 'race', 'region', 'educ', 'relig']

    gss = f.load_dta(f.data_loc('GSS7212_R2.DTA'), columns=import_cols, chunksize=None)

    # THESE LINES ADD ANNA'S COMPOSITE SCORE. COMMENTED OUT FOR NOW
    # prej = pd.read_csv("composites/prejudiceVar.csv")
    # gss = gss.merge(prej, 'left', on=["year","id"])

    # change age to number (89+ just coded as 89)
    gss.age = gss.age.cat.codes + 18
    age_mean = gss.age.mean()
    gss.age = gss.age.fillna(age_mean)
    gss.age = (gss.age - gss.age.mean())/gss.age.std()

    # map sex to numeric
    gss.sex = gss.sex.map({'female': 0, 'male': 1}).astype(int)

    # fill in missing educ values with mean
    gss.educ = gss.educ.cat.codes
    educ_mean = gss.educ.mean()
    gss.educ = gss.educ.replace(-1, educ_mean)
    gss.educ = (gss.educ - gss.educ.mean())/gss.educ.std()
    gss.insert(3, 'year_norm', (gss.year-gss.year.mean())/gss.year.std())

    # change categorical variables to one-hot encoding
    gss = pd.concat([gss, pd.get_dummies(gss['race'], prefix='race')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['region'], prefix='region')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['relig'], prefix='relig')], axis=1)
    gss = gss.drop(['race', 'region', 'relig'], axis=1)
    return gss


# processing of court data before bringing court and gss together
def preprocess_court_data():
    aff_ac = f.load_dta(f.data_loc('Circuit Cases/affirmative_action_panel_level.dta'), chunksize=None)
    race_discr = f.load_dta(f.data_loc('Circuit Cases/race_discrimination_panel_level.dta'), chunksize=None)

    aff_ac['casetype'] = "aff_ac"
    race_discr['casetype'] = "race_discr"

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
    casesums_lib = []
    casesums_cons = []
    for y in range(1985, 2005):
        for l in range(1, 6):
            years.append(y)
            lags.append(l)
            casesums_lib.append(affirm_year.loc[y-l, 'cases_lib'])
            casesums_cons.append(affirm_year.loc[y-l, 'cases_cons'])
    affirm_5yr = pd.DataFrame({'year': years, 'lag': lags, 'casesum_lib': casesums_lib, 'casesum_cons': casesums_cons})
    affirm_5yr = affirm_5yr.set_index(['year', 'lag'])
    return affirm_5yr


def process_combined_data(gss, court, y_name):
    # drop all rows where y variable is NA.
    gss = gss[gss[y_name].notnull()]

    # change affrmact to numeric
    gss[y_name] = gss[y_name].map({'strongly support pref': 1.5,
                                   'support pref': .5,
                                   'oppose pref': -.5,
                                   'strongly oppose pref': -1.5})

    # drop years without court case history
    court_years = court.index.levels[0]
    gss = gss[(gss['year'] >= court_years[0]) & (gss['year'] <= court_years[-1])]
    gss = gss.reset_index()

    court.casesum_lib = (court.casesum_lib - court.casesum_lib.mean())/court.casesum_lib.std()
    court.casesum_cons = (court.casesum_cons - court.casesum_cons.mean())/court.casesum_cons.std()

    # add variables for last 5 years court cases. affrmact has been asked from 1994. this tracks changes only over 10 years.
    for year in gss['year'].unique():
        for l in range(1, 6):
            gss.loc[gss['year'] == year, 'courtlag_lib' + str(l)] = court.loc[(year, l), 'casesum_lib']
            gss.loc[gss['year'] == year, 'courtlag_cons' + str(l)] = court.loc[(year, l), 'casesum_cons']

    # add interactions with time
    columns = gss.columns.tolist()
    columns = [c for c in columns if c.startswith(('age', 'sex', 'educ', 'race_', 'region_', 'relig_'))]
    for c in columns:
        gss[c + '_X_year'] = gss[c] * gss['year_norm']
    y_column = gss.columns.get_loc(y_name)
    x_columns = range(4, gss.shape[1])
    return gss, y_column, x_columns
