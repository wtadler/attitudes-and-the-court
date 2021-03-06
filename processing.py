import pandas as pd
import numpy as np
import functions as f
from sklearn.preprocessing import StandardScaler

# processing of gss data before bringing court and gss together
def preprocess_gss(composite = 'genderVar.csv', extra_imports=[], convert_to_one_hot=True):
    # choose cols to import. goes very slowly if you try to import everything
    # these seem like all of the relevant categories.
    import_cols = ['id', 'year', 'age',
                   'sex', 'race', 'region', 'educ', 'relig', 'news'] \
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
    gss.news = -numeric_fillna_standardize(gss.news)

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

    # modern 11th circuit was 5th circuit before 1982
    gss.loc[(gss.circuit==11) & (gss.year<1982), 'circuit'] = 5

    gss.insert(3, 'year_norm', StandardScaler().fit_transform(gss.year.reshape(-1, 1).astype(float)))

    if convert_to_one_hot:
        # change categorical variables to one-hot encoding
        gss = pd.concat([gss, pd.get_dummies(gss['race'], prefix='race')], axis=1)
        gss = pd.concat([gss, pd.get_dummies(gss['region'], prefix='region')], axis=1)
        gss = pd.concat([gss, pd.get_dummies(gss['relig'], prefix='relig')], axis=1)
        gss = gss.drop(['race', 'region', 'relig'], axis=1)

    if composite is not None:
        # prejudiceVar.csv has weird indexing. not sure how to line it up with the GSS
        compscore = pd.read_csv("composites/{}".format(composite), usecols = ['id', 'year', 'genderValue'])
        gss = gss.merge(compscore, 'left', on=["year","id"])

    return gss


# processing of court data before bringing court and gss together
def preprocess_court_data(summing_window=5, cases='sex_discr', include_decisions=True):
    case_data = process_court_data_alone(cases)

    case_data['lib_judge_diff'] = case_data['x_dem'] - case_data['E_x_dem']
    # case_data['cons_judge_diff'] = case_data['x_repub']-case_data['E_x_repub']

    # strip away most columns
    cols = ['year', 'circuit', 'lib_judge_diff']
    if include_decisions:
        cols.extend(['lib_decision', 'cons_decision'])
    case_data = case_data[cols]

    # group cases by type and year
    grouped = case_data.groupby(['circuit', 'year'])

    # take sum of liberal decisions and conservative decisions for each year
    # grouped = grouped.votelib.agg({'cases_lib': np.sum, 'cases_cons': lambda x: np.size(x) - np.sum(x)}).reset_index()
    grouped = grouped.aggregate(np.sum) # just sum everything

    # affirm_year = grouped[grouped['casetype'] == 'aff_ac'].set_index(['circuit', 'year'])

    new_index = pd.MultiIndex.from_tuples([(c,y) for c in range(1,13) for y in range(int(case_data.year.min()), int(case_data.year.max())+1)], names=['circuit', 'year'])

    grouped = grouped.reindex(new_index)
    grouped.lib_judge_diff.fillna(0, inplace=True)
    if include_decisions:
        grouped.lib_decision.fillna(0, inplace=True)
        grouped.cons_decision.fillna(0, inplace=True)

    groupby = grouped.groupby(level='circuit')

    lib_judge_diff_window = groupby.lib_judge_diff.apply(lambda x: x.rolling(window=summing_window, center=False).sum())

    if include_decisions:
        lib_decision_window = groupby.lib_decision.apply(lambda x: x.rolling(window=summing_window, center=False).sum())
        cons_decision_window = groupby.cons_decision.apply(lambda x: x.rolling(window=summing_window, center=False).sum())
        grouped['lib_decision_window'] = lib_decision_window
        grouped['cons_decision_window'] = cons_decision_window

    grouped['lib_judge_diff_window'] = lib_judge_diff_window

    grouped = grouped[grouped.lib_judge_diff_window.notnull()].reset_index()
    return grouped


def process_court_data_alone(cases='sex_discr'):
    if cases=='sex_discr':
        filename = 'Circuit Cases/affirmative_action_panel_level.dta'
    elif cases=='race_discr':
        filename = 'Circuit Cases/race_discrimination_panel_level.dta'
    elif cases=='aff_ac':
        filename = 'Circuit Cases/affirmative_action_panel_level.dta'

    case_data = f.load_dta(f.data_loc(filename), chunksize=None)

    case_data['date'] = pd.to_datetime(case_data.year.astype(int)*10000 +
                                   case_data.month.astype(int)*100 +
                                   np.random.randint(1, 29, size=len(case_data)),
                                   format='%Y%m%d')

    # code votes by ideology
    # case_data['votelib'] = case_data['panelvote']
    # case_data['votecons'] = 3 - case_data['panelvote']
    case_data['lib_decision'] = (case_data['panelvote'] > 1.5).astype(float)
    case_data['cons_decision'] = (case_data['panelvote'] < 1.5).astype(float)

    return case_data


def process_combined_data(gss, court, y_name):
    # drop all rows where y variable is NA.
    gss = gss[gss[y_name].notnull()]

    # drop years without court case history
    court_years = court.year.unique()
    gss = gss[(gss['year'] >= court_years[0]) & (gss['year'] <= court_years[-1])]
    gss = gss.reset_index()

    court = court.set_index(["circuit", "year"])
    courtvars = list(set(['lib_decision_window', 'cons_decision_window', 'lib_judge_diff_window']) & set(court.columns)) # because decision_info might not be there

    for year in gss['year'].unique():
        for circuit in gss['circuit'].unique():
            for courtvar in courtvars:
                try: # try, because lib_decision_window and cons_decision_window
                    gss.loc[(gss['year'] == year) & (gss['circuit'] == circuit), courtvar] = court.loc[(circuit, year), courtvar]
                except:
                    pass

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
    for courtvar in courtvars:
        # for lag in range(1,6):
        for c in columns:
            gss[c + '_X_' + courtvar] = gss[c] * gss[courtvar]
    for courtvar in courtvars:
        # for lag in range(1,6):
        for c in gss.columns.tolist():
            if courtvar in c:
                gss[c + '_X_' + "news"] = gss[c] * gss['news']
    
    columns = gss.columns.tolist()
    y_column = gss.columns.get_loc(y_name)

    x_columns = [i for i in range(gss.shape[1]) if columns[i] not in ['id', 'year', 'state', 'fipsstat', 'index', y_name]]
    x_columns_nocourt = [i for i in range(gss.shape[1]) if (columns[i] not in ['id', 'year', 'state', 'fipsstat', 'index', y_name] and not 'window' in columns[i])]
    
    return gss, y_column, x_columns, x_columns_nocourt