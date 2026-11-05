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

## Reading the figure

The time trace and ADC histogram describe the analogue path *before* the final
bit is selected. The trace moves in a structured way, and the histogram shows
which ADC codes were actually visited. A broad histogram alone would not tell
me whether each new reading was hard to predict from the previous one.

The Hann windowed spectrum has a prominent component at 0.067256 cycles per
sample, or about 14.87 samples per cycle. This could reflect the source,
power or sampling process; the figure does not identify which. Without saved
sample timing I cannot honestly turn it into hertz or label it as mains noise.

The autocorrelation gives the clearest warning. Raw lag 1 correlation of
0.9057 means adjacent ADC readings tend to resemble one another. The extracted
least significant bits have lag 1 correlation of 0.00119, which is much
smaller. That is useful, but it tests only one lag and does not show that the
bits are independent across all time scales or operating conditions.

The block balance plot checks whether the fraction of ones stays similar
through the capture. Overall, 497,767 of the million bits are ones. The
reported 0.9999856 bits of marginal Shannon entropy follows from that overall
balance. It is not an entropy rate: a sequence can have almost perfect balance
and still be partly predictable. The separate [validation notes](../../../docs/validation.md)
explain why a conservative source estimate needs controls and repeat runs.

See the [MATLAB guide](../../../software/matlab/README.md) for the source and
instructions to repeat the analysis.
