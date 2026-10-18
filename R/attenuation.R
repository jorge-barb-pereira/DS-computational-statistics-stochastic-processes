# Educational first-interaction model. Lengths are cm; mu is in cm^-1.
with_local_seed <- function(seed, expression) {
  if (length(seed) != 1L || !is.finite(seed) || seed < 0 || seed != floor(seed) || seed > .Machine$integer.max)
    stop("seed must be a nonnegative integer within R's integer range")
  existed <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  if (existed) old <- get(".Random.seed", envir = .GlobalEnv)
  on.exit(if (existed) assign(".Random.seed", old, envir = .GlobalEnv)
          else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE))
            rm(".Random.seed", envir = .GlobalEnv))
  set.seed(seed)
  force(expression)
}

simulate_attenuation <- function(n = 1000L, mu = 0.771, slab_length = 10,
                                 step = 0.1, seed = 20231115L,
                                 probability = c("exact", "linear")) {
  probability <- match.arg(probability)
  if (length(n) != 1L || !is.finite(n) || n < 1 || n != floor(n)) stop("n must be a positive integer")
  parameters <- c(mu, slab_length, step)
  if (length(parameters) != 3L || any(!is.finite(parameters)) || any(parameters <= 0))
    stop("mu, slab_length and step must be positive finite scalars")
  if (ceiling(slab_length / step) > 1e6) stop("Too many spatial steps")
  boundaries <- unique(c(seq(0, slab_length, by = step), slab_length))
  widths <- diff(boundaries)
  p <- if (probability == "exact") -expm1(-mu * widths) else mu * widths
  if (any(p > 1)) stop("Linear step probability exceeds one; use smaller steps")
  with_local_seed(seed, {
    remaining <- numeric(length(boundaries)); remaining[1] <- n
    events <- numeric(length(widths))
    for (i in seq_along(widths)) {
      events[i] <- rbinom(1, remaining[i], p[i])
      remaining[i + 1L] <- remaining[i] - events[i]
    }
    list(profile = data.frame(depth_cm = boundaries, remaining = remaining,
                              expected = n * exp(-mu * boundaries)),
         event_distances_cm = rep(boundaries[-1], events),
         interactions = events, transmitted = tail(remaining, 1),
         n = n, mu = mu, slab_length = slab_length, probability = probability)
  })
}

conditional_exponential_quantile <- function(p, mu, slab_length) {
  if (any(!is.finite(p)) || any(p < 0 | p > 1) || length(mu) != 1L ||
      length(slab_length) != 1L || !is.finite(mu) || !is.finite(slab_length) ||
      mu <= 0 || slab_length <= 0) stop("Invalid conditional exponential parameters")
  result <- -log1p(-p * (-expm1(-mu * slab_length))) / mu
  result[p == 1] <- slab_length
  result
}

basic_bootstrap_ci <- function(x, statistic = mean, replicates = 500L,
                                level = 0.99, seed = 20231115L) {
  if (!is.numeric(x) || length(x) < 2L || any(!is.finite(x))) stop("At least two finite observations required")
  if (length(replicates) != 1L || !is.finite(replicates) || replicates < 2 || replicates != floor(replicates))
    stop("replicates must be an integer >= 2")
  if (length(level) != 1L || !is.finite(level) || level <= 0 || level >= 1) stop("level must be in (0,1)")
  estimate <- statistic(x)
  if (length(estimate) != 1L || !is.finite(estimate)) stop("statistic must return a finite scalar")
  samples <- with_local_seed(seed, replicate(replicates, statistic(x[sample.int(length(x), replace = TRUE)])))
  if (any(!is.finite(samples))) stop("Nonfinite bootstrap statistic")
  alpha <- (1 - level) / 2
  interval <- 2 * estimate - quantile(samples, c(1 - alpha, alpha), names = FALSE)
  list(estimate = estimate, lower = interval[1], upper = interval[2],
       level = level, replicates = replicates, samples = samples)
}
