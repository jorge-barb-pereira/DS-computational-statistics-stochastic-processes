# Review and maintenance decisions

| Original observation | Maintained treatment |
| --- | --- |
| R uses `mu*dx`, a first-order bin probability | Default uses exact `1-exp(-mu*dx)`; comparison mode retained |
| R comments cite 0.809 while the final code sets mu to 0.771 | Defaults follow the executable final value, labeled illustrative |
| Q-Q comparisons use an unrestricted/unit-rate exponential or mismatched quantities | Conditional reference includes the actual mu and finite slab length |
| Transmitted photons are absent from bootstrap depth samples | Count them explicitly and define the conditional estimand |
| Draft bootstrap code differs from the final observed-depth approach | Maintain the observed-depth approach and preserve all four drafts |
| Notebook repeats substantial implementations in 19 code cells | Keep cell sources intact historically; provide one small package API |
| One multi-source loop initializes energy outside the per-source loop | Reset energy for every primary in the maintained implementation |
| Some diagonal directions are not normalized; early rotations are singular at an axial pole | Normalize flight directions and use a stable rotation basis |
| Notebook interpolates beyond the tabulated energy range | Reject source energies outside the table; deposit low-energy residuals explicitly |
| Original total coefficient and modeled partial channels are inconsistent | Rate is the sum of modeled partial coefficients |
| Some interrupted/escaped energies are not included in a complete ledger | Report deposited, escaped, unresolved and cutoff-subset energy |
| A 200 x 100 x 100 x 100 history array occupies about 1.6 GB before other arrays | Streaming batch statistics retain only a few voxel grids |
| Notebook figures refer to energy as dose and inconsistently describe source counts | Use MeV energy labels, per-primary normalization and explicit batch counts |
| Interactive volume output inflates the original notebook to 75 MB | Strip outputs and execution metadata; keep a hash of every code cell |

Preservation and maintenance are separate: historical bugs remain visible in the archive, whose cells are not run by CI. Only the small maintained notebook is executed. Reports and slides have not been converted into source code or used as evidence for implementation correctness.

Remaining scope limits include unvalidated coefficient provenance, simplified local deposition, omitted interaction channels, finite-bin location bias and small demonstration sample sizes. Tests establish numerical invariants and implementation behavior, not physical validation or statistical coverage.
