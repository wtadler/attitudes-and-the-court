import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def dta_preview(filename, nEntries = 100):
    reader = pd.read_stata(filename, iterator=True)
    df = reader.get_chunk(nEntries)
    
    return df

def load_dta(filename, chunksize = 5000, **kwargs):
	# use columns as a list
    import sys
    reader = pd.read_stata(filename, iterator=True, **kwargs)
    df = pd.DataFrame()

    try:
        chunk = reader.get_chunk(chunksize)
        i = 0
        while len(chunk) > 0:
            i += 1
            df = df.append(chunk, ignore_index=True)
            print 'Loaded {} rows...'.format(i*chunksize)
            sys.stdout.flush()
            chunk = reader.get_chunk(chunksize)
        print 'Done!'.format(len(df))
    except (StopIteration, KeyboardInterrupt, ValueError):
        pass

    

    return df

def plot_time_series(data, y, year_colname = 'year', title = '', n_label = True):
	years = data[year_colname].unique()
	mean = {}
	n = {}

	cat_strings = data[y].cat.categories
	for year in years:
		yeardata = data.loc[data[year_colname] == year]
		coded_y = pd.Categorical.from_array(yeardata[y]).codes
		mean[year] = np.mean(coded_y)
		n[year] = len(coded_y)

	plt.plot(years, [mean[year] for year in years])
	ax = plt.gca()
	ax.set_ylim([1, len(cat_strings)])
	ax.set_yticklabels(cat_strings)
	ax.set_title(title)
	if n_label:
		for year in years:
		    ax.text(year, mean[year], ' {}'.format(n[year]), rotation=55, verticalalignment='bottom', fontsize=9)