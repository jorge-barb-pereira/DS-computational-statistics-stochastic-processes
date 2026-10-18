source("R/attenuation.R")
args <- commandArgs(trailingOnly = TRUE)
output <- if (length(args)) args[1] else "output/r"
dir.create(output, recursive = TRUE, showWarnings = FALSE)
model <- simulate_attenuation()
x <- model$event_distances_cm
statistics <- list(mean = mean, median = median, percentile_95 = function(y) unname(quantile(y, 0.95)))
intervals <- lapply(statistics, function(f) basic_bootstrap_ci(x, f, replicates = 1000L))
summary <- do.call(rbind, lapply(names(intervals), function(name) {
  b <- intervals[[name]]
  data.frame(statistic = name, estimate_cm = b$estimate, lower_cm = b$lower,
             upper_cm = b$upper, confidence_level = b$level,
             observed_interactions = length(x), transmitted = model$transmitted)
}))
write.csv(summary, file.path(output, "bootstrap_intervals.csv"), row.names = FALSE)
write.csv(model$profile, file.path(output, "attenuation_profile.csv"), row.names = FALSE)
png(file.path(output, "attenuation.png"), width = 1500, height = 1100, res = 140)
par(mfrow = c(2, 2), mar = c(4.5, 4.5, 3, 1))
plot(model$profile$depth_cm, model$profile$remaining, type = "s", col = "#18788a",
     xlab = "Depth (cm)", ylab = "Photons remaining", main = "First-interaction attenuation")
lines(model$profile$depth_cm, model$profile$expected, col = "#d45a35", lwd = 2)
legend("topright", c("Simulation", "N exp(-mu x)"), col = c("#18788a", "#d45a35"), lty = 1, bty = "n")
plot(model$profile$depth_cm[-1], model$interactions / model$n, type = "h",
     xlab = "Right endpoint of bin (cm)", ylab = "Fraction of incident photons",
     main = "First interaction per spatial bin", col = "#18788a")
lines(model$profile$depth_cm[-1], -diff(exp(-model$mu * model$profile$depth_cm)), col = "#d45a35")
reference <- conditional_exponential_quantile(ppoints(length(x)), model$mu, model$slab_length)
plot(reference, sort(x), pch = 16, cex = 0.35, col = "#18788a",
     xlab = "Conditional exponential quantile (cm)", ylab = "Observed bin endpoint (cm)",
     main = "Conditional Q-Q plot (binned data)")
abline(0, 1, col = "#d45a35", lwd = 2)
hist(intervals$mean$samples, breaks = 30, col = "#18788a", border = "white",
     xlab = "Mean observed interaction depth (cm)", main = "Bootstrap means: conditional sample")
abline(v = c(intervals$mean$lower, intervals$mean$upper), col = "#d45a35", lwd = 2, lty = 2)
invisible(dev.off())
print(summary)
