###################
#INSTALL PACKAGES#
###################

set.seed(123)

library(reshape2)
library(rsample)
library(recipes)
library(keras)
library(tensorflow)
lapply(dbListConnections(MySQL()), dbDisconnect)
'%!in%' <- function(x,y)!('%in%'(x,y))

#devtools::install_github("rstudio/keras")
library(keras)
#install_keras()

#Data manipulation
library(data.table)
library(dplyr)
library(DT)

# Time manipulation
library(lubridate)

# Visualization
library(ggplot2)
if (!require("plotrix")) install.packages("plotrix")
library(plotrix)
if (!require("corrplot")) install.packages("corrplot")
library(corrplot)
if (!require("ggdendro")) install.packages("ggdendro")
library(ggdendro)
if (!require("ggrepel")) install.packages("ggrepel")
library(ggrepel)

## Wordcloud
if (!require("ggrepel")) install.packages("ggrepel")
library(wordcloud)


## Text manipulation
if (!require("tidytext")) install.packages("tidytext")
library(tidytext)
if (!require("stringr")) install.packages("stringr")
library(stringr)
if (!require("tm")) install.packages("tm")
library(tm)
if (!require("sentimentr")) install.packages("sentimentr")
library(sentimentr)
if (!require("RSentiment")) install.packages("RSentiment")
library(RSentiment)


###############################
#Reading and Preparing Data#
###############################

#First thing we are going to do is an analysis of the complete dataset.
#After that we will analyse every region.

ca_videos <- read.csv("Data/Youtube/CAvideos.csv")
de_videos <- read.csv("Data/Youtube/DEvideos.csv")
fr_videos <- read.csv("Data/Youtube/FRvideos.csv")
gb_videos <- read.csv("Data/Youtube/GBvideos.csv")
in_videos <- read.csv("Data/Youtube/INvideos.csv")
jp_videos <- read.csv("Data/Youtube/JPvideos.csv")
kr_videos <- read.csv("Data/Youtube/KRvideos.csv")
mx_videos <- read.csv("Data/Youtube/MXvideos.csv")
ru_videos <- read.csv("Data/Youtube/RUvideos.csv")
us_videos <- read.csv("Data/Youtube/USvideos.csv")

ca_videos$country <- "ca"
de_videos$country <- "de"
fr_videos$country <- "fr"
gb_videos$country <- "gb"
in_videos$country <- "in"
jp_videos$country <- "jp"
kr_videos$country <- "kr"
mx_videos$country <- "mx"
ru_videos$country <- "ru"
us_videos$country <- "us"

#videos <- as.data.table(rbind(gb,fr,ca,us,de))
videos <- as.data.table(rbind(ca_videos, de_videos, fr_videos, gb_videos, in_videos, jp_videos, kr_videos, mx_videos, ru_videos, us_videos))
videos$trending_date <- ydm(videos$trending_date)
videos$publish_time <- ymd(substr(videos$publish_time,start = 1,stop = 10))
videos$dif_days <- videos$trending_date-videos$publish_time

#Analyse Correlation between variables!
corrplot.mixed(corr = cor(videos[,c("category_id","views","likes","dislikes","comment_count")]))
#We can see that between views and likes we have a high correlation, 
#I thought that we will have a similar correlation between views and dislikes, but is almost half of the like correlation.


#2. Find the Most.....

#VIEWED
mvideo_viewed <- videos[,.("Total_Views"=round(sum(views,na.rm = T),digits = 2)),
                 by=.(title,thumbnail_link)][order(-Total_Views)]

mvideo_viewed %>% 
  mutate(image = paste0('<img width="80%" height="80%" src="', thumbnail_link , '"></img>')) %>% 
  arrange(-Total_Views) %>% 
  top_n(10,wt = Total_Views) %>% 
  select(image, title, Total_Views) %>% 
  datatable(class = "nowrap hover row-border", 
            escape = FALSE,
            options = list(dom = 't',scrollX = TRUE, autoWidth = TRUE))

#LIKES
mvideo_like <- videos[,.("Total_Likes"=round(sum(likes,na.rm = T),digits = 2)),
                      by=.(title,thumbnail_link)][order(-Total_Likes)]
mvideo_like %>% 
  mutate(image = paste0('<img width="80%" height="80%" src="', thumbnail_link , '"></img>')) %>% 
  arrange(-Total_Likes) %>% 
  top_n(10,wt = Total_Likes) %>% 
  select(image, title, Total_Likes) %>% 
  datatable(class = "nowrap hover row-border", escape = FALSE, options = list(dom = 't',scrollX = TRUE, autoWidth = TRUE))

#DISLIKES
mvideo_dislikes <- videos[,.("Total_Dislikes"=round(max(dislikes,na.rm = T),digits = 2)),
                 by=.(title,thumbnail_link)][order(-Total_Dislikes)]

mvideo_dislikes %>% 
  mutate(image = paste0('<img width="80%" height="80%" src="', thumbnail_link , '"></img>')) %>% 
  arrange(-Total_Dislikes) %>% 
  top_n(10,wt = Total_Dislikes) %>% 
  select(image, title, Total_Dislikes) %>% 
  datatable(class = "nowrap hover row-border", escape = FALSE, options = list(dom = 't',scrollX = TRUE, autoWidth = TRUE))


#COMMENT COUNT 
mvideo_comments <- videos[,.("Total_comments"=round(max(comment_count,na.rm = T),digits = 2)),by=.(title,thumbnail_link)][order(-Total_comments)]

mvideo_comments %>% 
  mutate(image = paste0('<img width="80%" height="80%" src="', thumbnail_link , '"></img>')) %>% 
  arrange(-Total_comments) %>% 
  top_n(10,wt = Total_comments) %>% 
  select(image, title, Total_comments) %>% 
  datatable(class = "nowrap hover row-border", escape = FALSE, options = list(dom = 't',scrollX = TRUE, autoWidth = TRUE))


#3. Top 10 in percentage
#Because the absolute number of likes, dislikes and comments didnt show all the information to really know if the video had an impact or not we will see their percentages.
mvideo_like_perc <- videos[,.("Percentage_Likes"=round(100*sum(likes,na.rm = T)/sum(views,na.rm = T),digits = 2)),by=.(title,thumbnail_link)][order(-Percentage_Likes)]

mvideo_like_perc %>% 
  mutate(image = paste0('<img width="80%" height="80%" src="', thumbnail_link , '"></img>')) %>% 
  arrange(-Percentage_Likes) %>% 
  top_n(10,wt = Percentage_Likes) %>% 
  select(image, title, Percentage_Likes) %>% 
  datatable(class = "nowrap hover row-border", escape = FALSE, options = list(dom = 't',scrollX = TRUE, autoWidth = TRUE))

#4.Top Trending Channels in all Countries
p <- ggplot(videos[,.N,
              by=channel_title][order(-N)][1:10],
       aes(reorder(channel_title,-N),N,fill=channel_title))
        + geom_bar(stat="identity")
        + geom_label(aes(label=N))
        + guides(fill="none")
        + theme(axis.text.x = element_text(angle = 45,hjust = 1))
        + labs(caption="Donyoe",title=" Top trending channel titles in all countries")
        + xlab(NULL)+ylab(NULL)+coord_flip()

#5.How much time passes between published and trending?
ggplot(videos[dif_days<30],
       aes(as.factor(dif_days),
           fill=as.factor(dif_days)))+geom_bar()+guides(fill="none")+labs(caption="Donyoe",title=" Time between published and trending",subtitle="In days")+xlab(NULL)+ylab(NULL)
#It seems that the videos never trend in the same day it is published.

######################
#Goals of the analysis
######################

#We want to answer questions like:
  
  #1. How many views do our trending videos have? Do most of them have a large number of views? Is having a large number of views required for a video to become trending?
  #2. The same questions above, but applied to likes and comment count instead of views.
  #3. Which video remained the most on the trendin-videos list?
  #4. How many trending videos contain a fully-capitalized word in their titles?
  #5. What are the lengths of trending video titles? Is this length related to the video becoming trendy?
  #6. How are views, likes, dislikes, comment count, title length, and other attributes correlate with (relate to) each other? How are they connected?
  #7. What are the most common words in trending video titles?
  #8. Which YouTube channels have the largest number of trending videos?
  #9. Which video category (e.g. Entertainment, Gaming, Comedy, etc.) has the largest number of trending videos?
  #10. When were trending videos published? On which days of the week? at which times of the day?


#Getting a feel of the dataset.
head(gb_videos)

#Now, let's see some information about our dataset
str(gb_videos)
#We can see that there are 38,916 entries in the dataset. 
#We can see also that all columns in the dataset are complete and what types they are!

#DATA CLEANING#
gb_videos$trending_date <- ydm(gb_videos$trending_date)
gb_videos$publish_time <- ymd(substr(gb_videos$publish_time,start = 1,stop = 10))
gb_videos$dif_days <- gb_videos$trending_date-gb_videos$publish_time
gb_videos$year <- format(gb_videos$trending_date,"%Y")
gb_videos$month <- format(gb_videos$trending_date,"%m")
gb_videos$day <- format(gb_videos$trending_date,"%d")
  
#Dataset collection years
#Let's see in which years the dataset was collected
counts<-table(gb_videos$year)
barplot(counts, main="Number of Videos by Year",
        xlab="Year", col=c("darkblue","red"),
        legend = rownames(counts))


#Views histogram#
#Let's plot a histogram for the views column to take a look at its distribution: 
#to see how many videos have between 10 million and 20 million views, 
#how many videos have between 20 million and 30 million views, and so on.
counts<-table(gb_videos$year)
barplot(counts, main="Number of Videos by Year",
        xlab="Year", col=c("darkblue","red"),
        legend = rownames(counts))

#How many trending video titles contain capitalized word?
#Now we want to see how many trending video titles contain at least a capitalized word (e.g. HOW). 
#To do that, we will add a new variable (column) to the dataset whose value is True if the video title has at least a capitalized word in it, and False otherwise

contains_capitalized_word <- function(row){
  title = row['title'][1]
  for (word in str_split(title," ")[[1]]){ #split each word in title out into chunks
    if (grepl("^[[:upper:]]+$", word)){ #check if whole word is uppercase
      return(TRUE)
    } else {
      return(FALSE)
    }
  }
}

gb_videos[,"contains_capitalized"] = apply(gb_videos, 1,contains_capitalized_word)
prop.table(table(gb_videos$contains_capitalized)) #17% include at least one word capitalised!

counts <- table(gb_videos$contains_capitalized)
pie(counts, main="Number of Videos by Year",
        xlab="Year", col=c("darkblue","red"),
        legend = rownames(counts))

#Video title lengths
#Let's add another column to our dataset to represent the length of each video title, 
#then plot the histogram of title length to get an idea about the lengths of trnding video titles
 
gb_videos[,"title_length"] = str_length(gb_videos[,"title"])
gb_videos[,"description_length"] = str_length(gb_videos[,"description"])
hist(gb_videos$title_length)
#We can see that title-length distribution resembles a normal distribution, 
#where most videos have title lengths between 30 and 60 character approximately.

#Now let's draw a scatter plot between title length and number of views to see the relationship between these two variables
plot(gb_videos$views, gb_videos$title_length)
#By looking at the scatter plot, we can say that there is no relationship between the title length and the number of views. 





#Correlation between dataset variables
#Now let's see how the dataset variables are correlated with each other: 
#for example, we would like to see how views and likes are correlated, 
#meaning do views and likes increase and decrease together (positive correlation)? 
#Does one of them increase when the other decrease and vice versa (negative correlation)? 
#Or are they not correlated?

#Correlation is represented as a value between -1 and +1 where +1 denotes the highest positive correlation, 
#-1 denotes the highest negative correlation, 
#and 0 denotes that there is no correlation.

#Let's see the correlation table between our dataset variables (numerical and boolean variables only)
nums <- unlist(lapply(gb_videos, is.numeric)) 
cor_analysis <- as.data.frame(cor(gb_videos[,nums]))
corrplot(as.matrix(gb_videos[,nums]), is.corr = FALSE)
corrplot.mixed(corr = cor(gb_videos[,nums]))

#Most common words in video titles
#Let's see if there are some words that are used significantly in trending video titles.
#We will display the 25 most common words in all trending video titles.

#Create a vector containing only the text
titles <- gb_videos$title
#Create a corpus  
docs <- Corpus(VectorSource(titles))
docs <- docs %>%
  tm_map(removeNumbers) %>%
  tm_map(removePunctuation) %>%
  tm_map(stripWhitespace)
docs <- tm_map(docs, content_transformer(tolower))
docs <- tm_map(docs, removeWords, stopwords("english"))

dtm <- TermDocumentMatrix(docs) 
matrix <- as.matrix(dtm) 
words <- sort(rowSums(matrix),decreasing=TRUE) 
df <- data.frame(word = names(words),freq=words)

set.seed(1234) # for reproducibility 
wordcloud(words = df$word, 
          freq = df$freq, 
          min.freq = 1, 
          max.words=200, 
          random.order=FALSE, rot.per=0.35,
          colors=brewer.pal(8, "Dark2"))

#For the music category - what words should you include in your title??



#https://www.kaggle.com/ammar111/youtube-trending-videos-analysis



####################
#PREDICTIONS#
####################
str(gb_videos)

gb_model_data <- gb_videos[,c("views","likes","dislikes","comment_count","category_id", "comments_disabled", "ratings_disabled", 
                            "video_error_or_removed", "dif_days", "year", "month", "day",
                            "contains_capitalized", "title_length", "description_length")]
gb_model_data$contains_capitalized <- as.factor(gb_model_data$contains_capitalized)
gb_model_data$dif_days <- as.numeric(gb_model_data$dif_days)
gb_model_data$category_id <- as.factor(as.character(gb_model_data$category_id))
str(gb_model_data)

plot(gb_model_data$likes, gb_model_data$views)

gb_model_data <- gb_videos[gb_videos$ratings_disabled == "False",]
gb_model_data <- gb_model_data[gb_model_data$comments_disabled == "False",]
gb_model_data <- gb_model_data[gb_model_data$dif_days < 50,]
gb_model_data <- gb_model_data[,c("views","likes","dislikes", "comment_count", "dif_days", 
                                  "title_length")]
#gb_model_data$category_id <- as.factor(as.character(gb_model_data$category_id))
gb_model_data$dif_days <- as.numeric(gb_model_data$dif_days)


#Split Into Train/Test Sets
train_test_split <- initial_split(gb_model_data, prop = 0.8)

#We can retrieve our training and testing sets using training() and testing() functions.
train_tbl <- training(train_test_split)
test_tbl  <- testing(train_test_split)

rec_obj <- recipe(views ~ ., data = train_tbl) %>%
  step_dummy(all_nominal(), -all_outcomes()) %>%
  #step_center(all_predictors(), -all_outcomes()) %>%
  #step_scale(all_predictors(), -all_outcomes()) %>%
  prep(data = train_tbl)

#Predictors
x_train_tbl <- bake(rec_obj, new_data = train_tbl) %>% select(-views)
x_train_tbl <- x_train_tbl[,colSums(is.na(x_train_tbl))<nrow(x_train_tbl)] #Remove Columns which are NA
x_test_tbl  <- bake(rec_obj, new_data = test_tbl) %>% select(-views)
x_test_tbl <- x_test_tbl[,names(x_test_tbl) %in% names(x_train_tbl)]


#Response variables for training and testing sets
y_train_vec <- train_tbl$views
y_test_vec <- test_tbl$views


#Set Hyperparams:
nodes1 = c(1000,500, 100)
nodes2 = c(100, 10)
dropout1 = c(0.2)
dropout2 = c(0.2)
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
                  callbacks = list(
                    callback_early_stopping(patience = 5),
                    callback_reduce_lr_on_plateau(factor = lr) #FLAGS$lr_annealing
                  ),
                  verbose = TRUE
                )
                
                predictions <- model_keras %>% predict(as.matrix(x_test_tbl))
                predictions <- round(predictions)
                results <- cbind(test_tbl, predictions)
                cor(results$views, results$predictions)
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






#1. Analysing data we see loads of videos have 0 likes and dislikes - comments disables  - reomve data from our model which don't have data points! 
#2. Add more data points to the model to make it better! - title_length, description_length
