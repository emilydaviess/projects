##################
#Load Libraries#
##################
library(DBI)
library(RSQLite)
library(dplyr)
library(woeBinning)
library(ggplot2)
library(keras)
library(tensorflow)
library(yardstick)
library(recipes)
set.seed(101)
options(scipen=999)
'%!in%' <- function(x,y)!('%in%'(x,y))

#Source in the load_data function from the file data_pull.R. 
#This keeps the main script (model_source.R clean and easy to read. 
source('1_data_pull.R') #load_data(database) function which will pull data from SQLite DB
policy_data <- load_data_nn("admiral_db.db") #Returns list of two, first is train data, second is test. 
policy_train <- as.data.frame(policy_data[1])
policy_test <- as.data.frame(policy_data[2])
#Check we have same proportion of ClaimFlag=1 in train/test datasets. 
(nrow(policy_train[policy_train$ClaimFlag == 1,])/nrow(policy_train))*100 #~7%
(nrow(policy_test[policy_test$ClaimFlag == 1,])/nrow(policy_test))*100 #~7%

##########################
#TUNE HYPERPARAMS#
##########################

#Test different variations of hyperparameters

#Set Hyperparams:
nodes1 = c(1024, 2048) 
nodes2 = c(256, 512)
dropout1 = c(0.2, 0.4)
dropout2 = c(0.2, 0.4)
optimizer = c("adam")
lr_annealing = c(0.001)
batch_size = c(50)
epochs = c(20)

combinations <- length(nodes1) * length(nodes2) * length(dropout1) * 
  length(dropout2) * length(optimizer) * length(lr_annealing) * length(batch_size) * length(epochs)


#Test different variations of hyperparameters using model_tune function from model_source.R!
results_df <- data.frame()
predictions_df <- data.frame()
run_num <- 1
for (n1 in nodes1){
  for (n2 in nodes2){
    for(d1 in dropout1){
      for (d2 in dropout2){
        for (opt in optimizer){
          for (lr in lr_annealing){
            for (bs in batch_size){
              for (e in epochs){
                print(paste("Run number ",run_num,"/",combinations, sep=""))
                print(paste(n1,n2,d1,d2,opt,lr,bs,e))
                source('2_model_train_nn.R') #model_train(train_data, test_data,n1,n2,d1,d2,opt,bs,e, lr) function which will train our train dataset.
                result <- model_train(policy_train,policy_test,n1,n2,d1,d2,opt,bs,e, lr)
                result_model <- as.data.frame(result[1]) #results of model 
                prediction <- as.data.frame(result[2]) #predictions
                results_df <- rbind(results_df, result_model)
                predictions_df <- rbind(predictions_df, prediction)
                run_num <- run_num + 1
              }
            }
          }
        }
      }
    }
  }
}


print("Tuning run finished")

#Order results_df by success_rate_claimers_25, this variables is a percentage of how many claim predictions we were correct on, out of all claims (ClaimFlag =1). 
#We use this variables rather than the general success rate, because the majority of observations are non-claims (ClaimFlag=0) - 93%
#Therefore it is key to understanding how our model performed at predicting ClaimFLag=1 specifically. 
results_df <- results_df[order(-results_df$success_rate_claimers_25),] 
opt_result <- results_df[1,] 
opt_run_num <- opt_result$run_num[1]

claim_predictions <- predictions_df[predictions_df$run_num == opt_run_num,] #Select predictions of our optimal model (opt_run_number)
claim_predictions <- claim_predictions[order(-claim_predictions$actual, -claim_predictions$prob),] 

##############
#RESULTS! 
##############

#Using  50% as a threshold
#success rate
nrow(claim_predictions[claim_predictions$correct == 1,])/nrow(claim_predictions)*100 
#success_rate_claimers
(nrow(claim_predictions[claim_predictions$correct == 1 & claim_predictions$actual == 1,])/nrow(claim_predictions[claim_predictions$actual == 1,]))*100 

#Using  25% as a threshold - We use a lower threshold for classifying results because ClaimFlag=1 has a much smaller proportion (~7%), therefore predicting this value is much more difficult. 
#The model will therefore be more likely to score observations lower, even though they are claims, hence, by using a lower threshold, 
#we maintain the overall accuracy levels, whilst also increasing our claim success prediction massively. 
#success rate
nrow(claim_predictions[claim_predictions$correct_25 == 1,])/nrow(claim_predictions)*100 
#success_rate_claimers
(nrow(claim_predictions[claim_predictions$correct_25 == 1 & claim_predictions$actual == 1,])/nrow(claim_predictions[claim_predictions$actual == 1,]))*100 

