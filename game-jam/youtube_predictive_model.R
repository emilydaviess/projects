###################
#INSTALL PACKAGES#
###################

#Machine Learning
library(recipes)
library(rsample)
library(stringr)
library(keras)
library(tensorflow)
#devtools::install_github("rstudio/keras")
library(keras)
#install_keras()


###############
#Data Input#
###############


videos <- read.csv("Data/Youtube/GBvideos.csv")

videos$country <- "gb"
videos$trending_date <- as.Date(videos$trending_date, format = "%y.%d.%m")
videos$publish_date <- as.Date(substr(videos$publish_time,start = 1,stop = 10), format = "%Y-%m-%d")
videos$dif_days <- videos$trending_date-videos$publish_date
videos$year <- format(videos$trending_date,"%Y")
videos$month <- format(videos$trending_date,"%m")
videos$day <- format(videos$trending_date,"%d")
videos[,"title_length"] = str_length(videos[,"title"])

names(videos)

#1. Predict the number of views using other variables for the music category (cat 10)

model_video_data <- videos[videos$category_id == 10,]
model_video_data <- model_video_data[,c("views","likes", "dislikes")]
str(model_video_data)

#Split Into Train/Test Sets
train_test_split <- initial_split(model_video_data, prop = 0.8)

#We can retrieve our training and testing sets using training() and testing() functions.
train_data <- training(train_test_split)
test_data  <- testing(train_test_split)

rec_obj <- recipe(views ~ ., data = train_data) %>%
  #step_scale(all_numeric(), -all_outcomes()) %>%
  #step_center(all_numeric(), -all_outcomes()) %>%
  step_dummy(all_nominal(), -all_outcomes()) %>%
  prep(data = train_data)

#Predictors
train_clean <- bake(rec_obj, new_data = train_data) %>% select(-views)
train_clean <- train_clean[,colSums(is.na(train_clean))<nrow(train_clean)] #Remove Columns which are NA
test_clean  <- bake(rec_obj, new_data = test_data) %>% select(-views)
test_clean <- test_clean[,names(test_clean) %in% names(test_clean)]


#Response variables for training and testing sets
train_response <- train_data$views
test_response <- test_data$views

#Build the model! 
model_keras <- keras_model_sequential()
model_keras %>% 
  
  # First hidden layer
  layer_dense(
    units              = 100,
    activation         = "relu", 
    input_shape        = ncol(train_clean)) %>% 
  layer_dropout(rate = 0.1) %>% #Dropout to prevent overfitting
  
  #Second hidden layer
  layer_dense(
    units              = 10,
    activation         = "relu") %>%
  layer_dropout(rate = 0.1) %>%
  
  # Output layer
  layer_dense(
    units  = 1) %>% 
  
  # Compile ANN
  compile(
    optimizer = "rmsprop", 
    loss      = 'mse',
    metrics   = c('mean_absolute_error') 
  )

history <- model_keras %>%  fit(
  x                = as.matrix(train_clean), 
  y                = train_response,
  batch_size       = 100, 
  epochs           = 30,
  validation_split = 0.15,
  # callbacks = list(
  #   callback_early_stopping(patience = 5),
  #   callback_reduce_lr_on_plateau(factor = lr) #FLAGS$lr_annealing
  # ),
  verbose = TRUE
)

predictions <- model_keras %>% predict(as.matrix(test_clean))
predictions <- round(predictions)
results <- cbind(test_data, predictions)
print(cor(results$views, results$predictions))

          
#Putting Channel ID in floods the model! we then have 1000+ columns. We need to do FEATURE ENGENEERING to create new columns. 
#For example, use the most popular channels found in the previous task, and create a new column, such as 'in_top_10_channels', with a yes/no, or create a couple of new columsn with '1','0', for the most popular channels. 
#Could also use the title feild, and the wordcloud from previous task to create columns such as 'contains_offical', when a video contains official in the title. 

model_video_data <- model_video_data[model_video_data$ratings_disabled == "False",]
model_video_data <- model_video_data[model_video_data$comments_disabled == "False",]
model_video_data <- model_video_data[model_video_data$dislikes > 0,]
model_video_data <- model_video_data[model_video_data$dif_days < 50,]












#ADVANCED!
#Set Hyperparams:
nodes1 = c(100)
nodes2 = c(10)
dropout1 = c(0.1)
dropout2 = c(0.1)
optimizer = c("rmsprop")
lr_annealing = c(0.01)
batch_size = c(250)
epochs = c(30)

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
                
                model_keras <- keras_model_sequential()
                model_keras %>% 
                  
                  # First hidden layer
                  layer_dense(
                    units              = n1,#FLAGS$nodes1
                    activation         = "relu", 
                    input_shape        = ncol(x_train_tbl)) %>% 
                  layer_dropout(rate = d1) %>% # Dropout to prevent overfitting
                  
                  #Second hidden layer
                  layer_dense(
                    units              = n2,
                    activation         = "relu") %>%
                  layer_dropout(rate = d2) %>%
                  
                  # Output layer
                  layer_dense(
                    units  = 1,
                    activation = "relu") %>% 
                  
                  # Compile ANN
                  compile(
                    optimizer = opt, 
                    loss      = 'mse',
                    metrics   = c('mean_absolute_error') 
                  )
                
                history <- model_keras %>%  fit(
                  x                = as.matrix(x_train_tbl), 
                  y                = y_train_vec,
                  batch_size       = bs, 
                  epochs           = e,
                  validation_split = 0.15,
                  # callbacks = list(
                  #   callback_early_stopping(patience = 5),
                  #   callback_reduce_lr_on_plateau(factor = lr) #FLAGS$lr_annealing
                  # ),
                  verbose = TRUE
                )
                
                predictions <- model_keras %>% predict(as.matrix(x_test_tbl))
                predictions <- round(predictions)
                results <- cbind(test_tbl, predictions)
                print(cor(results$views, results$predictions))
                
              }
            }
          }
        }
      }
    }
  }
}