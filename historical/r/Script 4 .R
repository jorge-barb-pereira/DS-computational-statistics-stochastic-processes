#-------- Intro --------
#
# We are going to simulate how a narrow beam of photons with energy 1MeV
# propagate and interact with the matter of a 10 cm length medium composed by Lead
#
# Each photon has a probability of interacting with each element of path of the medium
# This probability is translated in linear attenuation coeficient (mu). 
# For the interaction of 1MeV photons with lead: mu = 0.809 cm^(-1)

# It is possible to decompose the 10 cm length of medium in to smaller ones 
# with 0.1 cm length.

# In this case we can aproximate the probability of interaction of a photon with
# a 0.1 cm lenght of lead medium by:
library(ggplot2)

mu= 0.771
dx = 0.1
P_int = mu *dx

#That way we have 8.1% of approximated probability of occurring interaction of a
#1 MeV photon with 0.1 cm length of lead


N_i = 10^3
N_photons = N_i
photons = c(N_i)
steps = c(0)
interactions = c(0)
path_length = c()

#-From Bernoulli Experiment

for (i in 1:100) {
  step = i*dx
  
  step_sample = sample(x=c(1,0),
                       prob=c(P_int,1-P_int),
                       size=N_photons, 
                       replace = TRUE)
  
  step_interactions = sum(step_sample)
  N_photons = N_photons - step_interactions
  
  photons = c(photons,N_photons)
  interactions = c(interactions,step_interactions)
  steps = c(steps,step)
  path_length = c(path_length,rep(step,step_interactions))
  }


plot <- ggplot() + geom_col(aes(x=steps, y=photons), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps, y=N_i*exp(-steps*mu)), color="red",)
plot <- plot + labs(x = "Distance (cm)", y="Existing photons")
plot

plot <- ggplot() + geom_col(aes(x=steps, y=interactions/N_i), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps, y=mu*dx*exp(-(steps)*mu)), color="red",)
plot <- plot + labs(x = "Distance (cm)", y="Proportions of Interactions")
plot

#Appying narrow beam geometry aproximation that states that a photon with inte

# Create a Q-Q plot with an exponential distribution reference
#Cumulative plot

plot <- ggplot() + geom_histogram(aes(x=path_length), binwidth=0.1, color="white", fill="blue")
plot

frequency_vector <- layer_data(plot)$count
plot <- ggplot() + geom_col(aes(x = seq(0.1,length(frequency_vector)*0.1, length.out=length(frequency_vector)), y=cumsum(frequency_vector)), color="white", fill="blue")
plot

qqplot(quantile(path_length), pexp(ppoints(length(steps)), rate = mu), main = "Q-Q Plot with Exponential Distribution Reference")
abline(0, 1, col = "red")  # Add a reference line

#######################################

# dados: amostra de distâncias percorridas
n=length(path_length)
# estimar intervalos bootstrap
media_empirica <- mean(path_length)
# 200 replicas
B=200
set.seed(111) #para resultados reprodutívies
dados.star = sample(path_length, B*n, replace=TRUE)

boots.amostra <- matrix(dados.star, nrow=B, ncol=n)

## Calcular as médias de cada amostra bootstrap x*
bootsmu <- rowMeans(boots.amostra)
## Calcular w* para cada amostra bootstrap
wstar = bootsmu-media_empirica
## Determinar 0.05 e 0.95 quantis para wstar
d <- unname(quantile(wstar, c(0.05, 0.95))) # para um grau de confiança de 90%
# determinar o IC a 90% para \mu
ic_mean <- media_empirica-c(LI=d[2], LS=d[1])

########### IC PARA A MEDIANA ###############
mediana_empirica <- median(path_length)
m <- dim(boots.amostra)[1]
bootmedian <- NULL

for (i in 1:m){
  bootmedian[i] <- median(boots.amostra[i,])  
}

## Calcular w* para cada amostra bootstrap
wstar = bootmedian - mediana_empirica
## Determinar 0.05 e 0.95 quantis para wstar
d <- unname(quantile(wstar, c(0.05, 0.95))) # para um grau de confiança de 90%
# determinar o IC a 90% para \mu
ic_median <- mediana_empirica-c(LI=d[2], LS=d[1])


########### IC PARA O PERCENTIL (EX 0.95) ###############
q_empirico <- quantile(path_length,probs=0.95)
m <- dim(boots.amostra)[1]
bootquartil <- NULL

for (i in 1:m){
  bootquartil[i]<-quantile(boots.amostra[i,], probs = 0.95)  
}

## Calcular w* para cada amostra bootstrap
wstar <- bootquartil - q_empirico
## Determinar 0.05 e 0.95 quantis para wstar
d <- unname(quantile(wstar, c(0.05, 0.95))) # para um grau de confiança de 90%
# determinar o IC a 90% para \mu
ic_95quantile <- q_empirico-c(LI=d[2], LS=d[1])
