###################
#LIBRAIRES#
###################

if(!require(plotly)) install.packages("plotly")
library(plotly)
if(!require(plyr)) install.packages("plyr")
library(plyr)
if(!require(formattable)) install.packages("formattable")
library(formattable)
if(!require(dplyr)) install.packages("dplyr")
library(dplyr)

###################
#DATA INPUT#
###################

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

#####################
#DATA CLEANING#
#####################

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

data <- rbind(ca_videos, de_videos, fr_videos, gb_videos, in_videos, jp_videos, kr_videos, mx_videos, ru_videos, us_videos)
rm(ca_videos)
rm(de_videos)
rm(fr_videos)
rm(gb_videos)
rm(in_videos)
rm(jp_videos)
rm(kr_videos)
rm(mx_videos)
rm(ru_videos)
rm(us_videos)


#1. What are the most liked/disliked Videos Per Country - do they differ?

#2. How does category preference differ per country?
cat_pref_country_likes <- aggregate(data$likes~data$category_id+data$country, FUN=sum)
names(cat_pref_country_likes) <- c("category", "country", "likes")
total_country_likes <- aggregate(data$likes~data$country, FUN=sum)
names(total_country_likes) <- c("country", "total_country_likes")
cat_pref_country <- merge(cat_pref_country_likes, total_country_likes, by = c("country"))
cat_pref_country$like_perc <- round(cat_pref_country$likes/cat_pref_country$total_country_likes,4)*100



#3. Build a model which predicts the number of likes a video will get - this could be used for advertising prices etc. 

#4. How has category of videos popularity changed over the years - statistical analysis?

#5. Analysing what factors affect how popular a YouTube video will be?

#6. -	Build a YouTube Video Recommendations Engine – Find out what videos your peers like, or dislike and create a machine learning model to make predictions and recommendations of what they should watch next.


