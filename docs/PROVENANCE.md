# Source provenance and dates

Imported from the supplied folder `Computacional Statistics and Stocastic Processes` on 18 October 2026. The source folder remains untouched. All timestamps below are recorded in UTC; filesystem dates can reflect copying and are not signed historical records.

| Original file | Observed modification date | Published treatment |
| --- | --- | --- |
| `Projeto/Script.R` | 10 November 2023 | Verbatim R source |
| `Projeto/Script (1).R` | 13 November 2023 | Verbatim R source |
| `Projeto/Script 4 .R` | 15 November 2023 | Verbatim R source |
| `Projeto/Script_Final.R` | 15 November 2023 | Verbatim R source; seed `20231115` corroborates the period |
| `PEA/MC-PS.ipynb` | 23 September 2026 | Original code cells preserved; outputs and execution metadata removed |

The R study is reasonably described as **November 2023 coursework**. The notebook's original development date is **unknown**: its later timestamp and Python kernel metadata do not prove when the experiments were first written. New code and documentation belong to the **October 2026 maintained edition**, with genuine current Git commits rather than backdated commits.

[The machine-readable manifest](../historical/manifest.json) records exact source timestamps, original SHA-256 values for each R file, the full original notebook hash and a SHA-256 of each of its 19 code-cell sources. Notebook cleaning adds one warning markdown cell, drops outputs and execution metadata, and assigns stable cell IDs. Original cell source text is unchanged.

The original notebook contains 75,304,287 bytes, mostly stored output. Duplicate checkpoint and ZIP copies contain no additional code selected for this repository. R session history, IDE metadata, pre-rendered figures, the PDF report and PowerPoint slides are not published. Existing reports may involve collaborators and do not establish sole authorship. No individual contributions beyond the supplied project provenance have been inferred.

To repeat the source import against a private original folder:

```bash
python tools/import_sources.py "path/to/Computacional Statistics and Stocastic Processes"
python tools/audit_repository.py
```

The import reads only explicitly selected source files. It does not execute the original notebook. Git attributes disable line-ending conversion for historical R sources so their byte hashes remain stable across operating systems.
