###################
#INSTALL PACKAGES#
###################

#Data manipulation
library(data.table)
library(dplyr)
library(DT)
library(stringr)

#Visualisation
if (!require("corrplot")) install.packages("corrplot")
library(corrplot)
if (!require("plotly")) install.packages("plotly")
library(plotly)
library(RColorBrewer)
library(ggplot2)
library(dplyr)

#https://www.r-graph-gallery.com/index.html

## Wordcloud
if (!require("ggrepel")) install.packages("wordcloud")
library(wordcloud)

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

videos$trending_date <- as.Date(videos$trending_date, format = "%y.%d.%m")
videos$publish_date <- as.Date(substr(videos$publish_time,start = 1,stop = 10), format = "%Y-%m-%d")
videos$dif_days <- videos$trending_date-videos$publish_date
videos$year <- format(videos$trending_date,"%Y")
videos$month <- format(videos$trending_date,"%m")
videos$day <- format(videos$trending_date,"%d")
videos[,"title_length"] = str_length(videos[,"title"])
videos[,"description_length"] = str_length(videos[,"description"])

#Dataset collection years
#Let's see in which years the dataset was collected
counts<-table(videos$year)
colours <- brewer.pal(8, "Set2")
barplot(counts, main="Number of Videos by Year",
        xlab="Year", col=colours,
        legend = rownames(counts))


counts<-table(videos$month, videos$year)
colours <- brewer.pal(8, "Set2")
barplot(counts, main="Number of Videos by Year",
        xlab="Year", col=colours,
        legend = rownames(counts))

#Let's plot a histogram for the views column to take a look at its distribution: 
#to see how many videos have between 10 million and 20 million views, 
#how many videos have between 20 million and 30 million views, and so on.
#hist(videos$views)
ggplot(data=videos, aes(x=views)) +
  geom_density(adjust=1.5) +
  theme(
    legend.position="none",
    panel.spacing = unit(0.1, "lines"),
    axis.ticks.x=element_blank()
  )

#Make the histogram
#1. How many views do our trending videos have? 
summary(videos$views)
tapply(videos$views, videos$category_id, summary)
#Do most of them have a large number of views? 
#Is having a large number of views required for a video to become trending?
#Which categories require large number of views to trend?
#Which categories require smaller numbers of views to trend?
videos %>%
  filter(views<1000000) %>%
  ggplot( aes(x=views, group=category_id, fill=category_id)) +
  geom_density(adjust=1.5)+
  facet_wrap(~category_id)+
  theme(
    legend.position="none",
    panel.spacing = unit(0.1, "lines"),
    axis.ticks.x=element_blank()
  )

#2. The same questions above, but applied to likes and comment count instead of views.



#3. Which video remained the most on the trendin-videos list?
video_remained <- as.data.frame(table(videos$title))
names(video_remained) <- c("video_title", "days_trending")
video_remained <- video_remained[order(-video_remained$days_trending),]

#4. Which category of video appears the most on the trendin-videos list?
cat_trending <- as.data.frame(table(videos$category_id))
names(cat_trending) <- c("category", "frequency")
cat_trending <- cat_trending[order(-cat_trending$frequency),]

#4a. What proportion of videos on the trending list are category 10?
cat_trending$perc <- round(cat_trending$frequency/sum(cat_trending$frequency),4)*100
pie(table(videos$category_id), main="Number of Videos by Year",
    xlab="Year", col=colours,
    legend = rownames(table(videos$category_id)))

#5. Which channel_title has overall had the most views in the trendin-videos list?
channel_trending <- aggregate(videos$views~videos$channel_title, FUN=sum)
names(channel_trending) <- c("channel", "views")
channel_trending <- channel_trending[order(-channel_trending$views),]
channel_trending <- channel_trending[1:15,]
barplot(height=channel_trending$views, names=channel_trending$channel, col=colours)

#6. What are the the top 5 videos that overall had the most likes in the trendin-videos list?
video_likes <- aggregate(videos$likes~videos$title, FUN=sum)
names(video_likes) <- c("video_title", "likes")
video_likes <- video_likes[order(-video_likes$likes),]
#video_likes <- video_likes[1:15,]
barplot(height=video_likes$likes, names=video_likes$video_title, col=colours)

#7. Which 3 music videos (cat 10) have had the most likes in the trendin-videos list?
video_likes <- aggregate(videos$likes~videos$title+videos$category_id, FUN=sum)
names(video_likes) <- c("video_title","category_id", "likes")
video_likes <- video_likes[order(-video_likes$likes),]
#video_likes <- video_likes[1:15,]
barplot(height=video_likes$likes, names=video_likes$video_title, col=colours)


#8a. How many trending videos contain a fully-capitalized word in their titles?
#8b. Is there any correlation between a video haveing a capitalised word and number of views?

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

#9.Is there a relationship between title length, and number of views?
# - Draw scatter and look at relationship!
p1 <- ggplot(videos, aes(x=title_length, y=views, group=category_id, fill = category_id)) + 
  geom_point( color="#69b3a2") +
  facet_wrap(~category_id)+
  geom_smooth(method=lm , color="red", se=TRUE, fill="#69b3a2") #SETS trend line and conf.int
print(p1)


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

corrplot.mixed(corr = cor(videos[,c("category_id","views","likes","dislikes","comment_count")]))


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


