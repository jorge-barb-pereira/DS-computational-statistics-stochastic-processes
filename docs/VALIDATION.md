# Validation record

The maintained implementation is checked separately from the historical sources. The full original notebook is not executed because some experiments allocate large history arrays and contain known defects.

## Automated checks

- Python: energy accounting for both legacy materials and early termination; cutoff accounting; reproducible seeds; rotations at both poles; Compton energy-angle consistency; voxel boundary conventions; streaming mean and SEM against an independent retained-batch calculation; invalid inputs; CLI output readability.
- R: photon counts, monotone survival, analytic binomial survival within six standard deviations, reproducible seeds, preservation of the caller's RNG state, conditional exponential quantile inversion, degenerate and nondegenerate bootstrap intervals, invalid inputs.
- Integrity: four original R byte hashes and all 19 original notebook code-cell source hashes, stripped notebook output and bounded historical files.
- Integration: execution of the small maintained notebook and generation of both Python and R demonstration outputs.

## Recorded results: 18 October 2026

[Scientific checks run 39121436768](https://github.com/jorge-barb-pereira/computational-statistics-stochastic-processes/actions/runs/39121436768) completed successfully for implementation commit `62b5e10`:

| Environment | Result |
| --- | --- |
| Windows, Python 3.12, NumPy 2.3.5, Matplotlib 3.10.9 | Nine Python tests passed; demo, maintained notebook and integrity audit passed |
| GitHub-hosted Ubuntu, Python 3.11 | Nine Python tests, installed-package demo, notebook and integrity audit passed |
| GitHub-hosted Ubuntu, Python 3.12 | Nine Python tests, installed-package demo, notebook and integrity audit passed |
| GitHub-hosted Ubuntu, R release | All R assertions and the attenuation/bootstrap demo passed; generated outputs uploaded as `r-demo` |

R was not installed in the local Windows environment; its verification was performed by the real R interpreter in CI. The local Python CLI run used four batches of 300 primaries, seed 42 and a 24-cubed grid. Mean deposited energy was approximately **0.998743 MeV per primary**, with zero unresolved energy in those batches. These numbers describe that seeded educational example only.

`assets/transport.png` comes from that local Python run. `assets/attenuation.png` is the actual R-generated figure retrieved from the successful CI run. Both images were visually inspected. The original 75,304,287-byte notebook becomes a 41,130-byte source-only notebook, retaining all 19 code-cell source hashes.

Reproduction commands are in the README. The final preview and validation update changes documentation and assets only.

These checks establish implementation behavior and bookkeeping. They do not validate material data, prove distributional coverage of bootstrap intervals or establish transport accuracy against a benchmark.
