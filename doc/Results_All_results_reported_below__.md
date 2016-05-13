
# Results

All results reported below are calculated based on ten runs of the model, using a different randomly selected 10% of the GSS data held out as a test set on each run.

## Null model: Demographics only
When predicting the gender conservatism index using demographic predictors alone, we achieved an \(R^2\) of ~.11 on the training set, and ~.092  on the test set.

## Full model: Demographics and court data
We tested two versions of the full model that included the court data in addition to demographic predictors. 
First, we tested a model with court decisions (no. of conservative/liberal decisions) over different time windows along with the judge ideology predictor (difference from expectation in each time window).
Second, we also tested a model with only the judge ideology predictor. Since judges are randomly chosen from a large pool, their impact on attitudes counts as an interesting “natural experiment.”


Across all temporal windows tested (1 to 10 years), the addition of information from
recent circuit court decisions did not improve the prediction of gender conservatism in our test set. This is illustrated by Figure 2, which shows the \(R^2\) by model type (demographics only or demographics + court), time window, and dataset (training or test). On the test set, the full models' performance is consistently worse than those of the null model.

Although we were unable to detect any impact from the court decisions on the gender conservatism index, a number of demographic variables proved reliably predictive of gender conservatism. As Figure 3 shows, among the most reliable predictors were age, gender, race, education, and religion of the respondent. 
