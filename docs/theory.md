# Physical model under investigation

## Intended source

The project investigates noise associated with an LED junction under reverse bias. A semiconductor under reverse bias can exhibit leakage, generation and recombination noise, shot noise, and, at suitable electric fields, breakdown processes such as impact ionisation or tunnelling.

The Arduino does not observe those microscopic processes directly. It observes the end of a chain containing the junction, resistors, amplifier, supply, environment, wiring, and ADC. Some mechanisms in that chain may have quantum origins, but that is weaker than demonstrating a lower bound on unpredictable quantum entropy at the digital output.

## ED-2 analogue chain

The ED-2 circuit biases its amplifier stages around a nominal 2.5 V reference so an LM358 on a single supply can amplify small variations without requiring a negative rail. Two noninverting stages provide voltage gain relative to that reference. Decoupling capacitors reduce rail and reference movement, while the series output resistor limits current into the Arduino A0 input.

The nominal noninverting gain of a stage is:

```text
G = 1 + Rf / Rg
```

This ideal expression is only a starting point. LM358 input common mode range, output swing, offset, bias currents, bandwidth, supply noise, source impedance, and possible saturation all affect the real result.

## ADC and least significant bit extraction

For an integer ADC code `x`, the firmware emits:

```text
bit = x & 1
```

This asks whether the sampled ADC code is even or odd. A smooth or periodic analogue waveform can still cross alternating converter codes and produce a nearly balanced bitstream. Weak LSB correlation therefore does not cancel or explain structure in the raw signal.

## Debiasing and conditioning

The included von Neumann rule examines pairs without overlap: `01` becomes `0`, `10` becomes `1`, and equal pairs are discarded. For independent samples with a fixed bias, it removes that bias. Correlated or changing sources can violate those assumptions.

Cryptographic conditioning can distribute existing entropy and reduce visible bias, but a deterministic function cannot create entropy. A safe output length must follow from a conservative lower bound for the raw source.

## Evidence needed for a stronger claim

A stronger case for a physical source requires:

1. a measured junction operating point and source model;
2. calibrated analogue gain and bandwidth;
3. experimental and control differences consistent with that model;
4. bounds on classical and externally controllable contributions;
5. repeatability across restarts and operating conditions; and
6. conservative entropy estimation before conditioning.

Until that chain exists, "QRNG investigation" describes the aim and "experimental physical entropy source" describes the demonstrated category.
