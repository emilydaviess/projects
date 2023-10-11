###################
#INSTALL PACKAGES#
###################

#Graphs! - https://www.r-graph-gallery.com/index.html
#Mongo DB - https://datascienceplus.com/using-mongodb-with-r/

#Machine Learning
if (!require("recipes")) install.packages("recipes")
library(recipes)
if (!require("keras")) install.packages("keras")
library(keras)
if (!require("tensorflow")) install.packages("tensorflow")
library(tensorflow)
#devtools::install_github("rstudio/keras")
if (!require("keras")) install.packages("keras")
library(keras)
#install_keras()

#Data manipulation
if (!require("data.table")) install.packages("data.table")
library(data.table)
if (!require("dplyr")) install.packages("dplyr")
install.packages("dplyr")
if (!require("dplyr")) install.packages("dplyr")
library(dplyr)
if (!require("DT")) install.packages("DT")
library(DT)
if (!require("stringr")) install.packages("stringr")
library(stringr)

#Visualisation
if (!require("corrplot")) install.packages("corrplot")
library(corrplot)
if (!require("plotly")) install.packages("plotly")
library(plotly)
if (!require("RColorBrewer")) install.packages("RColorBrewer")
library(RColorBrewer)
if (!require("ggplot2")) install.packages("ggplot2")
library(ggplot2)
if (!require("dplyr")) install.packages("dplyr")
library(dplyr)

#https://www.r-graph-gallery.com/index.html

## Wordcloud
if (!require("wordcloud")) install.packages("wordcloud")
library(wordcloud)
if (!require("tm")) install.packages("tm")
library(tm)

##############################
#Reading and Preparing Data#
##############################

videos <- read.csv("Data/Youtube/GBvideos.csv")
videos$country <- "gb"

#Import Category and merge HERE!*****

######################
#Goals of the analysis
######################

#We want to answer questions like:

#1.Over what period do we have data for trending videos for GB?  
#2.Which five videos appeared the most on the trending-videos list?
#3.Which category of video appears the most on the trending-videos list?
#4.What proportion of videos on the trending list are Music (category 10)?
#5.Which YouTube channel overall has had the most views in the trending-videos?
#6.What are the top five videos that overall had the..
  #a.Most views in the trending-videos list?
  #b.Most likes in the trending-videos list?
  #c.Most dislikes  in the trending-videos list?
  #d.Most comments  in the trending-videos list?
#7.Which three Music videos (category 10) have had the most likes in the trending-videos list?
#8.How many trending videos contain a fully capitalized word in their titles?
  #a.Is there any correlation between a video having a capitalised word and number of views?
#9.What are the lengths of trending video titles? Does the length of video title correlate with the number of views a video gets?
  #a.Are there any categories which have a high correlation between title length and the number of views a video gets? If so, which, and with a positive/negative correlation?
#10.How are views, likes, dislikes, comment count, title length, and other attributes correlate with (relate to) each other? 
  #a.What is the correlation between views and comment count, is it positively or negatively correlated?
#11.What are the most common words in trending video titles?
#12.When we’re trending videos published? On which days of the week? at which times of the day?
  
#Getting a feel of the dataset.
head(videos)

#Now, let's see some information about our dataset
str(videos) 
#We can see that there are 38,916 entries in the dataset. 
#We can see also that all columns in the dataset are complete and what types they are!

#View the dataset! 
View(videos)

##########################################
#Preparing Data and Feature Engineering#
##########################################

videos$category_id <- as.factor(videos$category_id)
videos$trending_date <- as.Date(videos$trending_date, format = "%y.%d.%m")
videos$publish_date <- as.Date(substr(videos$publish_time,start = 1,stop = 10), format = "%Y-%m-%d")
videos$dif_days <- videos$trending_date - videos$publish_date
videos$year <- format(videos$trending_date,"%Y")
videos$month <- format(videos$trending_date,"%m")
videos$day <- format(videos$trending_date,"%d")




#1. Over what period do we have data for trending videos for GB?  
#table(videos$trending_date)
summary(videos$trending_date)
range(videos$trending_date) #OR
min(videos$trending_date) #OR
max(videos$trending_date) 

#Let's see in which years the dataset was collected
counts<-table(videos$year)
colours <- brewer.pal(8, "Set2")
barplot(counts, 
        main="Number of Videos by Year",
        xlab="Year", col=colours,
        legend = rownames(counts))

counts<-table(videos$month, videos$year)
colours <- brewer.pal(8, "Set2")
barplot(counts, main="Number of Videos by Year",
        xlab="Year", col=colours,
        legend = rownames(counts))


pop_months <- as.data.frame(table(videos$month))












#2. Which five video appeared the most on the trendin-videos list over this period?
video_remained <- as.data.frame(table(videos$title))
names(video_remained) <- c("video_title", "days_trending")
video_remained <- video_remained[order(-video_remained$days_trending),]
View(video_remained)


#5. Which category of video appears the most on the trendin-videos list?
cat_trending <- as.data.frame(table(videos$category_id))
names(cat_trending) <- c("category", "frequency")
cat_trending <- cat_trending[order(-cat_trending$frequency),]

#4a. What proportion of videos on the trending list are category 10?
cat_trending$prop <- cat_trending$Freq/sum(cat_trending$Freq)
cat_trending$perc <- round(cat_trending$frequency/sum(cat_trending$frequency),4)*100
pie(table(videos$category_id), main="Number of Videos by Year",
    xlab="Year", col=colours,
    legend = rownames(table(videos$category_id)))

#5. Which YouTube channel overall has had the most views in the trending-videos?
channel_data <- aggregate(videos$views ~ videos$channel_title, FUN = sum)








channel_trending <- aggregate(videos$views~videos$channel_title, FUN=sum)
names(channel_trending) <- c("channel", "views")
channel_trending <- channel_trending[order(-channel_trending$views),]
channel_trending <- channel_trending[1:15,]
#barplot(height=channel_trending$views, names=channel_trending$channel, col=colours)

#6. What are the top five videos that overall had the most likes in the trending-videos list?
video_likes <- aggregate(videos$likes~videos$title, FUN=sum)
names(video_likes) <- c("video_title", "likes")
video_likes <- video_likes[order(-video_likes$likes),]

#7. Which three Music videos (category 10) have had the most likes in the trending-videos list?
video_likes <- aggregate(videos$likes~videos$title+videos$category_id, FUN=sum)
names(video_likes) <- c("video_title","category_id", "likes")
video_likes <- video_likes[order(-video_likes$likes),]
video_likes <- video_likes[1:15,]


#8a. How many trending videos contain a fully-capitalized word in their titles?
#8a. Is there any correlation between a video having a capitalised word and number of views?

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

videos[,"contains_capitalized"] = apply(videos, 1,contains_capitalized_word)
prop.table(table(videos$contains_capitalized)) #17% include at least one word capitalised!

counts <- table(videos$contains_capitalized)
pie(counts, main="Number of Videos by Year",
    xlab="Year", col=c("darkblue","red"),
    legend = rownames(counts))

videos %>%
  filter(views<1000000) %>%
  ggplot( aes(x=views, group=contains_capitalized, fill=contains_capitalized)) +
  geom_density(adjust=1.5)+
  facet_wrap(~contains_capitalized)+
  theme(
    legend.position="none",
    panel.spacing = unit(0.1, "lines"),
    axis.ticks.x=element_blank()
  )

cor(videos$contains_capitalized, videos$views) #no correlation!

#9.What are the lengths of trending video titles? Does the length of video title correlate with the number of views a video gets?

videos[,"title_length"] = str_length(videos[,"title"])
# - Draw scatter and look at relationship!
p1 <- ggplot(videos, aes(x=title_length, y=views)) + 
  geom_point( color="#69b3a2") +
  geom_smooth(method=lm , color="red", se=TRUE, fill="#69b3a2") #SETS trend line and conf.int
print(p1)

cor(videos$title_length, videos$views)

p1 <- ggplot(videos, aes(x=title_length, y=views, group=category_id, fill = category_id)) + 
  geom_point( color="#69b3a2") +
  facet_wrap(~category_id)+
  geom_smooth(method=lm , color="red", se=TRUE, fill="#69b3a2") #SETS trend line and conf.int
print(p1)
by(videos, videos$category_id, FUN = function(X) cor(X$title_length, X$views)) #Correlation by GROUP category ID! 


#10. How are views, likes, dislikes, comment count, title length, and other attributes correlate with (relate to) each other? How are they connected?
#10a. What is the correlation between views and comment count, is it positively or negativley correlated?

#Now let's see how the dataset variables are correlated with each other: 
#for example, we would like to see how views and likes are correlated, 
#meaning do views and likes increase and decrease together (positive correlation)? 
#Does one of them increase when the other decrease and vice versa (negative correlation)? 
#Or are they not correlated?

#Correlation is represented as a value between -1 and +1 where +1 denotes the highest positive correlation, 
#-1 denotes the highest negative correlation, 
#and 0 denotes that there is no correlation.

corrplot.mixed(corr = cor(videos[,c("views","likes","dislikes","comment_count")]))


#11. What are the most common words in trending music video titles (cat 10)?

#Let's see if there are some words that are used significantly in trending video titles.
#We will display the 25 most common words in all trending video titles.

#Create a vector containing only the text
cat_10 <- videos[videos$category_id == 10,]
titles <- cat_10$title

#Create a corpus  
docs <- Corpus(VectorSource(titles))
docs <- docs %>%
  tm_map(removeNumbers) %>%
  tm_map(removePunctuation) %>%
  tm_map(stripWhitespace)
#docs <- tm_map(docs, content_transformer(tolower))
#docs <- tm_map(docs, removeWords, stopwords("english"))

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


