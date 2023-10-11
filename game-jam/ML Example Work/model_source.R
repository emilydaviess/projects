#############################
#READY FOR MACHINE LEARNING#
##############################

#The aim here is to  predict the liklihood of a visitor prediciting within a 60 day period! 
#The 'time_to_sale' will indicate if the user went on to make a sale within the given time period.  
model_tune <- function(data, nodes1, node2, dropout1, dropout2, optimizer, lr_annealing, batch_size, epochs){
  cubed_data <- data
  
  data <- 1
  set.seed(101)
  
  cubed_data <- cubed_data %>%
    select(-visitor_id) %>%
    select(-is_sale_visit) %>%
    select(-visit_id) %>%
    select(-max_sale) %>%
    select(-sales_date) %>%
    select(-time_to_sale) %>%
    select(-prev_visit) %>%
    select(-product_id) %>%
    select(-future_sale_count) %>%
    select(target_sale, everything())
  
  
  #Need to Normalise the data! visit_duration, page_count, lag_since_last_visit, visit_number, lag_since_sale, lag_since_product_sale
  feature_mean_sd <- data.frame()
  #vars_to_norm <- c("visit_duration", "lag_since_last_visit", "visit_number", "lag_since_sale", "lag_since_product_sale")
  vars_to_norm <- names(cubed_data)
  vars_to_norm <- vars_to_norm[! vars_to_norm %in% c("target_sale")]
  for (feature in vars_to_norm){
    cubed_data_subset <- cubed_data[cubed_data[,feature] != -10000,feature] #1.remove dummy variable
    iqr <- quantile(cubed_data_subset, c(0.1, 0.8)) #2. Find the IQR of each column - this will be used to remove outliers to calculate the true mean and SD
    iqr_uq <- iqr[[2]] #get the upper quartile
    cubed_data_subset <- cubed_data_subset[cubed_data_subset <= iqr_uq] #remove outliers using upper quartile
    mean <- mean(cubed_data_subset) #find mean and sd on new subset!
    sd <- sd(cubed_data_subset)
    sd <- ifelse(sd==0, 1, sd)
    cubed_data[,feature] <- (cubed_data[,feature] - mean)/sd #normliase orginial data!
    feature_mean_sd <- rbind(feature_mean_sd, cbind(feature, mean, sd))
  }
  
  
  #Split Into Train/Test Sets
  train_test_split <- initial_split(cubed_data, prop = 0.8)
  
  #We can retrieve our training and testing sets using training() and testing() functions.
  train_tbl <- training(train_test_split)
  test_tbl  <- testing(train_test_split)
  
  #Create recipe
  rec_obj <- recipe(target_sale ~ ., data = train_tbl) %>%
    prep(data = train_tbl)
  
  #Predictors
  x_train_tbl <- bake(rec_obj, new_data = train_tbl) %>% select(-target_sale)
  x_train_tbl <- x_train_tbl[,colSums(is.na(x_train_tbl))<nrow(x_train_tbl)] #Remove Columns which are NA
  x_test_tbl  <- bake(rec_obj, new_data = test_tbl) %>% select(-target_sale)
  x_test_tbl <- x_test_tbl[,names(x_test_tbl) %in% names(x_train_tbl)]
  
  #Response variables for training and testing sets
  y_train_vec <- ifelse(pull(train_tbl, target_sale) == 1, 1, 0)
  y_test_vec  <- ifelse(pull(test_tbl, target_sale) == 1, 1, 0)
  
  model_keras <- keras_model_sequential()
  
  model_keras %>% 
    
    # First hidden layer
    layer_dense(
      units              = nodes1,#FLAGS$nodes1
      activation         = "relu", 
      input_shape        = ncol(x_train_tbl)) %>% 
    
    # Dropout to prevent overfitting
    layer_dropout(rate = dropout1) %>% #FLAGS$dropout1
    
    # Second hidden layer
    layer_dense(
      units              = node2, #FLAGS$nodes2
      activation         = "relu") %>% 
    #layer_batch_normalization() %>%
    
    # Dropout to prevent overfitting
    layer_dropout(rate = dropout2) %>% #FLAGS$dropout2
    
    # Output layer
    layer_dense(
      units  = 1,
      activation = "sigmoid") %>% 
    
    # Compile ANN
    compile(
      optimizer = optimizer, #FLAGS$optimizer
      loss      = 'binary_crossentropy',
      metrics   = c('accuracy') 
    )
  
  history <- model_keras %>%  fit(
    x                = as.matrix(x_train_tbl), 
    y                = y_train_vec,
    batch_size       = batch_size, 
    epochs           = epochs,
    validation_split = 0.25,
    callbacks = list(
      callback_early_stopping(patience = 5),
      callback_reduce_lr_on_plateau(factor = lr_annealing) #FLAGS$lr_annealing
    ),
    verbose = TRUE
  )
  
  metric_loss <- history$metrics$loss[length(history$metrics$loss)]
  metric_acc <- history$metrics$acc[length(history$metrics$acc)]
  metric_val_loss <- history$metrics$val_loss[length(history$metrics$val_loss)]
  metric_val_acc <- history$metrics$val_acc[length(history$metrics$val_acc)]
  samples <- history$params$samples
  
  
  # Predicted Class
  yhat_keras_class_vec <- predict_classes(object = model_keras, x = as.matrix(x_test_tbl)) %>%
    as.vector()
  
  # Predicted Class & Propensity Probability
  yhat_keras_prob_vec  <- predict_proba(object = model_keras, x = as.matrix(x_test_tbl)) %>%
    as.vector()
  y_test_vec <- factor(as.character(y_test_vec), levels=c("0", "1"))
  yhat_keras_class_vec <- factor (as.character(yhat_keras_class_vec), levels=c("0", "1"))
  test <- cbind(yhat_keras_prob_vec, y_test_vec, yhat_keras_class_vec)
  print(str(test))
  print(test[1:1000,])
  
  # corrr_analysis <- x_train_tbl %>%
  #   mutate(target_sale = y_train_vec) %>%
  #   correlate() %>%
  #   focus(target_sale) %>%
  #   rename(feature = rowname) %>%
  #   arrange(abs(target_sale)) %>%
  #   mutate(feature = as_factor(feature))
  
  # names(corrr_analysis) <- c("feature", "weight")
  # corrr_analysis$product_id <- product_id
  # corrr_analysis$created <- gsub("BST", "", Sys.time()) 
  # corrr_analysis <- corrr_analysis[,c("product_id", "feature", "weight", "created")] #Ready for SQL!
  # corrr_analysis[is.na(corrr_analysis)] <- 0
  
  
  
  estimates_keras_tbl <- tibble(
    truth      = as.factor(y_test_vec),
    estimate   = as.factor(yhat_keras_class_vec), 
    class_prob = yhat_keras_prob_vec
  )
  #print(estimates_keras_tbl)
  options(yardstick.event_first = FALSE)
  
  precision_recall <- tibble(
    precision = estimates_keras_tbl %>% precision(truth, estimate),
    recall    = estimates_keras_tbl %>% recall(truth, estimate)
  )
  
  result <- as.data.frame(cbind(
    Sys.time(), 
    nodes1, 
    nodes2,  
    dropout1, 
    dropout2,
    optimizer, 
    lr_annealing,
    metric_loss, 
    metric_acc, 
    metric_val_loss, 
    metric_val_acc,
    samples,
    batch_size, 
    epochs, 
    precision_recall$precision[3], 
    precision_recall$recall[3]))
  names(result) <- c("date","flag_nodes1","flag_nodes2", "flag_dropout1","flag_dropout2","flag_optimizer", "flag_lr_annealing",
                     "metric_loss", "metric_acc", "metric_val_loss", "metric_val_acc", "samples", "batch_size", 
                     "epochs","precision", "recall")
  result[is.na(result)] <- 0
  result$prec_recall <- result$precision*result$recall
  return(result)
}










