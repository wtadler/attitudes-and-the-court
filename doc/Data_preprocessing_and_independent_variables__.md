# Data preprocessing and independent variables

## GSS predictors

When testing for the impact of course cases in our modeling section below, we controlled for various demographic variables from the GSS.
Specifically, we used the following variables as predictors in our model(s). 

- age (years)
- sex (male; female)
- education (years)
- race (black; white; other)
- region (New England; Middle Atlantic; Mountain; Pacific; South Atlantic;
East-North Central; East-South Central; West-North Central; West-South
Central)
- religion (Buddhist; Catholic; Christian; Hindu; inter/nondenominational;
Jewish; Muslim; Native American; Orthodox Christian; Protestant; Other
Eastern; Other; None)

For discrete predictors, we used one-hot encoding. Continuous variables were standardized to have zero mean and unit variance.
Along with these predictors, we also included race-by-region and race-by-religion interactions, and interactions of 
all demographic predictors with year in which the survey was administered.

## Court case predictors
For each case, we computed the difference between the judge ideology on a given panel and its expected value. To calculate this, we took the proportion of judges who were appointed by Democratic presidents on each panel, and subtracted the expected proportion based on the overall pool of judges in the circuit at the time of the case.

We then grouped court cases by circuit and year, and aggregated them in different temporal time windows ranging from 1 to 10 years. For each time window and each circuit we computed the *number of liberal* and the *number of conservative decisions*, as well as the summed *difference of judge ideology from expectation* value described above.


## Integrating the data sources
We removed GSS data for years in which court data was unavailable, and merged the three court predictors with the GSS demographics predictors by year and circuit (the "circuit" of a GSS respondent was determined by the region they resided in).
For each court predictor, we added interactions of court-predictor-by-year, and court-predictor-by-demographic for each demographic variable.