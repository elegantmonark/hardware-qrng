# Engineering roadmap

This is a living checklist rather than a deadline schedule. A task is complete only when its evidence is recorded, not when a promising result appears once.

## 1. Preserve ED-1

- [x] Preserve the original dataset containing one million samples and the PRNG control.
- [x] Preserve integrity hashes, figures, audit results, and exploratory NIST outputs.
- [x] Archive the ED-1 Arduino sampler separately from current firmware.
- [x] Add selected, captioned ED-1 hardware photographs.

## 2. Complete the ED-2 hardware record

- [x] Record the complete breadboard placement and electrical netlist in `circuit.md`.
- [x] Separate the acquisition status LED from the extracted bitstream.
- [x] Add a reusable template for run metadata.
- [x] Add selected, captioned ED-2 photographs.
- [ ] Add the hand drawn ED-2 circuit development sketch and a short caption.
- [ ] Confirm and record every installed component value before validation captures.
- [ ] Create a conventional schematic from the verified circuit as built.

## 3. Identify the dominant analogue signal

- [ ] Capture an ADC baseline at a defined midpoint.
- [ ] Capture controls using the amplifier and a resistor source.
- [ ] Compare conditions with LED bias off, low bias, and the intended experimental bias.
- [ ] Compare USB power with a suitable independent supply with low noise.
- [ ] Test ambient light and covered junction conditions.
- [ ] Measure waveform and spectrum directly if suitable instrumentation is available.

## 4. Verify the source operating regime

- [ ] Identify the LED or select a documented replacement.
- [ ] Measure its reverse current and voltage behaviour with safe current limiting.
- [ ] Choose and document an operating point.
- [ ] Establish whether signal changes follow the physical model.

## 5. Characterise the ED-2 analogue path

- [ ] Check LM358 input common mode range, output swing, offset, and the effects of bias current.
- [ ] Calculate and measure gain and bandwidth.
- [ ] Check for clipping, saturation, oscillation, and rail/reference movement.
- [ ] Record any change from the current topology as a new circuit revision.

## 6. Collect the ED-2 campaign

- [x] Add timestamped filenames and automatic JSON metadata to the collector.
- [ ] Collect all controls specified in `experiment-plan.md`.
- [ ] Collect the main source condition across independent power cycles.
- [ ] Retain failed and inconvenient captures.
- [ ] Preserve hashes and a run manifest for selected published data.

## 7. Establish a conservative entropy bound

- [ ] Determine whether an IID model is defensible or use a non IID assessment.
- [ ] Perform restart testing and examine variation across conditions.
- [ ] Run suitable estimators based on NIST SP 800-90B on raw source samples.
- [ ] Choose the most conservative supported lower bound.
- [ ] Derive a maximum conditioned output rate from that bound.

## 8. Design conditioning and health tests

- [x] Retain an explicitly educational von Neumann debiaser.
- [ ] Set limits for repetition count and adaptive proportion tests from the source model.
- [ ] Define behaviour for startup, continuous, and requested tests.
- [ ] Stop or quarantine output after a detected source failure.
- [ ] Select a conditioner only after the supported input entropy is known.

## 9. Build ED-3

- [ ] Use the printed shell as a fit prototype and record changes.
- [ ] Add CAD renders and photographs of the printed ED-3 shell.
- [ ] Transfer the verified ED-2 topology to perfboard.
- [ ] Keep analogue wiring short and separated from digital wiring.
- [ ] Add labelled leads, test points, strain relief, and safe clearances.
- [ ] Photograph and document the completed ED-3 assembly.
- [ ] Repeat key controls after the transfer.

## 10. Characterise enclosure effects

- [ ] Test optical sensitivity before deciding how fully to block light.
- [ ] Check temperature drift and ventilation requirements.
- [ ] Compare interference with the circuit exposed and provisionally enclosed.
- [ ] Record that a plastic enclosure does not provide meaningful EMI shielding by itself.
- [ ] Finalise CAD only after board dimensions and connector locations are stable.

## Definition of completion

The project can support a stronger hardware QRNG claim only when the physical source, controls, entropy bound, conditioning, restart behaviour, and health monitoring form a consistent evidence chain. Until then, each demonstrator remains valuable engineering progress without requiring an unsupported final label.
