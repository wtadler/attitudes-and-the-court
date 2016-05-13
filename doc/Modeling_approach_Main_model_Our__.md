

# Modeling approach

## Main model
Our main challenge in modeling these data was to strike a balance between predictive accuracy and interpretability. On the one hand, we wanted 
to make sure that our model was not overfitting the data and made good predictions. On the other hand, the question of this project required
us to use a method that allowed us to draw inferences about the impact of specific predictors. 

To make sure the results were easy to interpret, we chose to model the data using linear regression. To make sure our model does not overfit, we regularized it using L1 regularization (proportion=.9) and L2 regularization
(proportion=.1). This elastic net approach gave us the benefit of sparsity of the solution (due to L1 regularization), while stabilizing our estimates from correlated predictors via a small amount of L2 regularization. We chose the total amount of regularization using 10-fold cross-validation within the training set and chose the value that yielded the lowest average error.


## Alternative models
In addition to the regularized linear regression, we also tried a number of other machine learning algorithms to model our data. Each of these approaches yielded similar results as our main analysis regarding the impact of court predictors. Since their outcomes are more difficult to interpret, we chose to present results only from the linear regression.

Specifically, we tried the following algorithms.

* regression with a decision tree
* regression with a random forest
* regression with AdaBoost


 <!---
* dropping data from respondents for whom no court case had occured in their circuit within the temporal window
--->

In all cases, court-related predictors decreased performance on the validation set.
