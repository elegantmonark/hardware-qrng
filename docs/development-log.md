# Development log

This log records only development supported by surviving files, measurements, or a specific recollection. It intentionally separates working prototypes from claims that still need experimental support.

## December 2025: starting point

The project began as an attempt to build a physical random number source from basic components while learning semiconductor noise, analogue electronics, ADC sampling, Python data collection, and statistical validation.

The initial concept was to place an LED under reverse bias, amplify the resulting signal with an LM358P, sample it with an Arduino ADC, and extract the least significant bit of each sample.

## April 2026: ED-1 and the first complete pipeline

On 13 April, ED-1 produced the dataset now preserved at `data/ED-1/qrng_bits.csv`:

- 1,000,000 raw ADC readings and one extracted bit per reading;
- raw ADC range from 0 to 760 counts; and
- SHA-256 `84f9276dd0746fe06ef0f60ca0d3a2b98d365a43feaad63ccd2901a173a689d0`.

The first demonstrator worked as a complete system: hardware, Arduino capture, Python analysis, a software PRNG control, figures, and an exploratory NIST SP 800-22 run using an external package. This made ED-1 a useful prototype even though later analysis narrowed the claims that its data could support.

The early interpretation treated high Shannon entropy and several statistical test passes as confirmation that the bits were quantum. Those outputs cannot determine the physical origin of the signal. Classical noise, interference, ADC behaviour, or a mixture of mechanisms can produce similar apparent randomness.

## September 2026: ED-1 audit

The review before publication found four important points:

1. The saved raw ADC sequence has strong lag-1 correlation of approximately 0.906 and a dominant period of about 14.87 samples.
2. The LSB stream is close to balanced but not perfectly balanced.
3. The exploratory test run failed Frequency, Runs, and forward Cumulative Sums.
4. The recorded LED bias alone does not demonstrate that the junction operated in the assumed breakdown regime.

These findings did not make ED-1 useless. They converted it into a documented baseline and identified exactly what the next build needed to measure more carefully.

## October 2026: ED-2 improved breadboard build

ED-2 was assembled as an improved experimental demonstrator. The build documented in `circuit.md` adds:

- a defined 2.5 V reference;
- reference and supply decoupling;
- two LM358 amplification stages;
- explicit input bias resistors;
- a protected A0 connection;
- a separate D7 acquisition status LED; and
- a timestamped collector with metadata sidecars.

Successful ADC readings confirmed basic connectivity. ED-2 has not yet produced a published validation dataset, so no statistical or entropy improvement is claimed yet.

## ED-3: enclosure and permanent build direction

ED-3 is the next mechanical stage: transfer of the verified ED-2 circuit to perfboard, labelled external wiring, strain relief, and a 3D printed enclosure. The first printed shell is a fit and presentation prototype. Electrical validation must be repeated after any transfer to a permanent board.

## Current direction

The project is moving from "bits that look random" toward a reproducible investigation of a physical entropy source:

- preserve ED-1 as historical evidence;
- characterise ED-2 with controls and repeat captures;
- estimate entropy conservatively rather than from balance alone;
- add conditioning and health tests only after establishing a source model; and
- build ED-3 without confusing mechanical completion with validation.
