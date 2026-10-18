# Model definitions

## First interaction in a slab

For constant linear attenuation coefficient `mu`, survival at depth `x` is `S(x) = exp(-mu*x)`. Over a bin of width `dx`, the exact interaction probability is `1-exp(-mu*dx)`. The maintained R model uses `-expm1(-mu*dx)` for numerical stability and draws a binomial count from the remaining population. The original scripts' linear approximation `mu*dx` is available as `probability="linear"` for comparison, with a check that the probability cannot exceed one.

Each photon undergoes at most one recorded interaction. Photons surviving the entire slab are right-censored at its boundary. Recorded interaction locations are right endpoints of bins, including a shorter final bin when necessary.

The conditional reference CDF for interaction inside a slab of length `L` is `(1-exp(-mu*x))/(1-exp(-mu*L))`, for `0 <= x <= L`. Its quantile is `-log(1-p*(1-exp(-mu*L)))/mu`. The Q-Q plot compares binned measurements with this continuous conditional reference; small steps from discretization are expected.

The nonparametric basic bootstrap uses `2*estimate - quantile(bootstrap_estimates, [1-alpha/2, alpha/2])`. Its target is the chosen statistic of the **observed conditional, binned depth distribution**. It does not undo binning or recover unobserved transmitted depths. The default 99% intervals and 1,000 resamples are a demonstration; tail interval endpoints can be noisy and coverage is not established here. Separate bootstrap calls use a fixed seed for reproducibility, not independent inference across the three statistics.

## Photon transport

The maintained Python example launches independent 1 MeV primaries at the center of the entrance face of a 10 cm cube. Directions are unit vectors. The free-path distance is exponentially distributed with rate `density*(photoelectric_mass_coefficient + Compton_mass_coefficient)`. Coefficients are linearly interpolated on the supplied 0.05, 0.1, 0.5 and 1 MeV table; extrapolation is rejected. Only the two modeled partial coefficients contribute to the interaction rate.

Photoelectric events deposit all remaining energy locally. Compton events use the free-electron Klein-Nishina angular weight and outgoing energy `E' = E/(1+(E/0.511)*(1-cos(theta)))`. The energy difference is deposited at the interaction voxel. Azimuth is uniform. The rejection envelope is 2 for the unnormalized angular weight over uniform `cos(theta)`. A stable orthonormal basis handles rotations at both axial poles. For the physical background, consult the [OpenMC photon-physics methods](https://docs.openmc.org/en/stable/methods/photon_physics.html); this portfolio implements a much smaller model.

The cube uses half-open spatial bounds `[0,L)` and voxel edge lengths `L/grid_size`. A sampled next interaction outside the cube terminates the photon as escaped. At or below the default 0.05 MeV cutoff, residual energy is deposited at the current voxel; this approximation is recorded separately as `cutoff_deposited_mev`. That value is a **subset of deposition**, never an extra energy component. If the interaction limit is reached, remaining energy is reported as unresolved rather than silently discarded.

Every batch must satisfy:

```text
source_mev = deposited_mev + escaped_mev + unresolved_mev
0 <= cutoff_deposited_mev <= deposited_mev
```

Mass coefficients in cm^2/g and density in g/cm^3 imply a rate in cm^-1. These units reflect the original notebook's convention; the numerical tables themselves have not been validated against an authoritative dataset. Names `legacy-lead` and `legacy-water` indicate their historical origin. They are illustrative inputs, not calibrated material models.

## Uncertainty and memory

A history in the public API is an independent **batch of primaries**, not a single photon track. Each voxel tally is divided by the number of primaries per batch. For B independent batches, Welford's algorithm computes the mean and sample variance with denominator B-1; standard error is `sqrt(sample_variance/B)`. A small B does not establish convergence. A zero observed tally and zero estimated SEM can reflect insufficient sampling.

Voxel-array memory is O(grid_size^3), independent of the number of batches; scalar energy ledgers and spawned random seeds grow with batch count. The API limits the grid to at most 128 voxels per axis and requires at least two batches for SEM. The maintained model does not reproduce every multi-beam or interactive-volume experiment in the historical notebook.
