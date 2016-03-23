import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys 

def dta_preview(filename, nEntries = 100):
    reader = pd.read_stata(filename, iterator=True)
    df = reader.get_chunk(nEntries)
    
    return df

def load_dta(filename, chunksize = 5000, **kwargs):
    # use columns as a list
    reader = pd.read_stata(filename, iterator=True, **kwargs)
    df = pd.DataFrame()

    try:
        chunk = reader.get_chunk(chunksize)

        i = 0
        while len(chunk) > 0:
            i += 1
            df = df.append(chunk, ignore_index=True)

            print 'Loaded {} rows...'.format(len(df))
            sys.stdout.flush()

            chunk = reader.get_chunk(chunksize)

        print 'Done!'
        return df

    except StopIteration: # I guess this is an acceptable exception?
        print 'Done!'
        return df

    except Exception as e:
        print type(e).__name__ + ': ' + str(e)
        return df

def plot_time_series(data, y, year_colname = 'year', title = '', n_label = True):
    # right now this works for categorical, yes-no, and strong/mild/no-agree data as a function of time.
    # todo: make it more flexible.

    data = data[data[y].notnull()] # toss out rows with missing y values.

    years = data[year_colname].unique()
    mean = {}
    n = {}

    cat_strings = data[y].cat.categories
    if (set(['yes', 'no']) & set(cat_strings)) == set(cat_strings):
        yesno = True
    else:
        yesno = False
    n_cats = len(cat_strings)

    for year in years:
        yeardata = data.loc[data[year_colname] == year]
        coded_y = pd.Categorical.from_array(yeardata[y]).codes
        mean[year] = np.mean(coded_y)
        n[year] = len(coded_y)

    plt.plot(years, [mean[year] for year in years])
    ax = plt.gca()
    if yesno:
        ax.set_ylim([-1, 1])
        ax.set_yticks([-1, 1])
    else:
        ax.set_ylim([1, n_cats])
        ax.set_yticks(1 + np.arange(n_cats))
    ax.set_yticklabels(cat_strings)
    ax.set_title(title)
    if n_label:
        for year in years:
            ax.text(year, mean[year], ' {}'.format(n[year]), rotation=55, verticalalignment='bottom', fontsize=9)

    return ax

def plot_court_cases(data, flip_vote = False, title = ''):
	if flip_vote:
		data['panelvote'] = 4 - data['panelvote']
	
	plt.plot(data['date'], data['panelvote'], 'o', markersize = 3, clip_on = False)
	ax = plt.gca()

	ax.set_ylim([0,3])
	ax.set_yticks(np.arange(4))
	ax.set_yticklabels(np.arange(4))
	ax.set_ylabel('# "progressive" votes')

	ax.set_title(title)

	return ax