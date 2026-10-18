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

mu= 0.809
lamb = 1/0.809
dl = 0.1
dP_int = mu *dl

#That way we have 8.1% of aproximated probability of occurting interaction of a
#1 MeV photon with 0.1 cm lenght of lead


#A ideia agr é criar 50 experiencias binomiais para simular a propagação dos fotões
# ao longo dos 5cm de chumbo em steps de 0.1cm

# Podemos partir de 10^6 fotões 

N=10^6

step_1 = rbinom(N, 1, dP_int)
hist(step_1)
step_1_interactions = sum(step_1)

N_2 = N - step_1_interactions

#Appying narrow beam geometry aproximation that states that a photon with inte
