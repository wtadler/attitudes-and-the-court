library(ggplot2)
library(dplyr)
library(tidyr)
library(foreign)


# Change directory if desired
# user = Sys.info()["user"]
# setwd(paste("/Users/",user,"/GoogleDrive/NYU_GD/MLClass/project/gitRepo/RAnalyses",sep=""))


# ##### Read data (trying to only do this once)
# gss = read.dta(paste("/Users/",user,"/GoogleDrive/NYU_GD/MLClass/Societal\ Attitudes\ and\ Court\ Cases/data/GSS7212_R2.DTA",sep=""))
# raceData = gss %>%  
#         filter( age>17,race=='white') %>% 
#         select(year,age,id,sex,race,racmar,racpres,racseg,racfew,rachaf,racmost,racavoid,racdin,racpush,racschol,closeblk,feelblks,racjob,racmarel,racmarpr,racobjct,racopen,racchng,racpush,racquit,racsubs,racsups,racteach,wrkwayup)
# write.table(raceData,file="raceData.csv",sep=',')



###### Otherwise read from file
raceData = read.csv("raceData.csv", header = TRUE)

# other possibilities (added post-1977): AFFRMACT,discaff,CLOSEBLK,CLOSEWHT,MARBLK,LIVEBLKS, LIVEWHTS


##### Handling missing values 
raceData[raceData[,]=="iap"] <- NA
raceData[raceData[,]=="dk"] <- NA 

# Not sure if dk should really be NA, but leaving this for now


# Check out levels (for recoding)
print(sapply(droplevels(raceData),levels))
raceData = droplevels(raceData)


# Combine mutually exclusive columns about peers into one variable
raceData$racPeers  = NA
raceData[raceData$racmost == "no" & !is.na(raceData$racmost),]$racPeers  = 0
raceData[raceData$racfew == "yes, object" & !is.na(raceData$racfew),]$racPeers = 3
raceData[raceData$rachaf == "yes, object" & !is.na(raceData$rachaf),]$racPeers = 2
raceData[raceData$racmost == "yes, object"& !is.na(raceData$racmost),]$racPeers = 1


# Now recode so high is prejudiced
rdClean = raceData %>%
    transmute(year = year,
      id=id,
      racmar= racmar == "yes",
          racpres = racpres == "no",
          racseg = as.numeric(factor(racseg,levels(racseg)[c(3,4,2,1)])),
          racavoid = racavoid == "yes",
          racdin = as.numeric(racdin),
          racpush = as.numeric(factor(racpush,levels(racpush)[c(3,4,2,1)])),
          racschol = racschol == "separate schools",
          closeblk = as.numeric(max(closeblk,na.rm=TRUE)-closeblk),
          feelblks = as.numeric(feelblks),
          racmarel = as.numeric(racmarel),
          racmarpr = racmarpr == "agree",
          racopen = racopen == "owner decides",
          racchng = racchng == "no",
          racsubs = racsubs == "oppose",
          racsups = racsups == "agree",
          racteach = racteach == "disagree",
          racjob = racjob == "whites first",
          wrkwayup = as.numeric(factor(wrkwayup,levels(wrkwayup)[c(4,5,2,1,3)])),
          racPeers = as.numeric(racPeers))

# Check there's no weird data types...
print(sapply(rdClean,class))

# Get rid of old levels
rdClean = droplevels(rdClean)


# mean of each question in in 1977
means77 = rdClean %>%
  filter(year == "1977") %>%
  group_by(year) %>%
  summarize_each(funs(mean(., na.rm = TRUE)))

allMeans = as.numeric(means77[1,3:length(means77)])

# Standard deviation of each question the first year it was asked
sdFirst  = rdClean %>%
  group_by(year) %>%
  summarize_each(funs(sd(.,na.rm=TRUE)))%>%
  summarize_each(funs(first(as.numeric(na.omit(.)))))

allSDs = as.numeric(sdFirst[1,3:length(sdFirst)])


# Standardization function
computeScore <- function(vals){
  scores = (vals - allMeans)/allSDs
  return(mean(scores,na.rm=TRUE))
}


#### Compute score per participant per year
#  (I wish I could figure out the NSE functionality of dplyr and pass column names as a vector..)
pScores = rdClean %>%
	group_by(year,id) %>%
	summarize(prejudice = computeScore(c(racmar,   racpres,  racseg,   racavoid, racdin,   racpush, racschol, closeblk, feelblks, racmarel, racmarpr, racopen, racchng,  racsubs,  racsups,  racteach, racjob,   wrkwayup,racPeers)))

raceData <- merge(raceData,pScores,by=c("year","id"))


write.table(raceData,file="raceData_withComposite.csv",sep=',')