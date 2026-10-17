# Validation notes

## Scope of the preserved result

The published April 2026 file is one continuous ED-1 capture of ADC values and their least significant bits. It provides evidence about that run only. It does not establish behaviour across different units, restart behaviour, temperature stability, quantum dominance, or resistance to an active attacker.

ED-2 has not produced a published validation dataset. ED-3 is awaiting assembly and staged bring-up.

## ED-1 descriptive results

| Statistic | Value |
|---|---:|
| Samples | 1,000,000 |
| Ones | 497,767 |
| Zeros | 502,233 |
| Proportion of ones | 0.497767 |
| Binary Shannon entropy | 0.9999856126 bit/symbol |
| Most common value estimate | 0.9935712686 bit/symbol |
| Raw ADC minimum / maximum | 0 / 760 |
| Raw ADC mean / standard deviation | 315.746 / 182.339 |
| Raw ADC lag-1 correlation | 0.905704 |
| Dominant raw spectral component | 0.067256 cycles/sample |
| Corresponding period | 14.8686 samples |
| LSB lag-1 correlation | 0.001193 |

The most common value result is only `-log2(max(p0, p1))`. It does not account for temporal dependence, behaviour that changes with time, or adversarial knowledge and is not a NIST SP 800-90B minimum entropy result.

The ED-1 time trace, autocorrelation, and spectrum show a large roughly periodic component in the raw ADC sequence. Because the file has no timestamps, cycles per sample cannot be converted into a defensible frequency in hertz. The extracted LSBs hide most of the visible raw code structure; they do not explain or remove its physical cause.

## ED-1 exploratory SP 800-22 run

The files under `results/ED-1/nist/` came from the external `nist80022` Python package and one sequence containing one million bits.

| Test | Historical result |
|---|---|
| Frequency (Monobit) | Fail, p = 0.000008 |
| Block Frequency | Pass, p = 0.483517 |
| Runs | Fail, p reported as 0 |
| Longest Run | Skipped by the script |
| Binary Matrix Rank | Pass, p = 0.333555 |
| FFT Spectral | Pass, p = 0.358795 |
| Nonoverlapping Template | Pass, p = 0.354295 |
| Overlapping Template | Skipped by the script |
| Linear Complexity | Pass, p = 0.905349 |
| Universal | Pass, p = 0.956922 |
| Serial | Pass, p = 0.972381 and 0.707313 |
| Approximate Entropy | Pass, p = 0.449507 |
| Cumulative Sums, forward | Fail, p = 0.000010 |

The old summary counted individual Random Excursions states as separate passes and reported "35 passes." That is not a meaningful score for the project. Some tests return multiple p values, have prerequisites, or require many independent sequences to interpret pass proportions and the uniformity of p values.

Statistical tests cannot certify a generator for a security application or identify the physical origin of its entropy.

## ED-3 validation sequence

1. Verify and photograph the exact circuit as built.
2. Record source, supply, gain, ADC reference, firmware, sampling, and environment.
3. Collect controls and experimental runs from `experiment-plan.md`.
4. Analyse raw signals before examining or conditioning output bits.
5. Repeat important runs after independent power cycles.
6. Choose an IID or non IID model based on evidence.
7. Estimate entropy conservatively and define health test limits.
8. Condition only within the supported entropy rate.
9. Repeat relevant validation after the ED-4 perfboard transfer.

## Primary references

- NIST SP 800-90B, *Recommendation for the Entropy Sources Used for Random Bit Generation*: https://doi.org/10.6028/NIST.SP.800-90B
- NIST SP 800-22 Rev. 1a, *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*: https://doi.org/10.6028/NIST.SP.800-22r1a
- NIST, *Decision to Revise NIST SP 800-22 Rev. 1a*: https://www.nist.gov/news-events/news/2022/04/decision-revise-nist-sp-800-22-rev-1a
