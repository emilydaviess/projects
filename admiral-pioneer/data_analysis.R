#Create SQLite connection
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
policy_data <- policy_data[policy_data$TimeInsured == 1,]


#######################
#DATA CLEANING#
#######################

#Without further knowledge on missing values for TimeInsured, and as it's only 2.9% of data, we'll exclude for now. 
#policy_data <- policy_data[!is.na(policy_data$TimeInsured),]
#CreditScore=0 is a massive outlier, and without more information, we'll also exlcude this. 
policy_data <- policy_data[which(policy_data$CreditScore != 0),]
#Zip Population = 0 is also evidence of incorrect data. 
policy_data <- policy_data[which(policy_data$ZIP_Population != 0),]

#Create a test dataset. I will use 80/20 split. 
#The test/validation set must be kept completely seperate to development/training.
policy_data$value <- 1 #Set this so we can sum in our summarise
samp_size <- floor(0.8*nrow(policy_data))

#Set seed to make partition reproducable
set.seed(101)
valid_ind <- sample(seq_len(nrow(policy_data)), size = samp_size)

train <- policy_data[valid_ind,]
test <- policy_data[-valid_ind,]

#Summarise stats - We want equal proportions of Claims in each dataset
train %>% summarise(total = sum(value), sum_response = sum(ClaimFlag), perc = (sum_response/total)*100) #7.05%
test %>% summarise(total = sum(value), sum_response = sum(ClaimFlag), perc = (sum_response/total)*100) #7.14% 

###############################
#Binning Continous Variables
###############################

#Using woe.binning we are able to get the WOE (weight of evidene) and IV (information value) showing how each 'bin' discrimiates the response.
#The higher the IV the more influence it has on the reponse. 
b_CreditScore <- as.data.frame(woe.binning(train, 'ClaimFlag', 'CreditScore'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_CreditScore$var1 <- "CreditScore"
b_Age <- as.data.frame(woe.binning(train, 'ClaimFlag', 'Age'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_Age$var1 <- "Age"
b_NewestVehicleAge <- as.data.frame(woe.binning(train, 'ClaimFlag', 'NewestVehicleAge'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_NewestVehicleAge$var1 <- "NewestVehicleAge"
b_ZIP_AverageHomeValue <- as.data.frame(woe.binning(train, 'ClaimFlag', 'ZIP_AverageHomeValue'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_ZIP_AverageHomeValue$var1 <- "ZIP_AverageHomeValue"
b_ZIP_AverageIncomee <- as.data.frame(woe.binning(train, 'ClaimFlag', 'ZIP_AverageIncome'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_ZIP_AverageIncomee$var1 <- "ZIP_AverageIncome"
b_ZIP_Population <- as.data.frame(woe.binning(train, 'ClaimFlag', 'ZIP_Population'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_ZIP_Population$var1 <- "ZIP_Population"
b_ZIP_LandArea <- as.data.frame(woe.binning(train, 'ClaimFlag', 'ZIP_LandArea'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_ZIP_LandArea$var1 <- "ZIP_LandArea"
b_NumberOfVehicles <- as.data.frame(woe.binning(train, 'ClaimFlag', 'NumberOfVehicles'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_NumberOfVehicles$var1 <- "NumberOfVehicles"
b_PriorAccidentCount <- as.data.frame(woe.binning(train, 'ClaimFlag', 'PriorAccidentCount'))[,c("woe", "cutpoints.final", "cutpoints.final..1.", "iv.total.final", "X0", "X1")]
b_PriorAccidentCount$var1 <- "PriorAccidentCount"
cont_woe_df <- rbind(b_CreditScore,b_Age,b_NewestVehicleAge,b_NumberOfVehicles,b_PriorAccidentCount,b_ZIP_AverageHomeValue,b_ZIP_AverageIncomee,b_ZIP_Population,b_ZIP_LandArea)

###############################
#Binning Categorical Variables
###############################

#State
b_State <- as.data.frame(woe.binning(train, 'ClaimFlag', 'State'))[,c("woe", "Group.1","Group.2", "iv.total.final", "X0", "X1")]
b_State$var1 <- "State"
#CoverageGap
b_CoverageGap <- as.data.frame(woe.binning(train, 'ClaimFlag', 'CoverageGap'))[,c("woe", "Group.1","Group.2", "iv.total.final", "X0", "X1")]
b_CoverageGap$var1 <- "CoverageGap"

cat_woe_df <- rbind(b_State,b_CoverageGap)
names(cat_woe_df)[names(cat_woe_df) == 'Group.1'] <- 'cutpoints.final'
names(cat_woe_df)[names(cat_woe_df) == 'Group.2'] <- 'cutpoints.final..1.'

#Concat all dataframes together to get WOE and IV against response variable
all_woe <- rbind(cont_woe_df,cat_woe_df)
all_woe <- all_woe[which(all_woe$iv.total.final > 0.001),] #Remove any variables with very low IV - no influence on response. 
