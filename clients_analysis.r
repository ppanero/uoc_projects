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
if(!require(plyr)){
  install.packages('plyr', repos='http://cran.us.r-project.org')
  library(plyr)
}
if(!require(forcats)){
  install.packages('forcats', repos='http://cran.us.r-project.org')
  library(forcats)
}
if(!require(cluster)){
  install.packages('cluster', repos='http://cran.us.r-project.org')
  library(cluster)
}
if(!require(Rtsne)){
  install.packages('Rtsne', repos='http://cran.us.r-project.org')
  library(Rtsne)
}

# Constants
datasetDir = "/home/ppanero/workspace/uoc/uoc_projects/denorm_gourmetdb/denorm_clients.csv"

##############################
# Clients profiling analysis #
##############################

####
# Load data
####

# Read data
data <- read.csv(datasetDir, header=T, sep=',')

# Check dataset and select interesting variables
dim(data)
str(data)

####
# Select interesting data (Data cleaning)
####

filteredData <- select(data, -direccion_cliente, -codigo_cliente, -nombre_cliente, -fecha_nacimiento_cliente)

# Check for null values
colSums(filteredData=="NULL", na.rm=T)
nrow(subset(filteredData, numero_hijos_cliente=="NULL" & estado_civil_cliente == "NULL"))

# Clean wrong values
filteredData$total_compras_cliente[filteredData$total_compras_cliente == 0] = NA
colSums(is.na(filteredData))
filteredData <- kNN(filteredData, variable = c("total_compras_cliente"), dist_var = c("puntos_acumulados_cliente"))
# Delete imp boolean column
filteredData <- select(filteredData, -total_compras_cliente_imp)

# Descriptive analysis
for(i in names(filteredData)){
  tbl <- table(filteredData[,i])
  print(i)
  print(tbl/sum(tbl))
}

filteredData <- select(filteredData, -region_cliente)

# Total de compras y Puntos acumulados
hist(filteredData$puntos_acumulados_cliente, xlab="", main="Puntos acumulados cliente")
hist(filteredData$total_compras_cliente, xlab="", main="Total compras cliente")
# Compras
filteredData$total_compras_cliente[filteredData$total_compras_cliente > 30] = 30
filteredData$total_compras_cliente[filteredData$total_compras_cliente > 25 & filteredData$total_compras_cliente < 30] = 25
counts <- table(filteredData$total_compras_cliente)
barplot(counts,  main="Total compras cliente", las=3)
# Puntos
filteredData$puntos_acumulados_cliente[filteredData$puntos_acumulados_cliente > 30] = 30
filteredData$puntos_acumulados_cliente[filteredData$puntos_acumulados_cliente > 20 & filteredData$puntos_acumulados_cliente < 30] = 20
counts <- table(filteredData$puntos_acumulados_cliente)
barplot(counts,  main="Puntos acumulados cliente", las=3)
# Filter total buyings
filteredData <- select(filteredData, -total_compras_cliente)

# Edad
hist(filteredData$edad_cliente, xlab="", main="Edad cliente")

# Profesion
profesion_plot <- revalue(filteredData$profesion_cliente, 
                          c("Architectos-Decoradores-&-Humanistas"="Architectos",
                            "Economistas-Abogados-&-Admin.Empresas"="Economistas",
                            "Gerentes-&-Directivos"="Gerentes",
                            "Ingenieros-&-Especialistas"="Ingenieros",
                            "Doctores-&-Profesionales-de-la-Salud"="Doctores"))
counts <- table(fct_infreq(profesion_plot))
par(mar=c(5.1, 8.1, 4.1, 2.1))
barplot(counts, main="Profesion cliente", las=1, horiz=TRUE)
# Filter out "Food" occurences
filteredData <- filter(filteredData, profesion_cliente != "Food")

####
# Clustering
####
# Clustering without columns with NULL
noColNull <- select(filteredData, -numero_hijos_cliente, -estado_civil_cliente)
# noColNull <- select(filteredData, -numero_hijos_cliente, -estado_civil_cliente,
#                      -puntos_acumulados_cliente)

# Use Gower distance for dissimilarity matrix
gower_dist <- daisy(noColNull, metric = "gower")
summary(gower_dist)

# Sanity check
gower_mat <- as.matrix(gower_dist)

# Most similar
noColNull[which(gower_mat == min(gower_mat[gower_mat != min(gower_mat)]), arr.ind = TRUE)[1, ], ]

# Most different
noColNull[which(gower_mat == max(gower_mat[gower_mat != max(gower_mat)]),arr.ind = TRUE)[1, ], ]

results <- rep(0, 10)
for (i in c(2,3,4,5,6,7,8,9,10))
{
 pam_fit <- pam(gower_dist, diss = TRUE, k = i)
 results[i] <- pam_fit$silinfo$avg.width
}
plot(2:10,results[2:10],type="o",col="blue",pch=0,xlab="Numero de clusters",ylab="Silueta")
# K=3 is optimal
pam_fit <- pam(gower_dist, diss = TRUE, k = 9)

# Visualization
tsne_obj <- Rtsne(gower_dist, is_distance = TRUE)
tsne_data <- tsne_obj$Y %>% data.frame() %>% setNames(c("X", "Y")) %>%
  mutate(cluster = factor(pam_fit$clustering), name = filter(data, profesion_cliente != "Food")$codigo_cliente)

ggplot(aes(x = X, y = Y), data = tsne_data) + geom_point(aes(color = cluster))

# Show clusters examples
noColNull[pam_fit$medoids, ]

# # Not optimal
# # Clustering without rows with NULL
# noRowNull <- filter(filteredData, numero_hijos_cliente!="NULL" & estado_civil_cliente != "NULL")
# colSums(noRowNull=="NULL", na.rm=T)
# 
# # Use Gower distance for dissimilarity matrix
# gower_dist <- daisy(noRowNull, metric = "gower")
# summary(gower_dist)
# 
# # Sanity check
# gower_mat <- as.matrix(gower_dist)
# 
# # Most similar
# noRowNull[which(gower_mat == min(gower_mat[gower_mat != min(gower_mat)]), arr.ind = TRUE)[1, ], ]
# 
# # Most different
# noRowNull[which(gower_mat == max(gower_mat[gower_mat != max(gower_mat)]),arr.ind = TRUE)[1, ], ]
# 
# results <- rep(0, 10)
# for (i in c(2,3,4,5,6,7,8,9,10))
# {
#   pam_fit <- pam(gower_dist, diss = TRUE, k = i)
#   results[i] <- pam_fit$silinfo$avg.width
# }
# plot(2:10,results[2:10],type="o",col="blue",pch=0,xlab="Numero de clusters",ylab="Silueta")

