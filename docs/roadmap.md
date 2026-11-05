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

## 5. Build and characterise the ED-3 analogue path

- [ ] Build and verify the raw midpoint reference.
- [ ] Add the LM358 voltage follower and confirm that the buffered reference remains stable under load.
- [ ] Add the single signal amplifier and verify its baseline before connecting the LED source.
- [ ] Check LM358 input common mode range, output swing, offset, and the effects of bias current.
- [ ] Calculate and measure gain and bandwidth.
- [ ] Check for clipping, saturation, oscillation, and rail/reference movement.
- [ ] Record any change from the current topology as a new circuit revision.
- [ ] If useful, transfer the validated circuit to perfboard as part of ED 3,
  document its wiring and repeat the electrical checks and control captures.

## 6. Collect the ED-3 campaign

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

## 9. Confirm the ED 4 enclosure envelope

- [x] Use the printed shell as a fit prototype and confirm the bare perfboard envelope.
- [x] Add photographs of the printed ED-4 shell and initial perfboard fit check.
- [x] Set the nominal PCB target to the existing 89 by 52 mm board envelope.
- [ ] Measure the printed base and lid to establish final PCB edge tolerances,
  support clearances, component height and connector access.

## 10. Design and build the ED 4 PCB

- [x] Prepare the ED4 A Arduino schematic, routed prototype and assembly drawings.
- [x] Pass ERC, DRC, schematic parity and an independent circuit pin contract check.
- [ ] Complete Trishan's layout review and add his chosen screenshots.
- [ ] Design ED4 E for ESP32 after reviewing its power and ADC interface.
- [ ] Reduce or replace ED-3 if bench measurements show a simpler topology is more defensible.
- [ ] Freeze the analogue topology only after reference, gain, clipping, bandwidth and control captures pass.
- [ ] Compare the Arduino ADC, ESP32 ADC and a suitable external ADC using the same analogue test signal.
- [ ] Keep the microcontroller separate from the physical-source claim; it is acquisition and transport hardware only.
- [ ] Include labelled test points, source/control selection, decoupling and short analogue routing.
- [ ] Use a nominal 89 by 52 mm outline and 1.6 mm thickness, with rail and
  corner guide keepouts based on the printed enclosure.
- [ ] Run ERC and DRC and complete a schematic, PCB and BOM review before ordering.
- [ ] Assemble one board first and repeat the breadboard controls before treating the PCB as validated.

## 11. Characterise enclosure effects

- [ ] Test optical sensitivity before deciding how fully to block light.
- [ ] Check temperature drift and ventilation requirements.
- [ ] Compare interference with the circuit exposed and provisionally enclosed.
- [ ] Record that a plastic enclosure does not provide meaningful EMI shielding by itself.
- [ ] Keep the current printed enclosure and check the final PCB assembly against it.
- [ ] Record any enclosure adjustment needed for the selected connector or populated board.

## Definition of completion

The project can support a stronger hardware QRNG claim only when the physical source, controls, entropy bound, conditioning, restart behaviour, and health monitoring form a consistent evidence chain. Until then, each demonstrator remains valuable engineering progress without requiring an unsupported final label.
