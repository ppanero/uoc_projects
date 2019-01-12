# Install required libraries
if(!require(dplyr)){
  install.packages('dplyr', repos='http://cran.us.r-project.org')
  library(dplyr)
}
if(!require(ggpubr)){
  install.packages('ggpubr', repos='http://cran.us.r-project.org')
  library(ggpubr)
}

# Constants
datasetDir = "/Users/light/Workspace/uoc_projects/denorm_gourmetdb/denorm_products.csv"

####
# Costs analysis
####

# Read data
data <- read.csv(datasetDir, header=T, sep=',')

# Check columns
dim(data)
str(data)

# Goal: Check if some product or (sub)family is bought to more than a provider.
#       If so, whats the costs, selling price and benefit of each.
filteredData <- select(data, -descripcion_subfamilia, -periodo_pago_proveedor,
                       -telefono_proveedor, -pago_pendiente_proveedor, -direccion_proveedor,
                       -persona_contacto_proveedor, -descripcion_seccion, -descripcion_familia,
                       -nombre_proveedor, -descripcion_producto)
str(filteredData)

# Check and delete repeated values
for (row in 1:nrow(filteredData)) {
  if(filteredData$nombre_seccion[row] != filteredData$seccion_familia[row]) {
    print(sprintf("Different section name for product %s", filteredData$codigo_prodcuto[row]))
  }
  if(filteredData$pais_producto[row] != filteredData$pais_proveedor[row]) {
    print(sprintf("Different country name for product %s", filteredData$codigo_producto[row]))
  }
  if(filteredData$nombre_subfamilia[row] != filteredData$subfamilia_producto[row]) {
    print(sprintf("Different country name for product %s", filteredData$codigo_producto[row]))
  }
  if(filteredData$nombre_familia[row] != filteredData$familia_subfamilia[row]) {
    print(sprintf("Different country name for product %s", filteredData$codigo_producto[row]))
  }
  if(filteredData$codigo_proveedor[row] != filteredData$codigo_proveedor_producto[row]) {
    print(sprintf("Different country name for product %s", filteredData$codigo_producto[row]))
  }
}

filteredData <- select(filteredData, -seccion_familia, -subfamilia_producto, -familia_subfamilia,
                       -codigo_proveedor_producto)

# Only two countries with difference so we ignore it
filteredData <- select(filteredData, - pais_proveedor)

# Alcance_proveedor only three with different than global, makes it not reliable
filteredData <- select(filteredData, -alcance_proveedor)

str(filteredData)

# Check for null values
colSums(filteredData=="NULL", na.rm=T)
# Remove columns with high percentaje of null values
filteredData <- select(filteredData, -tipo_proveedor_proveedor)

# Check for outliers
summary(filteredData$beneficio_producto)
ggdensity(filteredData$beneficio_producto, main="Densidad", xlab = "Beneficio")
ggqqplot(filteredData$beneficio_producto, ylab="Q-Q", xlab="Beneficio")
boxplot(filteredData$beneficio_producto)

# The max value is totally isolated and more than three times the SD from the mean (outlier?)
sd(filteredData$beneficio_producto)
max <- filter(filteredData, beneficio_producto==340.420)
max

# Max benefit matched max cost. Conclusion: Not outlier
summary(filteredData$coste_producto)

# Correlation price / benefit, price / cost and cost / benefit
# TODO

# Check values without maximum
aux <- filter(filteredData, beneficio_producto < 340.420)
ggdensity(aux$beneficio_producto, main="Densidad", xlab = "Beneficio")
ggqqplot(aux$beneficio_producto, ylab="Q-Q", xlab="Beneficio")
boxplot(aux$beneficio_producto)

# stats
# A matrix, each column contains the extreme of the lower whisker, the lower hinge, the median, 
# the upper hinge and the extreme of the upper whisker for one group/plot. If all the inputs 
# have the same class attribute, so will this component.
ranges <- boxplot(aux$beneficio_producto)$stats
aux$beneficio_factor = NA
aux$beneficio_factor[aux$beneficio_producto<4.265] = "lower"
aux$beneficio_factor[aux$beneficio_producto>=4.265 & aux$beneficio_producto < 8.770] = "average"
aux$beneficio_factor[aux$beneficio_producto>=8.770 & aux$beneficio_producto < 18.090] = "avg-high"
aux$beneficio_factor[aux$beneficio_producto>=18.090] = "high"
aux$beneficio_factor[aux$beneficio_producto>=18.090] = "high"
aux$beneficio_factor <- as.factor(aux$beneficio_factor)
summary(aux$beneficio_factor)

# Discretize variables
# No variable needs to be formatted

# Descriptive analysis
# TODO

# Visual analysis
str(aux)
aux$beneficio_factor <- factor(aux$beneficio_factor, levels = c("lower", "average", "avg-high", "high"))
ggplot(data=aux,aes(x=nombre_seccion,fill=beneficio_factor))+geom_bar()
ggplot(data=aux,aes(x=nombre_seccion,fill=beneficio_factor))+geom_bar(position="fill")

# Check details for high and avg-high benefit products
aux_visual <- filter(aux, beneficio_factor == "high" | beneficio_factor == "avg-high")
# Family
ggplot(data=aux_visual,aes(x=nombre_familia,fill=beneficio_factor))+geom_bar()
ggplot(data=aux_visual,aes(x=nombre_familia,fill=beneficio_factor))+geom_bar(position="fill")
# Country
ggplot(data=aux_visual,aes(x=pais_producto,fill=beneficio_factor))+geom_bar()
ggplot(data=aux_visual,aes(x=pais_producto,fill=beneficio_factor))+geom_bar(position="fill")
# Unit type
ggplot(data=aux_visual,aes(x=tipo_unidad_producto,fill=beneficio_factor))+geom_bar()
ggplot(data=aux_visual,aes(x=tipo_unidad_producto,fill=beneficio_factor))+geom_bar(position="fill")
# Brand
# Too many to be plotted in a bar chart to we show a table
tbl <- table(aux_visual$marca_producto, aux_visual$beneficio_factor)
tbl/margin.table(tbl)

# Classification
Y <- aux$beneficio_factor # Classification variable
X <- select(aux, -codigo_producto, -codigo_proveedor, -beneficio_producto, -beneficio_factor,
            -coste_producto, -precio_venta_producto) # Dataset
model <- C50::C5.0(X, Y,rules=TRUE )
summary(model)

