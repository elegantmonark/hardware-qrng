# ED4 A Arduino prototype, revision B

This board carries the proposed ED 3 buffered reference and signal amplifier
inside the printed ED 4 enclosure. It uses through hole parts and an external
Arduino for power and data capture. The PCB is 89 by 52 mm and 1.6 mm thick.

The layout is a review prototype. The circuit has not yet been validated on
breadboard or PCB, and populated fit has not been checked in the actual print.
Check the circuit and enclosure fit before ordering a populated prototype.

## Open the project

Open [ED4_A_Arduino.kicad_pro](ED4_A_Arduino.kicad_pro) in KiCad 10. The
[schematic](ED4_A_Arduino.kicad_sch) and [PCB](ED4_A_Arduino.kicad_pcb) are
editable. The circuit values follow the current ED 3 proposal, with a local
10 uF supply capacitor and a source/control selector added for testing. This
revision uses an MCP6002 op amp and standard resistor values chosen for the
actual circuit rather than parts already on hand.

## Files for review

| File | Purpose |
| --- | --- |
| [Schematic PDF](drawings/ED4_A_schematic.pdf) | Connected circuit and pin labels |
| [Assembly PDF](drawings/ED4_A_assembly.pdf) | Component positions and enclosure rail strips |
| [BOM](BOM.csv) | Selected manufacturer parts and board footprints |

KiCad 10.0.1 reports 0 ERC violations, 0 DRC violations, 0 unconnected items
and 0 schematic parity issues. An independent pin contract check agreed with
the schematic and board. These checks do not replace bench validation.

The [ngspice signal path check](simulation/README.md) uses an injected test
signal and an approximate op amp model to check the intended reference and
amplifier response. It does not model the LED noise or validate the PCB in
hardware.

The BOM lists selected manufacturer parts. Confirm stock and the actual
enclosure fit before ordering. KiCad can export Gerbers and the drill file from
the PCB when the design is ready for manufacture. A successful layout check
does not establish that the LED produces useful entropy in this circuit.

## Arduino connector

J1 is a straight 2.54 mm pin header. Pad 1 is square and the signals are marked
on the board. Check pin numbers in KiCad before attaching the harness.

| J1 pin | Signal | Connection |
| --- | --- | --- |
| 1 | 5V | Arduino 5 V supply |
| 2 | 3V3 | Arduino 3.3 V source bias supply |
| 3 | GND | Common ground |
| 4 | A0 | Analogue output for a 5 V Arduino ADC interface |

Arduino AREF is left disconnected. Do not connect the output directly to an
ESP32 ADC. The future ED4 E revision will handle that interface separately.

## Source and control selector

JP1 is a three pin header with one removable shunt. Change its position with
power disconnected.

| Shunt | Connection | Use |
| --- | --- | --- |
| Pins 1 and 2 | LED source to the coupling capacitor | Source capture |
| Pins 2 and 3 | Coupling capacitor input to ground | Grounded AC input control |
| No shunt | Coupling capacitor input open | Open input diagnostic only |

The grounded control changes the input condition and does not isolate every
noise contribution. D1 remains biased through R3 in either shunt position.
Use separate covered LED, resistor control and restart captures as well.

D1 pad 1 is the cathode and pad 2 is the anode. Its reverse biased connection
follows the experimental ED 3 circuit. The listed Kingbright WP7113GD is a
physical part choice, not a validated entropy source. Its reverse behavior at
3.3 V must be measured before a functional claim can be made.

## Test points

| Point | Signal |
| --- | --- |
| TP1 | Raw midpoint reference |
| TP2 | Buffered midpoint reference |
| TP3 | LED source node |
| TP4 | Amplifier input |
| TP5 | Amplifier output before R7 |
| TP6 | Arduino A0 output after R7 |
| TP7 | Ground |

Probing the high impedance source node can load it. Record the probe and
measurement setup when interpreting the source signal.

## Mechanical review

The board outline matches the envelope used for the enclosure fit check.
The marked rail contact strips are on the drawing layer. Check solder joints
against the rails, components against the corner guides and lid, and the cable
bend against the 26 by 12 mm opening. No mounting holes have been assumed.

The [enclosure CAD](../../cad/README.md) preserves the existing printed geometry.
Two rule areas prohibit pads and vias where the printed rails touch the board.
The bottom copper layer has a filled ground return.

## Board mark

The front silkscreen carries a compact QRNG mark: a Q ring flowing into three
digital bit marks. It is an editable group named `QRNG logo` in the PCB editor.
The [SVG](../assets/qrng-logo.svg) is included for reuse in project documents.

## First bench checks

1. Check part values, U1 orientation, D1 polarity and capacitor polarity.
2. With the supply off, inspect for shorts and verify J1 pin order.
3. Power the board with current limiting and check the supply rails.
4. Measure TP1 and TP2. Confirm the reference remains stable under load.
5. Select the grounded AC control and check amplifier baseline and headroom.
6. Inspect for clipping or oscillation before connecting the Arduino ADC.
7. Compare source, control and restart captures using the original raw samples.

The nominal gain is 1 + 100k / 1k = 101. R4 is 100k and R7 is 1k. The
MCP6002 has much lower input bias than the earlier LM358 choice, which matters
for the high impedance input. Its offset still affects the baseline, so check
TP5 for clipping and stability. The [Microchip datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6001-1R-1U-2-4-1-MHz-Low-Power-Op-Amp-DS20001733L.pdf)
documents the PDIP pinout and electrical limits. The schematic uses the
KiCad LM2904 graphical symbol because its three units have the same pin map;
the fitted component is the MCP6002-I/P in the BOM and PCB.
