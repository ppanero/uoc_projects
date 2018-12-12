# Install required libraries
if(!require(dplyr)){
    install.packages('dplyr', repos='http://cran.us.r-project.org')
    library(dplyr)
}
if(!require(ggpubr)){
    install.packages('ggpubr', repos='http://cran.us.r-project.org')
    library(ggpubr)
}
if(!require(VIM)){
  install.packages('VIM', repos='http://cran.us.r-project.org')
  library(VIM)
}
if(!require(C50)){
    install.packages('C50', repos='http://cran.us.r-project.org')
    library(C50)
}
if(!require(arules)){
    install.packages('arules', repos='http://cran.us.r-project.org')
    library(arules)
}

# Absolute path to the dataset
datasetDir = "./original_dataset/"
# Read training and testing datasets
dataTrain <- read.csv(paste(datasetDir, "train.csv", sep="/"), stringsAsFactors=FALSE, header = TRUE)
dataTest <- read.csv(paste(datasetDir, "test.csv", sep="/"), stringsAsFactors=FALSE, header = TRUE)

#####
# Integration and selection of the attributes to use
#####

# Dataset dimensions
dim(dataTrain)
dim(dataTest)

# Variables class
vars <- sapply(dataTrain, class)
table(data.frame(variables=names(vars), clase=as.vector(vars)))

# Remove PassangerId, Name and Ticket attributes
View(dataTrain)
filteredData <- select(dataTrain, -PassengerId)
filteredData <- select(filteredData, -Name)
filteredData <- select(filteredData, -Ticket)

# Explore the obtained dataset
str(filteredData)

# Discretize the corresponding variables and check the type
colsToFactor<-c("Survived","Pclass","Sex","Embarked")
for (i in colsToFactor){
    filteredData[,i] <- as.factor(filteredData[,i])
}
str(filteredData)

# Explore SibSp and Parch
summary(as.factor(filteredData$SibSp))
summary(as.factor(filteredData$Parch))

#####
# Data cleaning
#####

#
# Check for NAs, empty or null values
#

# Check empty / NA values
colSums(is.na(filteredData))
colSums(filteredData=="", na.rm=T)
colSums(filteredData==" ", na.rm=T)
colSums(filteredData<0, na.rm=T)

# Check levels mismatch
levels(filteredData$Survived)
levels(filteredData$Pclass)
levels(filteredData$Sex)
levels(filteredData$Embarked)
# Check Embarked distribution of values
summary(filteredData$Embarked)

# Delete Cabin attribute
View(filteredData)
filteredData <- select(filteredData, -Cabin)

# Assign NAs to empty values to use KNN imputation
filteredData$Embarked[filteredData$Embarked==""]=NA
# Assing values based on KNN
filteredData <- kNN(filteredData, variable = c("Embarked", "Age"))
# Check the assigned values make sense
filteredData$Embarked[62]
filteredData$Embarked[830]
filteredData$Age[18]
filteredData$Age[30]
filteredData$Age[236]

# Remove generated attributes from the KNN imputation
filteredData <- select(filteredData, -Embarked_imp)
filteredData <- select(filteredData, -Age_imp)

# Crosscheck that there are no empty values
colSums(is.na(filteredData))
colSums(filteredData=="", na.rm=T)
colSums(filteredData==" ", na.rm=T)
colSums(filteredData<0, na.rm=T)

#
# Attribute Engineering
#

# Create attribute Family Size (FSize)
filteredData$FSize <- filteredData$SibSp + filteredData$Parch + 1
filteredData$SibSp <- as.factor(filteredData$SibSp)
filteredData$Parch <- as.factor(filteredData$Parch)

# Check and discretize the new attribute
summary(as.factor(filteredData$FSize))
filteredData$FSize <- as.factor(filteredData$FSize)

#
# Treat extreme values
#

# Get box plots graphics
boxplot(filteredData$Age)
boxplot(filteredData$Fare)

# Get box plot extreme values
boxplot(filteredData$Age)$out
boxplot(filteredData$Fare)$out

# Get max age from extreme values
max(boxplot(filteredData$Age)$out)

# Get min fare from extreme values
min(boxplot(filteredData$Fare)$out)

# Study fare extreme values in relation to pclass
pclass_min <- filteredData$Pclass[filteredData$Fare >= 66.6]
summary(pclass_min)
mean(boxplot(filteredData$Fare)$out)
pclass_mean <- filteredData$Pclass[filteredData$Fare >= 128.2916]
summary(pclass_mean)
highPrice <- filteredData$Fare[filteredData$Fare> 500]
highPrice
lowPrice <- filteredData$Fare[filteredData$Fare == 0]
lowPrice
sd(filteredData$Fare)
# Mark as NA the extreme values an imputate based on KNN
filteredData$Fare[filteredData$Fare == 0 | filteredData$Fare > 500]=NA
filteredData <- kNN(filteredData, variable = c("Fare"))

####
# Check normality and homogeneity of variance
####

# Check graphically the results
ggplot(data=filteredData[filteredData$Fare_imp==TRUE,], aes(x=Fare))+geom_histogram(binwidth = 10)+facet_wrap(~Pclass)

# Remove imputation generated attribute
filteredData <- select(filteredData, - Fare_imp)

# Get density and QQ plots
ggdensity(filteredData$Age, main="Densidad", xlab = "Age")
ggdensity(filteredData$Fare, main="Densidad", xlab = "Fare")
ggqqplot(filteredData$Age, ylab="Q-Q", xlab="Age")
ggqqplot(filteredData$Fare, ylab="Q-Q", xlab="Fare")

# Carry out Shapiro Tests
shapiro.test(filteredData$Age)
shapiro.test(filteredData$Fare)

# Carry out Flinger Killneen test
fligner.test(Age ~ Fare, filteredData)

####
# Data analysis
####

#
# Correlation tests
#

# Check correlation of categorical variables
corr_matrix <- matrix(nc = 2, nr = 0) 
colnames(corr_matrix) <- c("variable", "p-value")
categoricas <- select(filteredData, -Survived, -Age, -Fare)
for(i in 1:(ncol(categoricas))) {
    pair = matrix(ncol = 2, nrow = 1)
    pair[1][1] = colnames(categoricas)[i]
    pair[2][1] = chisq.test(filteredData$Survived, categoricas[,i])$p.value
    corr_matrix <- rbind(corr_matrix, pair)
}

corr_matrix

# Check correlation of numerical variables
anova_fare <- aov(Fare ~ Survived, filteredData)
summary(anova_fare)

anova_age <- aov(Age ~ Survived, filteredData)
summary(anova_age)

#
# Classification
#

# Sanitize empty levels tags
levels(filteredData$Embarked)[1] = "missing"

# Check, prepare data and run C50
dim(filteredData)
Y <- filteredData[,1] # Classification variable
X <- filteredData[,2:9] # Dataset
model <- C50::C5.0(X, Y,rules=TRUE )
summary(model)

#
# Association rules
#

# Discretize numerical variables
filteredData$AgeFactor <- NA # Age
filteredData$AgeFactor[filteredData$Age < 5] = "Baby"
filteredData$AgeFactor[filteredData$Age > 5 & filteredData$Age < 15] = "Kid"
filteredData$AgeFactor[filteredData$Age >= 5 & filteredData$Age < 15] = "Kid"
filteredData$AgeFactor[filteredData$Age >= 15 & filteredData$Age < 25] = "Young"
filteredData$AgeFactor[filteredData$Age >= 25 & filteredData$Age < 50] = "Adult"
filteredData$AgeFactor[filteredData$Age >= 50] = "Elder"
filteredData$AgeFactor <- as.factor(filteredData$AgeFactor)
filteredData$FareFactor <- NA # Fare
filteredData$FareFactor[filteredData$Fare < 12] = "Cheap"
filteredData$FareFactor[filteredData$Fare >= 12 & filteredData$Fare < 30] = "Medium"
filteredData$FareFactor[filteredData$Fare >= 30 & filteredData$Fare < 100] = "Expensive"
filteredData$FareFactor[filteredData$Fare >= 100] = "Ridiciulous"
filteredData$FareFactor <- as.factor(filteredData$FareFactor)

# Plot the new attributes to crosscheck
ggplot(data=filteredData,aes(x=AgeFactor,fill=Survived))+geom_bar(position="fill")
ggplot(data=filteredData,aes(x=FareFactor,fill=Survived))+geom_bar(position="fill")

# Generate dataset, binarize data and run Apriori
asociationData <- select(filteredData, -Age, -Fare)
mba <- as(asociationData, "transactions")
summary(mba)

rules <- apriori(mba, parameter = list(supp = 0.05, conf = 0.95), appearance=list(rhs='Survived=1',default='lhs'))

# Sort based on confidence and inspect rules
rules <- sort(rules, by="confidence", decreasing=TRUE)
inspect(rules[1:6], ruleSep = "---->", itemSep = " + ", setStart = "", setEnd ="", linebreak = FALSE)


####
# Graphical representation
####

# Sex
ggplot(data=filteredData,aes(x=Sex,fill=Survived))+geom_bar()
ggplot(data=filteredData,aes(x=Sex,fill=Survived))+geom_bar(position="fill")
# Age
ggplot(data=filteredData,aes(x=Age,fill=Survived))+geom_histogram(binwidth=3)
ggplot(data=filteredData,aes(x=Age,fill=Survived))+geom_histogram(binwidth=3, position="fill")
# Age and Sex
ggplot(data=filteredData, aes(x=Age, fill=Survived))+geom_histogram(binwidth = 10)+facet_wrap(~Sex)
ggplot(data=filteredData, aes(x=Age, fill=Survived))+geom_histogram(binwidth = 10, position="fill")+facet_wrap(~Sex)
# Fare
ggplot(data=filteredData,aes(x=Fare,fill=Survived))+geom_histogram(binwidth=20)
ggplot(data=filteredData,aes(x=Fare,fill=Survived))+geom_histogram(binwidth=20, position="fill")
# PClass
ggplot(data=filteredData,aes(x=Pclass,fill=Survived))+geom_bar()
ggplot(data=filteredData,aes(x=Pclass,fill=Survived))+geom_bar(position="fill")
# SibSp
ggplot(data=filteredData,aes(x=SibSp,fill=Survived))+geom_bar()
ggplot(data=filteredData,aes(x=SibSp,fill=Survived))+geom_bar(position="fill")
# Parch
ggplot(data=filteredData,aes(x=Parch,fill=Survived))+geom_bar()
ggplot(data=filteredData,aes(x=Parch,fill=Survived))+geom_bar(position="fill")
# FSize
ggplot(data=filteredData,aes(x=FSize,fill=Survived))+geom_bar()
ggplot(data=filteredData,aes(x=FSize,fill=Survived))+geom_bar(position="fill")
# Embarked
ggplot(data=filteredData,aes(x=Embarked,fill=Survived))+geom_bar()
ggplot(data=filteredData,aes(x=Embarked,fill=Survived))+geom_bar(position="fill")
