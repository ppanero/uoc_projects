# Install required libraries
if(!require(dplyr)){
  install.packages('dplyr', repos='http://cran.us.r-project.org')
  library(dplyr)
}
if(!require(ggpubr)){
  install.packages('ggpubr', repos='http://cran.us.r-project.org')
  library(ggpubr)
}
if(!require(cluster)){
  install.packages('cluster', repos='http://cran.us.r-project.org')
  library(cluster)
}

# Constants
datasetDir = "/home/ppanero/workspace/uoc/uoc_projects/denorm_gourmetdb/denorm_clients.csv"

####
# Order delay and stock analysis
####

# Read data
data <- read.csv(datasetDir, header=T, sep=',')

# Check dataset and select interesting variables
str(data)
filteredData <- select(data, -direccion_cliente, -codigo_cliente, -nombre_cliente, -fecha_nacimiento_cliente)

# Check for null values
colSums(filteredData=="NULL", na.rm=T)
nrow(subset(filteredData, numero_hijos_cliente=="NULL" & estado_civil_cliente == "NULL"))

# Clustering without columns with NULL
nocolnull <- select(filteredData, -numero_hijos_cliente, -estado_civil_cliente)

# Source: https://www.r-bloggers.com/clustering-mixed-data-types-in-r/
# Use Gower distance for dissimilarity matrix
gower_dist <- daisy(nocolnull, metric = "gower", type = list(logratio = 3))
summary(gower_dist)

# Sanity check
gower_mat <- as.matrix(gower_dist)

# Most similar
nocolnull[which(gower_mat == min(gower_mat[gower_mat != min(gower_mat)]), arr.ind = TRUE)[1, ], ]

# Most different
nocolnull[which(gower_mat == max(gower_mat[gower_mat != max(gower_mat)]),arr.ind = TRUE)[1, ], ]

results <- rep(0, 10)
for (i in c(2,3,4,5,6,7,8,9,10))
{
 pam_fit <- pam(gower_dist, diss = TRUE, k = i)
 results[i] <- pam_fit$silinfo$avg.width
}
plot(2:10,results[2:10],type="o",col="blue",pch=0,xlab="Numero de clusters",ylab="Silueta")
# K=3 is optimal
pam_fit <- pam(gower_dist, diss = TRUE, k = 3)

# Visualization
tsne_obj <- Rtsne(gower_dist, is_distance = TRUE)

tsne_data <- tsne_obj$Y %>% data.frame() %>% setNames(c("X", "Y")) %>%
  mutate(cluster = factor(pam_fit$clustering), name = data$codigo_cliente)

ggplot(aes(x = X, y = Y), data = tsne_data) + geom_point(aes(color = cluster))

# # Not optimal
# # Clustering without rows with NULL
# norownull <- filter(filteredData, numero_hijos_cliente!="NULL" & estado_civil_cliente != "NULL")
# colSums(norownull=="NULL", na.rm=T)
#
# # Use Gower distance for dissimilarity matrix
# gower_dist <- daisy(norownull, metric = "gower", type = list(logratio = 3))
# summary(gower_dist)
#
# Sanity check
# gower_mat <- as.matrix(gower_dist)
#
# # Most similar
# norownull[which(gower_mat == min(gower_mat[gower_mat != min(gower_mat)]), arr.ind = TRUE)[1, ], ]
#
# # Most different
# norownull[which(gower_mat == max(gower_mat[gower_mat != max(gower_mat)]),arr.ind = TRUE)[1, ], ]
#
# results <- rep(0, 10)
# for (i in c(2,3,4,5,6,7,8,9,10))
# {
#   pam_fit <- pam(gower_dist, diss = TRUE, k = i)
#   results[i] <- pam_fit$silinfo$avg.width
# }
# plot(2:10,results[2:10],type="o",col="blue",pch=0,xlab="Numero de clusters",ylab="Silueta")

