#-------- Intro --------
#
# We are going to simulate how a narrow beam of photons with energy 1MeV
#(typical energies used on Megavoltage radiotherapy) 
# propagate and intereact with 5 cm of a medium composed by Lead
#
# Each photon has a propability of interacting with each element of path in the medium
# This probability is translated in linear attenuation coeficient (mu). 
# For the interaction of 1MeV photons with lead: mu = 0.809 cm^(-1)

# It is possible to decomponde the 5 cm lenght of medium in smaller ones for exp.
# with lenght of 0.1 cm.

# In this case we can aproximate the probability of interaction of a photon with
# a 0.1 cm lenght of lead medium by:
library(ggplot2)

mu= 0.809
lamb = 1/0.809
dl = 0.1
dP_int = mu *dl

#That way we have 8.1% of aproximated probability of occurting interaction of a
#1 MeV photon with 0.1 cm lenght of lead


#A ideia agr é criar 50 experiencias binomiais para simular a propagação dos fotões
# ao longo dos 5cm de chumbo em steps de 0.1cm

# Podemos partir de 10^6 fotões 

N_i = 10^3
N_photons = N_i
photons = c(N_i)
steps = c(0)
interactions = c(0)
path_length = c() #Variavel aleatoria a estudar



#-------From Binomial Experiment
#
#for (x in 1:50) {
#  step_1 = rbinom(N, 1, dP_int)
#  step_1_interactions = sum(step_1)
#  N = N - step_1_interactions
#  photons = c(photons,N)
#}

#-From Bernoulli Experiment

for (x in 1:50) {
  step = x*0.1
  
  step_sample = sample(x=c(0,1),
                       prob=c(1-dP_int,dP_int),
                       size=N_photons, 
                       replace = TRUE)
  
  step_interactions = sum(step_sample)
  N_photons = N_photons - step_interactions
  
  photons = c(photons,N_photons)
  interactions = c(interactions,step_interactions)
  steps = c(steps,step)
  path_length = c(path_length,rep(step,step_interactions))}


plot <- ggplot() + geom_col(aes(x=steps, y=photons), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps, y=N_i*exp(-steps*mu)), color="red",)
plot <- plot + labs(x = "Distance (cm)", y="Existing photons")
plot

plot <- ggplot() + geom_col(aes(x=steps, y=interactions/N_i), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps, y=mu*dl*exp(-(steps)*mu)), color="red",)
plot <- plot + labs(x = "Distance (cm)", y="Proportions of Interactions")
plot

#Appying narrow beam geometry aproximation that states that a photon with inte

# Create a Q-Q plot with an exponential distribution reference

hist(path_length,breaks = 50)

qqplot(quantile(path_length), pexp(ppoints(length(steps)), rate = mu), main = "Q-Q Plot with Exponential Distribution Reference")
abline(0, 1, col = "red")  # Add a reference line

#######################################

y=N_i*exp(-steps*mu)
n_f<-NULL
for (i in 2:51) {
  j=i-1
  n_f[j]<--(y[i]-y[i-1])
}

sum(n_f*steps[2:51])/N_i # distância média percorrida por um fotão (em cm)

df<-data.frame(distancias=steps[2:51],n_fotoes=round(n_f))

n<-dim(df)[1]
distancias<-NULL
for (i in 1:n) {
  distancias<-c(distancias,rep(df[i,1],each=df[i,2]))
}

# dados: amostra de distâncias percorridas
n=length(distancias)
# estimar intervalos bootstrap
(media_empirica<-mean(distancias))
# 200 replicas
B=200
set.seed(111) #para resultados reprodutívies
dados.star = sample(distancias, B*n, replace=TRUE)

boots.amostra= matrix(dados.star, nrow=B, ncol=n)

## Calcular as médias de cada amostra bootstrap x*
bootsmu = rowMeans(boots.amostra)
## Calcular w* para cada amostra bootstrap
wstar = bootsmu-media_empirica
## Determinar 0.05 e 0.95 quantis para wstar
d =(quantile(wstar, c(0.05, 0.95))) # para um grau de confiança de 90%
# determinar o IC a 90% para \mu
(ic = media_empirica-c(LI=d[2], LS=d[1]))

