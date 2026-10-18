# Validation record

The maintained implementation is checked separately from the historical sources. The full original notebook is not executed because some experiments allocate large history arrays and contain known defects.

## Automated checks

- Python: energy accounting for both legacy materials and early termination; cutoff accounting; reproducible seeds; rotations at both poles; Compton energy-angle consistency; voxel boundary conventions; streaming mean and SEM against an independent retained-batch calculation; invalid inputs; CLI output readability.
- R: photon counts, monotone survival, analytic binomial survival within six standard deviations, reproducible seeds, preservation of the caller's RNG state, conditional exponential quantile inversion, degenerate and nondegenerate bootstrap intervals, invalid inputs.
- Integrity: four original R byte hashes and all 19 original notebook code-cell source hashes, stripped notebook output and bounded historical files.
- Integration: execution of the small maintained notebook and generation of both Python and R demonstration outputs.

GitHub Actions runs Python on 3.11 and 3.12 and R in a separate job. Reproduction commands are in the README. Run results and preview provenance are recorded after remote validation.

These checks establish implementation behavior and bookkeeping. They do not validate material data, prove distributional coverage of bootstrap intervals or establish transport accuracy against a benchmark.
