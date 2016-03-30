import pandas as pd
import numpy as np
import functions as f

# processing of gss data before bringing court and gss together
def preprocess_gss():
    # choose cols to import. goes very slowly if you try to import everything,
    # and some cols make it error. see file
    import_cols = ['id', 'affrmact', 'year', 'age', 'sex', 'race', 'region', 'educ', 'relig']
    # these seem like all of the relevant categories. Some of them don't plot nicely yet.
    # chunksize must be None or >= 57061 rows (for GSS), because of pandas flaw
    gss = f.load_dta(f.data_loc('GSS7212_R2.DTA'), chunksize = None,
                     columns = import_cols)

    # THESE LINES ADD ANNA'S COMPOSITE SCORE. COMMENTED OUT FOR NOW
    # prej = pd.read_csv("composites/prejudiceVar.csv")
    # gss = gss.merge(prej, 'left', on=["year","id"])

    # change age to number (89+ just coded as 89)
    gss.age = gss.age.cat.codes + 18
    age_mean = gss.age.mean()
    gss.age = gss.age.fillna(age_mean)
    # map sex to numeric
    gss.sex = gss.sex.map({'female': 0, 'male': 1}).astype(int)
    # fill in missing educ values with mean
    gss.educ = gss.educ.cat.codes
    educ_mean = gss.educ.mean()
    gss.educ = gss.educ.replace(-1, educ_mean)
    gss.insert(3, 'year_norm', gss.year-gss.year.mean())
    # change categorical variables to one-hot encoding
    gss = pd.concat([gss, pd.get_dummies(gss['race'], prefix='race')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['region'], prefix='region')], axis=1)
    gss = pd.concat([gss, pd.get_dummies(gss['relig'], prefix='relig')], axis=1)
    gss = gss.drop(['race', 'region', 'relig'], axis=1)
    return gss


# processing of court data before bringing court and gss together
def preprocess_court_data():
    # chunksize must be None or >= 57061 rows (for GSS), because of pandas flaw
    aff_ac = f.load_dta(f.data_loc('Circuit Cases/affirmative_action_panel_level.dta'), chunksize = None)
    race_discr = f.load_dta(f.data_loc('Circuit Cases/race_discrimination_panel_level.dta'), chunksize = None)

    aff_ac['casetype'] = "aff_ac"
    race_discr['casetype'] = "race_discr"

    # join the two datasets, convert the date
    joint = pd.concat([aff_ac, race_discr])
    joint['date'] = pd.to_datetime(joint.year.astype(int)*10000 + \
                                   joint.month.astype(int)*100 + \
                                   np.random.randint(1, 29, size = len(joint)), format='%Y%m%d')
    joint['votelib'] = joint['panelvote']
    joint['votecons'] = 3 - joint['panelvote']
    joint['votenorm'] = 1.5 - joint['panelvote']
    groupby_year_type = joint.groupby(['casetype', 'year'])
    groupby_year_type = groupby_year_type.votenorm.aggregate(np.sum).reset_index()
    # lets just take affirmative action cases for now
    affirm_year = groupby_year_type[groupby_year_type['casetype']=='aff_ac'].set_index('year')
    years = []
    lags = []
    casesums = []
    for y in range(1985, 2005):
        for l in range(1, 6):
            years.append(y)
            lags.append(l)
            casesums.append(affirm_year.loc[y-l, 'votenorm'])
    affirm_5yr = pd.DataFrame({'year': years, 'lag': lags, 'casesum': casesums})
    affirm_5yr = affirm_5yr.set_index(['year', 'lag'])
    return affirm_5yr


def process_combined_data(gss, court):
    # drop all rows where y variable is NA
    gss = gss[gss['affrmact'].notnull()]
    # change racdin to numeric
    gss.affrmact = gss.affrmact.map({'strongly support pref': 1.5, 'support pref': .5,
                                     'oppose pref': -.5, 'strongly oppose pref': -1.5})
    # drop years without court case history
    gss = gss[(gss['year'] > 1984) & (gss['year'] < 2005)]
    gss = gss.reset_index()
    # add variables for last 5 years court cases
    # this takes a few seconds...
    for l in range(1, 6):
        gss['courtlag' + str(l)] = 0
    for i in range(len(gss)):
        curr_year = gss.loc[i, 'year']
        for l in range(1, 6):
            gss.loc[i, 'courtlag' + str(l)] = court.loc[(curr_year, l), 'casesum']
    # add interactions with time
    columns = gss.columns.tolist()
    for c in columns[5:]:
        gss[c + '_X_year'] = gss[c] * gss['year_norm']
    y_column = 2
    x_columns = range(4, gss.shape[1])
    return gss, y_column, x_columns

