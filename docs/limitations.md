# Limitations

## ED-1 source mechanism was not isolated

The ED-1 record does not include a measured LED current and voltage curve, oscilloscope trace, analogue spectrum, complete gain network record, or timestamps. The captured signal may include junction noise, amplifier noise, ADC and reference noise, supply ripple, interference, sampling interaction, or floating input behaviour.

## ED-2 exposed a reference-loading problem

ED-2 improved the circuit record and produced live ADC readings, but systematic probing showed its unbuffered midpoint reference collapsing under the Stage A reference branch. No validated ED-2 dataset is published. ED-3 is a proposed correction and must be tested independently.

## LSB extraction is not a source model

Taking an ADC least significant bit can hide visible structure, but it does not prove independence, unpredictability, or quantum origin. Deterministic interference can also toggle the LSB.

## ED-1 represents one run

The April capture has no associated restart campaign, temperature series, component identifiers, or measured timing for each sample. Its sample rate is inferred from firmware and serial behaviour rather than recorded at the sample level.

## Statistical testing is limited

The historical SP 800-22 output came from an external package, skipped two tests, used one sequence, and failed three reported tests. Passing other tests cannot identify the source mechanism or establish cryptographic security.

## The debiaser is educational

`software/extract.py` includes a von Neumann debiaser. Its classic guarantee assumes independent, identically distributed input pairs with stable bias. Those assumptions have not been established here. Its output is diagnostic, not production randomness.

## No adversarial or environmental qualification

The project has not been qualified against supply injection, electromagnetic coupling, temperature manipulation, optical injection, component substitution, or malicious interference with the data path.

## ED-4 enclosure is not validation

A perfboard assembly or printed enclosure may improve mechanical stability but can also alter coupling, temperature, grounding, and noise. ED-4 must repeat the relevant controls and measurements after assembly.
