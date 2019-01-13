# Install required libraries
if(!require(dplyr)){
  install.packages('dplyr', repos='http://cran.us.r-project.org')
  library(dplyr)
}
if(!require(ggpubr)){
  install.packages('ggpubr', repos='http://cran.us.r-project.org')
  library(ggpubr)
}
if(!require(arules)){
  install.packages('arules', repos='http://cran.us.r-project.org')
  library(arules)
}

# Constants
datasetDir = "/Users/light/Workspace/uoc_projects/denorm_gourmetdb/denorm_orders.csv"

####
# Order delay and stock analysis
####

# Read data
data <- read.csv(datasetDir, header=T, sep=',')

# Check dataset and select interesting variables

str(data)
filteredData <- select(data, codigo_producto_pedido, codigo_pedido, codigo_proveedor,
                       nombre_tienda, pais_tienda, tiempo_entrega_pedido,
                       excfal_pedido, pais_proveedor)
str(filteredData)
filteredData$codigo_proveedor <- as.factor(filteredData$codigo_proveedor)
filteredData$codigo_pedido <- as.factor(filteredData$codigo_pedido)
filteredData$codigo_producto_pedido <- as.factor(filteredData$codigo_producto_pedido)

# Analyze delays
summary(filteredData$tiempo_entrega_pedido)
ggdensity(filteredData$tiempo_entrega_pedido, main="Densidad", xlab = "Retraso")
ggqqplot(filteredData$tiempo_entrega_pedido, ylab="Q-Q", xlab="Retraso")
boxplot(filteredData$tiempo_entrega_pedido)

# Analyze delays
summary(filteredData$excfal_pedido)
ggdensity(filteredData$excfal_pedido, main="Densidad", xlab = "Exceso/Falta mercancia")
ggqqplot(filteredData$excfal_pedido, ylab="Q-Q", xlab="Exceso/Falta mercancia")
boxplot(filteredData$excfal_pedido)

# Create factor for missing stock
filteredData$missing_stock[filteredData$excfal_pedido < 0] = 1
filteredData$missing_stock[filteredData$excfal_pedido == 0] = 0
filteredData$missing_stock <- as.factor(filteredData$missing_stock)

# Classification
Y <- filteredData$missing_stock # Classification variable
X <- select(filteredData, -codigo_pedido, -excfal_pedido, -missing_stock) # Dataset
model <- C50::C5.0(X, Y,rules=TRUE )
summary(model)

Y <- filteredData$missing_stock # Classification variable
X <- select(filteredData, -codigo_producto_pedido, -codigo_pedido, -excfal_pedido, -missing_stock) # Dataset
model <- C50::C5.0(X, Y,rules=TRUE )
summary(model)

# Association
asociationData <- select(filteredData, -codigo_pedido, 
                         -excfal_pedido, -tiempo_entrega_pedido) # Dataset
mba <- as(asociationData, "transactions")
rules <- apriori(mba, parameter = list(supp = 0.05, conf = 0.80), appearance=list(rhs='missing_stock=1',default='lhs'))
