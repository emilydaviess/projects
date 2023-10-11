# Remove outliers from a column functions (used within load_data_dt & load_data_nn)
remove_outliers <- function(x, na.rm = TRUE) {
  qnt <- quantile(x, probs=c(0.001, 0.995), na.rm = na.rm)
  H <- 1.5 * IQR(x, na.rm = na.rm)
  y <- x
  y[x < (qnt[1] - H)] <- NA
  y[x > (qnt[2] + H)] <- NA
  y
}
remove_all_outliers1 <- function(df){
  # We only want the numeric columns
  df[,sapply(df, is.numeric)] <- lapply(df[,sapply(df, is.numeric)], remove_outliers)
  df
}

#Decision Tree Load Data
load_data_dt <- function(database){
  
  #Create SQLite connection
  #database <- "admiral_db.db"
  con <- dbConnect(SQLite(), database)
  #as.data.frame(dbListTables(con))
  
  #Pull the PolicyData and GeographicData from SQLite DB. 
  policy_data <- dbReadTable(con, 'PolicyData')
  policy_data$TimeInsured <- as.numeric(policy_data$TimeInsured)
  policy_data$PolicyID <- as.factor(as.character(policy_data$PolicyID))
  policy_data$CoverageGap <- as.factor(as.character(policy_data$CoverageGap))
  policy_data$ZipCode <- as.factor(as.character(policy_data$ZipCode))
  policy_data$State <- as.factor(as.character(policy_data$State))
  # policy_data$NumberOfVehicles <- as.factor(as.character(policy_data$NumberOfVehicles))
  # policy_data$PriorAccidentCount <- as.factor(as.character(policy_data$PriorAccidentCount))
  
  geo_data <- dbReadTable(con, 'GeographicData')
  
  #Merge two datasets on ZipCode
  policy_data <- merge(policy_data, geo_data, by=c("ZipCode"))
  
  #To train our data, we'll subset out customers who have TimeInsured==1, hence, policy complete. 
  policy_data <- policy_data[policy_data$TimeInsured == 1 | policy_data$ClaimFlag==1,]
  
  
  #######################
  #DATA CLEANING#
  #######################
  
  #Without further knowledge on missing values for TimeInsured, and as it's only 2.9% of data, we'll exclude for now. 
  #policy_data <- policy_data[!is.na(policy_data$TimeInsured),]
  #CreditScore=0 is a massive outlier, and without more information, we'll also exlcude this. 
  policy_data <- policy_data[which(policy_data$CreditScore != 0),]
  #Zip Population = 0 is also evidence of incorrect data. 
  policy_data <- policy_data[which(policy_data$ZIP_Population != 0),]
  policy_data <- policy_data[which(policy_data$ZIP_AverageHomeValue > 0),]
  policy_data <- policy_data[which(policy_data$ZIP_AverageIncome > 0),]
  
  #Create a test dataset. I will use 80/20 split. 
  #The test/validation set must be kept completely seperate to development/training.
  policy_data$value <- 1 #Set this so we can sum in our summarise
  samp_size <- floor(0.8*nrow(policy_data))
  
  #Set seed to make partition reproducable
  valid_ind <- sample(seq_len(nrow(policy_data)), size = samp_size)
  
  train <- policy_data[valid_ind,]
  test <- policy_data[-valid_ind,]
  
  #Summarise stats - We want equal proportions of Claims in each dataset
  train %>% summarise(total = sum(value), sum_response = sum(ClaimFlag), perc = (sum_response/total)*100) #7.05%
  test %>% summarise(total = sum(value), sum_response = sum(ClaimFlag), perc = (sum_response/total)*100) #7.14% 
  
  ###################
  #Remove Outliers
  ###################
  
  train <- remove_all_outliers1(train)
  train <- na.omit(train)
  
  ###################
  #Binning Variables
  ##################
  
  #Using woe.binning we are able to get the WOE (weight of evidene) and IV (information value) showing how each 'bin' discrimiates the response.
  #The higher the IV the more influence it has on the reponse.
  binned_cols <- c("Age", "CreditScore", "NewestVehicleAge","ZIP_AverageHomeValue", "ZIP_AverageIncome", "ZIP_Population", "ZIP_LandArea")
  train1 <- train[ , -which(names(train) %in% c("TimeInsured","PolicyID", "ClaimAmount", "value", "ZipCode"))] #Only bin variables we want to put forward into the model
  bin_all <- woe.binning(train1, 'ClaimFlag', 
                         train1[,binned_cols], 
                         min.perc.total = 0.05, min.perc.class = 0.05, stop.limit = 0.1)
  dftrain <- woe.binning.deploy(train1, bin_all, min.iv.total=0.01)
  #dftrain <- dftrain[ , which(names(dftrain) %!in% binned_cols)]
  
  #Apply the bins onto the validation data frame
  test1 <- test[ , -which(names(test) %in% c("TimeInsured","PolicyID", "ClaimAmount", "value", "ZipCode"))]
  dftest <- woe.binning.deploy(test1, bin_all, min.iv.total=0.01)
  #dftest <- dftest[ , which(names(dftest) %!in% binned_cols)]
  
  ###################################
  #CREATE FINAL TEST/TRAIN DATASETS
  ###################################
  
  dftrain$ClaimFlag <- as.factor(as.character(dftrain$ClaimFlag))
  dftest$ClaimFlag <- as.factor(as.character(dftest$ClaimFlag))

  dftrain[,sapply(dftrain, is.factor)] <- lapply(dftrain[,sapply(dftrain, is.factor)], function(y) gsub("\\(|\\)|\\[|\\]", "", y)) 
  dftrain[sapply(dftrain, is.character)] <- lapply(dftrain[sapply(dftrain, is.character)], as.factor) #Above converts back to character so need to convert again
  dftrain[,sapply(dftrain, is.factor)] <- lapply(dftrain[,sapply(dftrain, is.factor)], function(y) gsub("\\,", "-", y))
  dftrain[sapply(dftrain, is.character)] <- lapply(dftrain[sapply(dftrain, is.character)], as.factor)
  

  dftest[,sapply(dftest, is.factor)] <- lapply(dftest[,sapply(dftest, is.factor)], function(y) gsub("\\(|\\)|\\[|\\]", "", y))
  dftest[sapply(dftest, is.character)] <- lapply(dftest[sapply(dftest, is.character)], as.factor) #Above converts back to character so need to convert again
  dftest[,sapply(dftest, is.factor)] <- lapply(dftest[,sapply(dftest, is.factor)], function(y) gsub("\\,", "-", y))
  dftest[sapply(dftest, is.character)] <- lapply(dftest[sapply(dftest, is.character)], as.factor)
  
  train_test_list <- list(dftrain, dftest)
  
  return(train_test_list)
}

#Neural Network Load Data 
load_data_nn <- function(database){
  
  #Create SQLite connection
  #database <- "admiral_db.db"
  con <- dbConnect(SQLite(), database)
  #as.data.frame(dbListTables(con))
  
  #Pull the PolicyData and GeographicData from SQLite DB. 
  policy_data <- dbReadTable(con, 'PolicyData')
  policy_data$TimeInsured <- as.numeric(policy_data$TimeInsured)
  policy_data$PolicyID <- as.factor(as.character(policy_data$PolicyID))
  policy_data$CoverageGap <- as.factor(as.character(policy_data$CoverageGap))
  policy_data$ZipCode <- as.factor(as.character(policy_data$ZipCode))
  policy_data$State <- as.factor(as.character(policy_data$State))
  # policy_data$NumberOfVehicles <- as.factor(as.character(policy_data$NumberOfVehicles))
  # policy_data$PriorAccidentCount <- as.factor(as.character(policy_data$PriorAccidentCount))
  
  geo_data <- dbReadTable(con, 'GeographicData')
  
  #Merge two datasets on ZipCode
  policy_data <- merge(policy_data, geo_data, by=c("ZipCode"))
  
  #To train our data, we'll subset out customers who have TimeInsured==1, hence, policy complete. 
  policy_data <- policy_data[policy_data$TimeInsured == 1 | policy_data$ClaimFlag==1,]
  
  
  #######################
  #DATA CLEANING#
  #######################
  
  #Without further knowledge on missing values for TimeInsured, and as it's only 2.9% of data, we'll exclude for now. 
  #policy_data <- policy_data[!is.na(policy_data$TimeInsured),]
  #CreditScore=0 is a massive outlier, and without more information, we'll also exlcude this. 
  policy_data <- policy_data[which(policy_data$CreditScore != 0),]
  #Zip Population = 0 is also evidence of incorrect data. 
  policy_data <- policy_data[which(policy_data$ZIP_Population != 0),]
  policy_data <- policy_data[which(policy_data$ZIP_AverageHomeValue > 0),]
  policy_data <- policy_data[which(policy_data$ZIP_AverageIncome > 0),]
  
  ###################
  #Remove Outliers
  ###################
  
  policy_data <- remove_all_outliers1(policy_data)
  policy_data <- na.omit(policy_data)
  
  #Create a test dataset. I will use 80/20 split. 
  #The test/validation set must be kept completely seperate to development/training.
  policy_data$value <- 1 #Set this so we can sum in our summarise
  samp_size <- floor(0.8*nrow(policy_data))
  
  #Set seed to make partition reproducable
  valid_ind <- sample(seq_len(nrow(policy_data)), size = samp_size)
  
  train <- policy_data[valid_ind,]
  test <- policy_data[-valid_ind,]
  
  #Summarise stats - We want equal proportions of Claims in each dataset
  train %>% summarise(total = sum(value), sum_response = sum(ClaimFlag), perc = (sum_response/total)*100) #7.05%
  test %>% summarise(total = sum(value), sum_response = sum(ClaimFlag), perc = (sum_response/total)*100) #7.14% 
  
  
  ###################
  #Binning Variables
  ##################
  
  #Using woe.binning we are able to get the WOE (weight of evidene) and IV (information value) showing how each 'bin' discrimiates the response.
  #The higher the IV the more influence it has on the reponse.
  binned_cols <- c("Age", "CreditScore", "NewestVehicleAge","ZIP_AverageHomeValue", "ZIP_AverageIncome", "ZIP_Population", "ZIP_LandArea")
  train1 <- train[ , -which(names(train) %in% c("TimeInsured","PolicyID", "ClaimAmount", "value", "ZipCode"))] #Only bin variables we want to put forward into the model
  bin_all <- woe.binning(train1, 'ClaimFlag', 
                         train1[,binned_cols], 
                         min.perc.total = 0.05, min.perc.class = 0.05, stop.limit = 0.1)
  dftrain <- woe.binning.deploy(train1, bin_all, min.iv.total=0.01)
  #dftrain <- dftrain[ , which(names(dftrain) %!in% binned_cols)]
  
  #Apply the bins onto the validation data frame
  test1 <- test[ , -which(names(test) %in% c("TimeInsured", "ClaimAmount", "value", "ZipCode"))]
  dftest <- woe.binning.deploy(test1, bin_all, min.iv.total=0.01)
  #dftest <- dftest[ , which(names(dftest) %!in% binned_cols)]
  
  ###################################
  #CREATE FINAL TEST/TRAIN DATASETS
  ###################################
  
  dftrain$ClaimFlag <- as.factor(as.character(dftrain$ClaimFlag))
  dftest$ClaimFlag <- as.factor(as.character(dftest$ClaimFlag))
  
  #Clean training set - removing characters which brake model 
  dftrain[,sapply(dftrain, is.factor)] <- lapply(dftrain[,sapply(dftrain, is.factor)], function(y) gsub("\\(|\\)|\\[|\\]", "", y)) 
  dftrain[sapply(dftrain, is.character)] <- lapply(dftrain[sapply(dftrain, is.character)], as.factor) #Above converts back to character so need to convert again
  dftrain[,sapply(dftrain, is.factor)] <- lapply(dftrain[,sapply(dftrain, is.factor)], function(y) gsub("\\,", "-", y))
  dftrain[sapply(dftrain, is.character)] <- lapply(dftrain[sapply(dftrain, is.character)], as.factor)
  
  #Clean test set - removing characters which brake model 
  dftest[,sapply(dftest, is.factor)] <- lapply(dftest[,sapply(dftest, is.factor)], function(y) gsub("\\(|\\)|\\[|\\]", "", y))
  dftest[sapply(dftest, is.character)] <- lapply(dftest[sapply(dftest, is.character)], as.factor) #Above converts back to character so need to convert again
  dftest[,sapply(dftest, is.factor)] <- lapply(dftest[,sapply(dftest, is.factor)], function(y) gsub("\\,", "-", y))
  dftest[sapply(dftest, is.character)] <- lapply(dftest[sapply(dftest, is.character)], as.factor)
  
  #One Hot Encode and Normalise Data#
  #Create recipe
  rec_obj <- recipe(ClaimFlag ~ ., data = dftrain) %>%
    step_dummy(all_nominal(), -all_outcomes()) %>%
    step_center(all_predictors(), -all_outcomes()) %>%
    step_scale(all_predictors(), -all_outcomes()) %>%
    prep(data = dftrain)
  
  str(dftrain)
  
  # Predictors
  x_train_tbl <- bake(rec_obj, new_data = dftrain) %>% select(-ClaimFlag)
  x_train_tbl <- x_train_tbl[,colSums(is.na(x_train_tbl))<nrow(x_train_tbl)] #Remove Columns which are NA
  x_train_tbl <- x_train_tbl[ , order(names(x_train_tbl))]
  x_train_tbl <- cbind(x_train_tbl, ClaimFlag=dftrain$ClaimFlag)
  

  x_test_tbl <- bake(rec_obj, new_data = dftest) %>% select(-ClaimFlag)
  x_test_tbl <- x_test_tbl[,colSums(is.na(x_test_tbl))<nrow(x_test_tbl)] #Remove Columns which are NA
  x_test_tbl <- x_test_tbl[ , order(names(x_test_tbl))]
  x_test_tbl <- cbind(x_test_tbl, ClaimFlag=dftest$ClaimFlag, PolicyID=test1$PolicyID)
  
  train_test_list <- list(x_train_tbl, x_test_tbl)
  
  return(train_test_list)
}

