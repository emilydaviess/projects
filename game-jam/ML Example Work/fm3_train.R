library(RMySQL)
library(dplyr)
library(reshape2)
library(rsample)
library(recipes)
#library(corrr)
library(yardstick)
library(forcats)
library(tfruns)
library(keras)
library(tensorflow)
lapply(dbListConnections(MySQL()), dbDisconnect)


################
#DATA INPUT#
#################

yard_data <- read.csv("yard_data.csv")


##########################
#TUNE HYPERPARAMS#
##########################

source('model_source.R')

#Test different variations of hyperparameters

#Set Hyperparams:
nodes1 = c(1000,500)
nodes2 = c(100)
dropout1 = c(0.1)
dropout2 = c(0.1)
optimizer = c("adam")
lr_annealing = c(0.01)
batch_size = c(50)
epochs = c(5)

combinations <- length(nodes1) * length(nodes2) * length(dropout1) * 
  length(dropout2) * length(optimizer) * length(lr_annealing) * length(batch_size) * length(epochs)

#Test different variations of hyperparameters using model_tune function from model_source.R!
results_df <- data.frame()
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
                run_num <- run_num + 1
                result <- model_tune(yard_data,n1,n2,d1,d2,opt,lr,bs,e)
                results_df <- rbind(results_df, result)
                #rm(result)
                gc()
              }
            }
          }
        }
      }
    }
  }
}
    
    
print("Tuning run finished")

results_df <- results_df[order(-results_df$prec_recall),]
opt_result <- results_df[1,] ## insert to agg_model_hyperparams



