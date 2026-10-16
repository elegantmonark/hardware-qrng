# ED-2 experiment plan

The purpose of the ED-2 campaign is to determine whether the intended junction source makes a repeatable contribution distinguishable from amplifier, ADC, supply, and environmental effects.

## 1. Record the configuration

Before each capture, record:

- demonstrator and circuit version;
- LED colour, marking, and part number if known;
- installed resistor and capacitor values;
- Arduino board, firmware revision, serial port, and baud rate;
- supply and ADC reference arrangement;
- nominal sampling interval and observed capture duration;
- temperature, lighting, power source, nearby equipment, and operator notes; and
- photographs that identify the physical configuration.

Use `hardware/ED-2/run-metadata-template.yaml` as the plain text checklist. The collector also creates a structured JSON sidecar.

## 2. Controlled captures

Collect the same target number of raw ADC samples for every condition and repeat the important conditions after independent power cycles.

| ID | Condition | Purpose |
|---|---|---|
| C0 | ADC input connected to the defined midpoint | ADC and digital baseline |
| C1 | Amplifier present with a resistor replacing the LED source | amplifier and resistor baseline |
| C2 | LED installed with no reverse bias | control with the junction present and bias off |
| C3 | LED below any measured operating threshold | comparison at low bias |
| E1 | LED at the selected documented operating point | main experiment |
| E2 | E1 repeated across independent restarts | repeatability and restart behaviour |

Use only safe operating conditions with a current limit. Do not raise the reverse bias without identifying the component and checking its rating and the microcontroller input protection.

## 3. Analyse every run

For each stream of raw samples, examine:

- distribution, time trace, clipping, and code occupancy;
- autocorrelation and power spectral density;
- stationarity over the capture;
- relationship between raw ADC code and extracted bits;
- bit proportion, runs, pair frequencies, and block variation;
- experimental versus control differences; and
- a conservative entropy assessment whose assumptions are explicit.

Retain failed and inconvenient results. Do not select only the run that looks best.

## 4. Evidence threshold

ED-2 may be described as a characterised physical entropy source prototype only when:

- its intended source operates in a measured and documented regime;
- experimental runs differ from controls in a repeatable, physically plausible way;
- a conservative lower entropy bound survives restart and non IID assessment;
- health test limits follow from that bound and observed failure modes; and
- any conditioned output rate does not exceed the supported input entropy rate.

A specifically quantum claim requires an additional physical argument that bounds the quantum contribution and competing predictable or classical contributions.
