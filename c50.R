install.packages('C50') 

library('C50') # load the package  

data <- read.csv('Paper/WASP-CBSS-BT/ExecutedTraces.csv') # read the dataset 
head(data) # look at the 1st 6 rows

rules <- C5.0(data[,-8], as.factor(data[,8]), rules = TRUE) 
summary(rules) # view the ruleset 

decision_tree <- C5.0(data[,-8], as.factor(data[,8])) 
summary(decision_tree) # view the ruleset 
plot(decision_tree, main = 'robot decision tree')

write(capture.output(summary(rules)), "Paper/WASP-CBSS-BT/c50-rules.txt")

