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

videos <- read.csv("Data/Youtube/GBvideos_recommendations.csv")
videos <- videos[!is.na(videos$rated),]

videos$trending_date <- as.Date(videos$trending_date, format = "%y.%d.%m")
videos$publish_date <- as.Date(substr(videos$publish_time,start = 1,stop = 10), format = "%Y-%m-%d")
videos$dif_days <- videos$trending_date-videos$publish_date
videos$year <- format(videos$trending_date,"%Y")
videos$month <- format(videos$trending_date,"%m")
videos$day <- format(videos$trending_date,"%d")
videos[,"title_length"] = str_length(videos[,"title"])


#1. Create a recommendations engine, recommending youtube videos you think the user will like, based on the data! 
names(videos)
model_video_data <- videos[,c("rated","category_id", "likes", "dislikes")]
model_video_data$category_id <- as.factor(model_video_data$category_id)
str(model_video_data)

#Split Into Train/Test Sets
train_test_split <- initial_split(model_video_data, prop = 0.8)

#We can retrieve our training and testing sets using training() and testing() functions.
train_tbl <- training(train_test_split)
test_tbl  <- testing(train_test_split)

rec_obj <- recipe(rated ~ ., data = train_tbl) %>%
  #step_scale(all_numeric(), -all_outcomes()) %>%
  #step_center(all_numeric(), -all_outcomes()) %>%
  step_dummy(all_nominal(), -all_outcomes()) %>%
  prep(data = train_tbl)

#Predictors
x_train_tbl <- bake(rec_obj, new_data = train_tbl) %>% select(-rated)
x_train_tbl <- x_train_tbl[,colSums(is.na(x_train_tbl))<nrow(x_train_tbl)] #Remove Columns which are NA
x_test_tbl  <- bake(rec_obj, new_data = test_tbl) %>% select(-rated)
x_test_tbl <- x_test_tbl[,names(x_test_tbl) %in% names(x_train_tbl)]


#Response variables for training and testing sets
y_train_vec <- train_tbl$rated
y_test_vec <- test_tbl$rated


#Build the model! 
model_keras <- keras_model_sequential()
model_keras %>% 
  
  # First hidden layer
  layer_dense(
    units              = 32,#FLAGS$nodes1
    activation         = "relu", 
    input_shape        = ncol(x_train_tbl)) %>% 
  layer_dropout(rate = 0.1) %>% # Dropout to prevent overfitting
  
  #Second hidden layer
  layer_dense(
    units              = 10,
    activation         = "relu") %>%
  layer_dropout(rate = 0.1) %>%
  
  # Output layer
  layer_dense(
    units  = 1,
    activation = "sigmoid") %>% 
  
  #Compile ANN
  compile(
    optimizer = "adam", 
    loss      = 'binary_crossentropy',
    metrics   = c('accuracy') 
  )

history <- model_keras %>%  fit(
  x                = as.matrix(x_train_tbl), 
  y                = y_train_vec,
  batch_size       = 100, 
  epochs           = 30,
  validation_split = 0.15,
  # callbacks = list(
  #   callback_early_stopping(patience = 5),
  #   callback_reduce_lr_on_plateau(factor = lr) #FLAGS$lr_annealing
  # ),
  verbose = TRUE
)

options(scipen=999) #stop scientific notation

#Predicted Class
predicted_class <- predict_classes(object = model_keras, x = as.matrix(x_test_tbl)) %>%
  as.vector()
# Predicted Class & Propensity Probability
predicted_prob  <- predict_proba(object = model_keras, x = as.matrix(x_test_tbl)) %>%
  as.vector()
results <- cbind(test_tbl,predicted_class,predicted_prob)


#Putting Channel ID in floods the model! we then have 1000+ columns. We need to do FEATURE ENGENEERING to create new columns. 
#For example, use the most popular channels found in the previous task, and create a new column, such as 'in_top_10_channels', with a yes/no, or create a couple of new columsn with '1','0', for the most popular channels. 
#Could also use the title feild, and the wordcloud from previous task to create columns such as 'contains_offical', when a video contains official in the title. 
