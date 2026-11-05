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

Successful ADC readings confirmed basic connectivity, but systematic probing found that the Stage A gain-reference branch pulled the unbuffered midpoint from approximately 2.5 V to approximately 1.3 V. ED-2 has not produced a published validation dataset, so no statistical or entropy improvement is claimed.

## October 2026: ED-3 simplified breadboard redesign

ED-3 replaces the two signal-gain stages with one buffered midpoint reference and one signal amplifier. The redesign is intended to prevent the gain network from collapsing the reference and to make staged fault isolation easier. Assembly and validation remain pending.

## ED 4: PCB and existing printed enclosure

The first enclosure base was printed in October 2026, and an unpopulated
89 by 52 mm perfboard fitted between its locating features. The photographs
and enclosure CAD preserve that initial fit investigation. The earlier unfinished KiCad
perfboard placement draft was later superseded by the routed ED4 A project.

On 5 November 2026, the stage plan was consolidated into four demonstrators.
ED 3 covers breadboard validation and optional perfboard transfer afterwards.
ED 4 covers the custom routed PCB and the existing printed enclosure. The
nominal PCB target is 89 by 52 mm and 1.6 mm thick, with final fit and connector
clearances to be checked against the actual print.

The PCB will use the simplest analogue topology that survives staged voltage
checks, control captures, restarts and signal analysis. Arduino, ESP32 and
external ADC acquisition remain options to evaluate. The processor acquires
and transports measurements and is not the physical entropy source.

The first PCB variant is ED4 A for an external Arduino with a 5 V ADC
interface. Its KiCad schematic and routed layout were prepared on 5 November.
Board revision B uses an MCP6002, a 100k and 1k gain network, and parts selected
for the BOM. The source jumper and local supply capacitor support bench checks.
KiCad ERC, DRC and schematic parity pass. Breadboard validation, owner review
and populated enclosure fit remain pending. ED4 E is a separate planned ESP32
version.

## Current direction

The project is moving from "bits that look random" toward a reproducible investigation of a physical entropy source:

- preserve ED-1 as historical evidence;
- assemble and characterise ED-3 with controls and repeat captures;
- estimate entropy conservatively rather than from balance alone;
- add conditioning and health tests only after establishing a source model;
- compare acquisition choices without assuming that a more powerful microcontroller provides a better ADC; and
- optionally transfer the validated ED 3 circuit to perfboard and check it again;
- build the ED 4 PCB to fit the enclosure already printed.
