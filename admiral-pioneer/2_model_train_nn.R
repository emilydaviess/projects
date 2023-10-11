model_train <- function(policy_train, policy_test, nodes1, nodes2, dropout1, dropout2, optimizer, batch_size, epochs, lr_annealing){
  set.seed(101)
  #Response variables for training set
  y_train_vec <- as.numeric(as.character(policy_train$ClaimFlag))
  x_train_tbl <- policy_train[,which(names(policy_train) %!in% c("ClaimFlag"))]
  
  # Response variables testing set
  y_test_vec <- as.numeric(as.character(policy_test$ClaimFlag))
  x_test_tbl <- policy_test[,which(names(policy_test) %!in% c("ClaimFlag","PolicyID"))]
  
  model_keras <- keras_model_sequential()
  model_keras %>% 
    
    # First hidden layer
    layer_dense(
      units              = nodes1,
      activation         = "relu", 
      input_shape        = length(x_train_tbl)) %>% 
    layer_dropout(rate = dropout1)  
    
    if (nodes2 != -1){
      #Second hidden layer
      model_keras %>% layer_dense(
        units              = nodes2, 
        activation         = "relu") %>%
      layer_dropout(rate = dropout2) 
    }
    
  # Output layer
  model_keras %>% layer_dense(
    units  = 1,
    activation = "sigmoid") %>% 
    
  compile(   # Compile ANN
      optimizer = optimizer,
      loss      = 'binary_crossentropy',
      metrics   = c('accuracy') 
    )

  history <- model_keras %>%  fit(
    x                = as.matrix(x_train_tbl), 
    y                = as.matrix(y_train_vec),
    batch_size       = batch_size, 
    epochs           = epochs,
    validation_split = 0.2,
    callbacks = list(
      callback_early_stopping(patience = 5),
      callback_reduce_lr_on_plateau(factor = lr_annealing) 
    ),
    verbose = TRUE 
  )

  metric_loss <- history$metrics$loss[length(history$metrics$loss)]
  metric_acc <- history$metrics$acc[length(history$metrics$acc)]
  metric_val_loss <- history$metrics$val_loss[length(history$metrics$val_loss)]
  metric_val_acc <- history$metrics$val_acc[length(history$metrics$val_acc)]

  # Predicted Class
  yhat_keras_class_vec <- predict_classes(object = model_keras, x = as.matrix(x_test_tbl)) %>%
    as.vector()
  
  # Predicted Class & Propensity Probability
  yhat_keras_prob_vec  <- predict_proba(object = model_keras, x = as.matrix(x_test_tbl)) %>%
    as.vector()
  
  y_test_vec <- factor(as.character(y_test_vec), levels=c("0", "1"))
  yhat_keras_class_vec <- factor (as.character(yhat_keras_class_vec), levels=c("0", "1"))
  
  estimates_keras_tbl <- tibble(
    truth      = as.factor(y_test_vec),
    estimate   = as.factor(yhat_keras_class_vec), 
    class_prob = yhat_keras_prob_vec
  )
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
    batch_size, 
    epochs, 
    precision_recall$precision[3], 
    precision_recall$recall[3]))
  names(result) <- c("date","flag_nodes1","flag_nodes2", "flag_dropout1","flag_dropout2","flag_optimizer", "flag_lr_annealing",
                     "metric_loss", "metric_acc", "metric_val_loss", "metric_val_acc", "batch_size", 
                     "epochs","precision", "recall")
  result[is.na(result)] <- 0
  result$prec_recall <- result$precision*result$recall
  
  
  yhat_keras_prob_vec  <- round(predict_proba(object = model_keras, 
                                              x = as.matrix(x_test_tbl[,which(names(x_test_tbl) %!in% c("ClaimFlag","PolicyID"))])) %>% as.vector(),4)
  yhat_keras_class_vec <- ifelse(round(yhat_keras_prob_vec,2) >= 0.5, 1, 0)
  
  claim_predictions <- as.data.frame(cbind(PolicyID=policy_test$PolicyID,
                                           actual=as.numeric(as.character(policy_test$ClaimFlag)), 
                                           predicted=yhat_keras_class_vec, 
                                           prob=yhat_keras_prob_vec))
  claim_predictions$correct <- ifelse(claim_predictions$actual == claim_predictions$predicted, 1, 0)
  success_rate <- (nrow(claim_predictions[claim_predictions$correct == 1,])/nrow(claim_predictions))*100
  success_rate_claimers <- (nrow(claim_predictions[claim_predictions$correct == 1 & claim_predictions$actual == 1,])/nrow(claim_predictions[claim_predictions$actual == 1,]))*100
  
  #Use 25% as a threshold as well
  claim_predictions$predicted_25 <- ifelse(claim_predictions$prob >= 0.25, 1, 0)
  claim_predictions$correct_25 <- ifelse(claim_predictions$actual == claim_predictions$predicted_25, 1, 0)
  success_rate_25 <- nrow(claim_predictions[claim_predictions$correct_25 == 1,])/nrow(claim_predictions)*100 
  success_rate_claimers_25 <- (nrow(claim_predictions[claim_predictions$correct_25 == 1 & claim_predictions$actual == 1,])/nrow(claim_predictions[claim_predictions$actual == 1,]))*100 
  
  result$success_rate <- success_rate
  result$success_rate_claimers <- success_rate_claimers
  result$success_rate_25 <- success_rate_25
  result$success_rate_claimers_25 <- success_rate_claimers_25
  
  result$run_num <- run_num
  claim_predictions$run_num <- run_num
  result <- list(result, claim_predictions)
  
  return(result)
}


