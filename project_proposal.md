---
title: Attitudes and the court project proposal
author: Will Adler, Anna Coenen, Alex Rich (Advisor Daniel Chen)
---


# Problem Overview

Federal US circuit courts often make rulings in areas that are socially or
politically relevant to the American public, such as capital punishment,
affirmative action, gay rights, environmental protection, and abortion. In this
project, we seek to measure how these rulings may affect Americans' social and
political attitudes. Our goal is to determine whether court rulings tend to move
attitudes in the direction "intended" by the ruling (e.g., towards acceptance of
gays when a ruling expands gay rights), or whether rulings tend to move
attitudes in the opposite direction (i.e., cause backlash) or polarize attitudes.

# Data sets

We will use two main data sets for our analyses. The first is the US General Social
Survey (GSS), which records the social and political attitudes as well as demographic
information for a representative sample of 57,061 Americans since 1972. The GSS has about 5,000 questions, though much of the data is missing. The second is a
data set of US circuit court decisions for 6,500 cases. These cases are coded
by topic (capital punishment, criminal appeals, etc.), and by the proportion of
the three-court panel that voted in the more liberal or more conservative
direction. The meaning of the ruling coding depends on the topic; for example
rulings would be coded as pro-life or pro-choice in the case of an abortion
case. The court data also includes demographic information about all judges on
the panel, including the party of their appointing president.

# Evaluation of performance

Our measure of performance will be the degree to which the inclusion of court
ruling data improves the forecasting of attitude trends over time-series analysis
using the GSS data alone. This will require two models: one that includes both
GSS predictors and court data predictors, and one that uses GSS predictors alone.

# Planned approach

We intend to tackle this problem iteratively, by gradually increasing the
complexity and size of both the models used and the data to which the models are applied.

Rather than immediately apply our models to the entire set of GSS data or court
case data, we plan to begin our analyses with a reduced data set. To do this, we
will choose a single court case topic (e.g., affirmative action), and a single
composite measure of attitudes (e.g., racism) from the GSS developed by previous
researchers. This will allow us to confirm the feasibility of our approach
before increasing the dimensionality of our predictors and outcome variables.

While we do not have prior experience in time series analyses, our current plan
is to use the ARIMA family of models for our analyses. Our first ARIMA model
will simply predict the value of a given attitude over time using past values of
that attitude, thus capturing basic trends in the attitude data. We will then
add the court case rulings and the time of their occurrence as an additional set
of predictors, and estimate the improvement of performance. Following this first
step, we will then continue to improve our model by incorporating more
predictors of attitudes from the GSS data (e.g., demographic information), as
well as including the court predictors in more sophisticated ways (e.g.,
allowing lagged effects of rulings, allowing rulings to interact with
demographics). At all points, we will maintain versions of the model with and
without the court data predictors, so we can measure the forecasting power of
the court results as opposed to other trends.
