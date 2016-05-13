
# Dependent variable: Index of conservative attitudes about gender roles

## Approach 
Our dependent variable was people's attitudes towards gender roles. To operationalize these attitudes, we used 7 questions from the GSS that asked for people's opinions on gender roles (see below). To arrive at a single outcome measure, we performed a Principal Components Analysis (PCA) as a method of dimensionality reduction.
Before fitting the PCA, we standardized the answers to each question to have variance of 1 and mean of 0.
To handle missing data, we excluded every respondent who answered only four or fewer of the 7 questions. Otherwise, missing values were imputed using the average response to a given question by other respondents in the same year. 

PCA performs a total least squares regression on a number of variables to find the dimensions that can explain the most (or least) amount of variance in the data. Each principle component is an eigenvector of the data's covariance matrix (\(D^TD\)) and the amount of variance it explains is the corresponding eigenvalue. 

## Resulting measure
The first principle component of the 7 gender questions from the GSS explained 36% of the variance in the data
and by examining its coefficients for each question, we confirmed that it captures respondents' level of conservatism regarding gender roles. The following table summarizes the coefficients per question. 


| GSS Statement | Coefficient of 1st principal component |
|------------|------------------------------------------|
| A working mother can establish just as warm and secure a relationship with her children as a mother who does not work.   | -0.53      |
| Because of past discrimination, employers should make special efforts to hire and promote qualified women.     | -0.02      |
| I favor the preferential hiring and promotion of women. | 0          |
| Most men are better suited emotionally for politics than are most women. | 0.3        |
| It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.   | 0.54       |
| Family life often suffers because men concentrate too much on their work. | 0.54       |
| A preschool child is likely to suffer if his or her mother works.      | 0.56       |

<br>
After projecting the question data on this component, participants with more traditional views on gender roles (assigning more domestic responsibilities to women and more professional ones to men)  end up with higher values than more progressive respondents. In the rest of this report we will use this measure as our dependent variable, which we refer to as the _gender conservatism index_. 


