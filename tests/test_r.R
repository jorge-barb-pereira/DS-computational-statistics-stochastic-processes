source("R/attenuation.R")
fails <- function(expression) inherits(try(force(expression), silent = TRUE), "try-error")
set.seed(97); state <- .Random.seed
a <- simulate_attenuation(n = 50000L, slab_length = 2.05, step = 0.1, seed = 12)
stopifnot(identical(state, .Random.seed))
stopifnot(identical(a, simulate_attenuation(n = 50000L, slab_length = 2.05, step = 0.1, seed = 12)))
stopifnot(length(a$event_distances_cm) + a$transmitted == a$n,
          all(diff(a$profile$remaining) <= 0), tail(a$profile$depth_cm, 1) == 2.05)
# Aggregate binomial sampling agreement with the analytic survival probability.
p <- exp(-a$mu * a$slab_length)
stopifnot(abs(a$transmitted - a$n * p) < 6 * sqrt(a$n * p * (1-p)))
stopifnot(all(a$event_distances_cm > 0 & a$event_distances_cm <= a$slab_length))
q <- conditional_exponential_quantile(c(0, 0.2, 0.7, 1), 0.771, 2)
stopifnot(q[1] == 0, q[4] == 2, all(diff(q) > 0))
stopifnot(max(abs((1-exp(-0.771*q))/(1-exp(-0.771*2)) - c(0, 0.2, 0.7, 1))) < 1e-12)
b <- basic_bootstrap_ci(rep(3, 10), replicates = 50)
stopifnot(b$estimate == 3, b$lower == 3, b$upper == 3)
b <- basic_bootstrap_ci(1:20, replicates = 400, seed = 12)
stopifnot(b$lower < b$estimate, b$upper > b$estimate, identical(state, .Random.seed))
stopifnot(fails(simulate_attenuation(n = 0)), fails(simulate_attenuation(mu = -1)),
          fails(simulate_attenuation(mu = 2, step = 1, probability = "linear")),
          fails(basic_bootstrap_ci(1)), fails(basic_bootstrap_ci(c(1, NA))),
          fails(conditional_exponential_quantile(1.1, 1, 1)))
cat("R checks passed: conservation, analytic survival, reproducibility, RNG isolation, conditional quantiles, bootstrap and invalid inputs.\n")
