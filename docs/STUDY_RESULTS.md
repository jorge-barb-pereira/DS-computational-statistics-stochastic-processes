# Recorded study results

Full experiment run on 18 October 2026 using Python 3.12.14, NumPy 2.3.5, SciPy 1.18.1 and Matplotlib 3.10.9. The [design and reproduction commands](STUDIES.md) define the model and estimators. Run metadata and individual batch estimates are retained in [results](../results/).

## Transport sampling convergence

Legacy-water; 1 MeV central beam; 10 cm cube; 12 voxels per axis; cutoff 0.05 MeV; 24 independent batches at each photon count; root seed 20261018. The full study simulated **105,600 primaries**, with conserved energy ledgers and no unresolved energy.

| Photons per batch | Mean deposited MeV per primary | SD across batch estimates | Approximate 95% interval for grand mean | Relative interval half-width |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 0.275540 | 0.036869 | [0.259972, 0.291109] | 5.650% |
| 300 | 0.277021 | 0.016073 | [0.270234, 0.283808] | 2.450% |
| 1,000 | 0.273803 | 0.010219 | [0.269488, 0.278118] | 1.576% |
| 3,000 | 0.275226 | 0.005431 | [0.272932, 0.277519] | 0.833% |

The fitted slope of log(batch SD) versus log(N) is **-0.542**, approximately consistent with the expected -0.5 rate. This is descriptive evidence from four settings, not a formal acceptance test. The 0.833% relative half-width applies to the grand mean over **24 x 3,000 = 72,000 photons** at the largest setting, not to a single 3,000-photon batch or every voxel.

The independent analytic transmission benchmark uses p = exp(-0.771 x 2) = **0.213952768**. Its observed RMSE need not decrease monotonically or match the theoretical curve exactly with only 24 replicates:

| N | Empirical transmission RMSE | Exact binomial RMSE | Wilson 95% intervals containing exact p |
| ---: | ---: | ---: | ---: |
| 100 | 0.037338 | 0.041009 | 24/24 |
| 300 | 0.018515 | 0.023677 | 23/24 |
| 1,000 | 0.011867 | 0.012968 | 24/24 |
| 3,000 | 0.008917 | 0.007487 | 21/24 |

The observed 87.5% coverage at N = 3,000 is reported rather than discarded. Twenty-four trials cannot precisely assess nominal 95% coverage. No claim that coverage has been established is made.

## Absorbing-chain benchmark

Twenty transient spatial states, two terminal states and 50,000 independent paths; mu = 0.771 cm^-1, length 2 cm and bin width 0.1 cm; seed 20261019.

| Quantity | Exact calculation | Simulated paths |
| --- | ---: | ---: |
| Transmission probability | 0.213952768 | 0.217280000 |
| Absorption/first-interaction probability | 0.786047232 | 0.782720000 |
| Mean transitions to termination | 10.593239 | 10.637680 |

The exact exponential transmission and fundamental-matrix result differ by less than 1e-15. The simulated transmission's Wilson 99% interval is **[0.212567, 0.222068]**, containing the exact value. There were **39,136 first interactions** and **10,864 transmitted paths**. Every transition-matrix row sums to one to floating-point precision.

These results demonstrate agreement within the simplified first-interaction model. They do not independently validate the 3D scattering engine or the material coefficients. Both figures were generated from these full-run results and visually checked.
