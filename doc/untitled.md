


# Question

Federal US circuit courts often make rulings in areas that are socially 
relevant to the American public, such as capital punishment,
affirmative action, or racial discrimination. In this
project, we seek to measure how these rulings may affect Americans' social and
political attitudes. Our goal is to determine whether court rulings tend to move
attitudes in the direction "intended" by the ruling or whether rulings tend to move
attitudes in the opposite direction or polarize attitudes.
We will focus on rulings about gender discrimination and their impact on
on attitudes about gender roles. 




# Datasets
To address this question we used two datasets.

First, we used the US General Social Survey (GSS), which is a long running (1972–) survey on social attitudes and behaviors of US American citizens \citep{smith2013general}. In addition to social attitudes, the GSS provides demographic and life-course data about respondents. Each row represents one respondent.

Second, we used a database of federal appeals court cases that were decided at the level of circuit courts \citep{sunstein2007judges}. The cases were separated by issue (e.g. affirmative action, gender discrimination, racial discrimination). The federal court system is divided into 12 circuits, each of which establishes legal precedent for a group of several states. A circuit court case is decided by a randomly assigned panel of three judges chosen from the pool of judges appointed to that circuit.  The dataset provides information about the outcome of each case, which is coded as the number of judges who voted in favor the outcome that can be considered to be more "progressive" (for example, pro-affirmative action, and against racial or gender discrimination).

Another dataset was used to assign judge characteristics to each case \cite{eb60c240-7076-4b7f-829d-9b68e9f5494c}. This included, for instance, the number of panel judges who were female, or who were appointed by a Democratic president. It also included the average number of female judges (and other characteristics) in the pool of judges for that circuit at the time of the ruling.

For our analyses reported below, we focused of the issue of gender discrimination, and restricted ourselves to court case data pertaining to that issue. In total, we used 100 cases (one case per row) that were decided between 1995 and 2004. We chose this subset of cases because it was the subset that had the longest period of intersection with several relevant questions on the GSS.