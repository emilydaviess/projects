##################
#Load Libraries#
##################
library(DBI)
library(RSQLite)
library(dplyr)
library(woeBinning)
library(ggplot2)
library(C50)
library(mltools)
library(data.table)
library(gmodels)
set.seed(101)
options(scipen=999)
'%!in%' <- function(x,y)!('%in%'(x,y))

#############################
#DATA PULL & Data Cleaning#
############################

#Source in the load_data function from the file data_pull.R. 
#This keeps the main script (model_source.R clean and easy to read. 
source('1_data_pull.R') #load_data(database) function which will pull data from SQLite DB
policy_data <- load_data_dt("admiral_db.db") #Returns list of two, first is train data, second is test. 
policy_train <- as.data.frame(policy_data[1])
policy_test <- as.data.frame(policy_data[2])
str(policy_train)

###################
#Model Build 
###################

#1. Response Variable is classifed as CATEGORICAL - ClaimFlag (1/0). 
#2. Model will be supervised, as we will train on labelled data. 
#3. Chosen model is a descision tree.
#I've chosed this model, over the likes of a neural network/random forest because I want the model to be explainable to the customer.
#Therefore, if we were to use this model to predict the liklihood of somebody 
str(policy_train)

response_index <- grep("ClaimFlag", colnames(policy_train))
fit <- C5.0(x = policy_train[,-response_index], y = policy_train[,c("ClaimFlag")])
summary(fit)
#The Error field of our model shows a rate of error of 12.6%
claim_pred <- predict(fit, policy_test[,-response_index])
claim_prob <- predict(fit, policy_test[,-response_index],type = "prob")

#Apply our decision tree to our test dataset using predict() function. 
CrossTable(policy_test$ClaimFlag, claim_pred, prop.chisq = FALSE,
           prop.c = FALSE, prop.r = FALSE, dnn = c('actual default', 'predicted default'))

#84% accuracy, however, model only correctly predicted 38 out of 1063 claims - 3.57%.
#This is where the model needs to be improved. 


#Use boosting to boost performance of our model 
tree_boost <- C5.0(x = policy_train[,-response_index], y = policy_train[,c("ClaimFlag")], trials = 5)
summary(tree_boost)

#Apply our decision tree to our test dataset using predict() function. 
claim_pred_boost <- predict(tree_boost, policy_test[,-response_index])
claim_prob_boost <- predict(tree_boost, policy_test[,-response_index],type = "prob")
policy_test <- cbind(policy_test,claim_pred,claim_prob)
policy_test <- cbind(policy_test,claim_pred_boost,claim_prob_boost)
CrossTable(policy_test$ClaimFlag, claim_pred_boost, prop.chisq = FALSE,
           prop.c = FALSE, prop.r = FALSE, dnn = c('actual default', 'predicted default'))

#84% accuracy, however, model only correctly predicted 52 out of 1063 claims - 4.89% 
#This is where the model needs to be improved. 
#Also, we are getting very little variance with our probabilities (propensity scores), highlighting the model is not powerful to make such predictions.

#Because of these low scores, i've decided to build a more advanced model - neural network 
#Although blackbox, hopefully we will see much better accuracy scoring for predicting claims.  
#See 0_model_source_nn.R.
