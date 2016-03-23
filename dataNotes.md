# Court case data

## File: race\_discrimination\_panel\_level.dta

* 100 cases
* panelvote column codes for anti-discrimination votes
* very limited date range: 1995 - 2004


## File: affirmative\_action\_panel\_level.dta

* 153 cases
* panelvote column codes for pro affirmative action votes
* date range: 1980 - 2003
* potential problem: perhaps not all of these are race-based (although all of those I checked were..)

# General Social Survey data

* 57061 rows
* some columns raise `ValueError: Categorical categories must be unique` ([see Stack Overflow](http://stackoverflow.com/questions/31782283/loading-stata-file-categorial-values-must-be-unique)). Will has discovered these so far, but hasn't looked systematically:
	* `age`
	* `zodiac`
* in categorical pandas data, every category is assigned an integer. A -1 codes for a blank (NaN) entry. I modified `plot_time_series()` to toss out empty rows, but thought I'd note it here in case it comes up again.