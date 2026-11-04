# MATLAB results from the April capture

These are the original exports from a MATLAB R2026b Update 1 run using the
preserved April Arduino capture. They were reviewed on 5 November 2026.

| File | Contents |
| --- | --- |
| [Diagnostics PNG](../../../figures/ED-1/matlab_diagnostics.png) | Six plots of the signal, spectrum, correlations and bit balance |
| [Editable figure](ed1_matlab_diagnostics.fig) | The MATLAB figure, about 9 MB |
| [Report](ed1_matlab_report.json) | Statistics, runtime version and reference check result |
| [Correlation CSV](autocorrelation.csv) | Raw ADC and extracted bit correlations at lags 0 through 100 |
| [Summary](summary.txt) | The printed analysis summary |

The report matches the preserved Python audit and a fresh analysis of the source
CSV. All 101 correlation rows match the recomputed values within floating point
precision. The original exports have been copied without changes.

The report records `generated_at` as `20261104T125937`. Its timezone was not
recorded. The MATLAB Drive input path is retained as exported.

Input: [original capture](../../../data/ED-1/qrng_bits.csv).
SHA256: `84f9276dd0746fe06ef0f60ca0d3a2b98d365a43feaad63ccd2901a173a689d0`.

The extracted bits are nearly balanced, with a proportion of ones of 0.497767.
The raw ADC sequence has a lag 1 correlation of 0.9057 and a dominant component
at 0.067256 cycles per sample. The CSV does not establish a sampling rate.
These diagnostics describe the capture and do not establish quantum origin or
cryptographic security.

See the [MATLAB guide](../../../software/matlab/README.md) for the source and
instructions to repeat the analysis.
