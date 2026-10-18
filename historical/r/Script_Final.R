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
set.seed(20231115)

mu= 0.771
dx = 0.1
P_int = mu *dx

#That way we have 7.71% of approximated probability of occurring interaction of a
#1 MeV photon with 0.1 cm length of lead


N_i = 10^3
N_photons = N_i
photons = c(N_i)
steps_length = c(0)
interactions = c(0)
steps_length_sample = c()

#-From Bernoulli Trial
for (i in 1:100) {
  step_length = i*dx
  
  step_sample = sample(x=c(1,0),
                       prob=c(P_int,1-P_int),
                       size=N_photons, 
                       replace = TRUE)
  
  step_interactions = sum(step_sample)
  N_photons = N_photons - step_interactions
  
  photons = c(photons,N_photons)
  interactions = c(interactions,step_interactions)
  steps_length = c(steps_length,step_length)
  steps_length_sample = c(steps_length_sample,rep(step_length,step_interactions))
  }


plot <- ggplot(main="Exponential Q-Q Plot") + geom_col(aes(x=steps_length, y=photons), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps_length, y=N_i*exp(-steps_length*mu)), color="red",)
plot <- plot + labs(x = "Total Steps Length (cm)", y="Number of Remaining Photons") + ggtitle("Number of Remaining Photons along 10 centimeters lenght of a Pb medium")
plot

p_interactions = interactions/N_i
plot <- ggplot() + geom_col(aes(x=steps_length, y=p_interactions), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps_length, y=mu*dx*exp(-(steps_length)*mu)), color="red",)
plot <- plot + labs(x = "Total Steps Length (cm)", y="Proportions of Photons Interactions") + ggtitle("Proportion of Photons Interactions along 10 centimeters lenght of a Pb medium")
plot

#Cumulative plot
cum_p_interactions <- cumsum(p_interactions)
plot <- ggplot() + geom_col(aes(x=steps_length, y=cum_p_interactions), color="white", fill="blue")
plot <- plot + geom_line(aes(x=steps_length, y=1-exp(-(steps_length)*mu)), color="red",)
plot <- plot + labs(x = "Total Steps Length (cm)", y="Cumulative Proportions of Interactions") + ggtitle("Cumulative Proportion of Photons Interactions along 10 centimeters lenght of a Pb medium")
plot

# Create a Q-Q plot with an exponential distribution reference
p <- ppoints(1000)    # 250 equally spaced points on (0,1), excluding endpoints
q <- quantile(steps_length_sample,p=p) # percentiles of the sample distribution
plot(qexp(p) ,q, main="Exponential Q-Q Plot",
     xlab="Theoretical Quantiles of the Exponential Distribution (cm)",ylab="Sample Quantiles of the Simulated Sample (cm)"
     , pch = 16, cex=0.4)
qqline(q, distribution=qexp,col="red", lty=2) 

#######################################

# dados: amostra de distâncias percorridas
n=length(steps_length_sample)
# estimar intervalos bootstrap
media_empirica <- mean(steps_length_sample)
# 500 replicas
B=500
dados.star = sample(steps_length_sample, B*n, replace=TRUE)
boots.amostra <- matrix(dados.star, nrow=B, ncol=n)
## Calcular as médias de cada amostra bootstrap x*
bootsmu <- rowMeans(boots.amostra)
hist(bootsmu,  breaks = 25)
summary(bootsmu)
## Calcular w* para cada amostra bootstrap
wstar = bootsmu-media_empirica
## Determinar 0.005 e 0.995 quantis para wstar
d <- quantile(wstar, c(0.005, 0.995)) # para um grau de confiança de 99%
# determinar o IC a 99% para a média
ic_mean <- media_empirica-c(LI=d[2], LS=d[1])

########### IC PARA A MEDIANA ###############
mediana_empirica <- median(steps_length_sample)
m <- dim(boots.amostra)[1]
bootmedian <- NULL

for (i in 1:m){
  bootmedian[i] <- median(boots.amostra[i,])  
}
hist(bootmedian , breaks = 25)
summary(bootmedian)
## Calcular w* para cada amostra bootstrap
wstar = bootmedian - mediana_empirica
## Determinar 0.005 e 0.995 quantis para wstar
d <- quantile(wstar, c(0.005, 0.995)) # para um grau de confiança de 99%
# determinar o IC a 99% para a mediana
ic_median <- mediana_empirica-c(LI=d[2], LS=d[1])


########### IC PARA O PERCENTIL (EX 0.95) ###############
q_empirico <- quantile(steps_length_sample,probs=0.95)
m <- dim(boots.amostra)[1]
bootquartil <- NULL

for (i in 1:m){
  bootquartil[i]<-quantile(boots.amostra[i,], probs = 0.95)  
}
hist(bootquartil , breaks = 25)
summary(bootquartil)
## Calcular w* para cada amostra bootstrap
wstar <- bootquartil - q_empirico
## Determinar 0.005 e 0.995 quantis para wstar
d <- quantile(wstar, c(0.005, 0.995)) # para um grau de confiança de 99%
# determinar o IC a 99% para quantil 95
ic_95quantile <- q_empirico-c(LI=d[2], LS=d[1])

