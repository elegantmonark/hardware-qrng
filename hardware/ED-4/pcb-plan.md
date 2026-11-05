# ED 4 PCB plan

ED 4 is the custom routed PCB and printed enclosure stage. The current review
layout builds on the proposed ED 3 circuit with an MCP6002 and revised resistor
values. Fabrication release waits for breadboard measurements and physical fit.
An optional perfboard
version remains part of ED 3 and must repeat the checks after transfer.

## Interface revisions

- [ED4 A](pcb/ED4-A/README.md) is the Arduino version with a 5 V ADC interface.
  The routed layout is available for review; physical validation remains pending.
- ED4 E is the future ESP32 version. Its ADC range, power and connector choices
  need a separate review before creating that board.

## Mechanical target

Use the existing printed enclosure and preserve its board envelope.

| Constraint | Target or existing dimension |
| --- | --- |
| Nominal PCB outline | 89 by 52 mm |
| PCB thickness | 1.6 mm |
| Enclosure internal space | 105 by 68 by 34 mm |
| Board support height | 8 mm above the inner floor |
| Nominal clearance above the board | 24.4 mm before accounting for the lid lip and other obstructions |
| Existing cable opening | 26 by 12 mm |
| Retention | Existing support rails and corner guides |

The bare perfboard fit check confirms an initial envelope. Measure the actual
printed base and lid before fixing fabrication tolerances. Check underside
solder joints against the rails, components against the corner guides and lid,
and the complete connector and cable bend against the opening. Keep those
contact areas clear in the PCB layout. Do not assume mounting hole positions
that the printed enclosure does not provide.

## Circuit and acquisition

Use the simplest source and amplifier circuit supported by measurements. If
ED 3 is unstable or saturated, revise it and record the new circuit before
transferring it to PCB. Preserve raw samples and keep conditioning separate.

The microcontroller and ADC are acquisition hardware. Select the interface from
measurements of the same analogue test signal. An external ADC is an option if
the internal ADC obscures the signal or introduces unacceptable structure.

## Intended features

- Replaceable source connection and explicit source disconnected control.
- Buffered reference and gain selected from the validated circuit.
- Labelled source, reference, supply and ADC test points.
- Local supply decoupling and short analogue routing.
- Raw analogue output and a modular acquisition connector.
- Output protection checked against the selected ADC interface.
- Board edge, rail and corner guide clearances matching the printed enclosure.

## Before fabrication

- Measure reference and quiescent output across restarts.
- Calculate and check gain and usable bandwidth.
- Investigate clipping, oscillation, periodic interference and supply movement.
- Save source connected, source disconnected, covered source and resistor controls.
- Preserve repeat captures with metadata and hashes.
- Review the schematic, BOM, connector pinout and component polarity.
- Complete ERC, PCB review and DRC on the actual routed PCB.
- Check the board outline and populated assembly against the printed enclosure.

Assemble one PCB first and repeat the ED 3 electrical checks and captures before
describing ED 4 as validated. Use the current ED4 A routed project for the
fabrication review.
