# ED-3 simplified circuit

## Status

This is the planned ED-3 breadboard topology. It has not yet passed bring-up or
validation. Component positions will be recorded after the circuit works as
intended, rather than inferred from the earlier breadboard.

## Design change

ED-2 used an unbuffered midpoint reference with two amplifier stages. During
bring-up, connecting the Stage A gain-reference branch pulled the nominal 2.5 V
reference down to approximately 1.3 V. ED-3 separates those functions:

1. LM358 amplifier A buffers the midpoint reference.
2. LM358 amplifier B provides one noninverting signal-gain stage.
3. The source signal is AC-coupled so its DC level does not set the amplifier
   operating point.

## Component register

| Reference | Value | Purpose |
|---|---:|---|
| R1 | 10 kOhm | Upper half of the midpoint divider |
| R2 | 10 kOhm | Lower half of the midpoint divider |
| RLED | 10 MOhm | Current limiting for the reverse-biased green LED source |
| RBIAS | 330 kOhm | Biases the signal input at buffered VREF |
| RF | 330 kOhm | Amplifier feedback resistor |
| RG | 4.4 kOhm | Gain resistor to buffered VREF |
| ROUT | 690 Ohm | Series protection between the LM358 output and A0 |
| CREF | 10 uF electrolytic | Stabilises the raw midpoint reference |
| CDEC | 100 nF | LM358 supply decoupling |
| CIN | 100 nF | AC-couples the source signal |

The nominal signal gain is:

```text
Gain = 1 + RF / RG
     = 1 + 330 kOhm / 4.4 kOhm
     = 76
```

## Electrical netlist

### Supply and raw reference

```text
Arduino 5 V ---- R1 10 kOhm ---- VREF_RAW ---- R2 10 kOhm ---- GND
                                      |
                                  CREF 10 uF
                                      |
                                     GND
```

CREF is polarised. Its positive leg connects to VREF_RAW and its marked
negative leg connects to ground.

### LM358 power and buffered reference

```text
Pin 8 = 5 V
Pin 4 = GND
CDEC  = 100 nF directly between pins 8 and 4

Pin 3 = VREF_RAW
Pin 2 = Pin 1
Pin 1 = VREF_BUFFERED
```

Pins 1 to 3 form a voltage follower. The gain network uses VREF_BUFFERED, not
the divider midpoint directly.

### Experimental LED source

```text
Arduino 3.3 V ---- RLED 10 MOhm ---- SOURCE_NODE ---- LED cathode
                                                        LED anode ---- GND

SOURCE_NODE ---- CIN 100 nF ---- SIGNAL_INPUT
```

The source LED is intentionally reverse biased and should remain dark. Its
identity and operating regime still require experimental verification; this
connection does not by itself prove a quantum source.

### Signal amplifier and ADC output

```text
SIGNAL_INPUT ---- pin 5
SIGNAL_INPUT ---- RBIAS 330 kOhm ---- VREF_BUFFERED

Pin 6 ---- RG 4.4 kOhm ---- VREF_BUFFERED
Pin 7 ---- RF 330 kOhm ---- Pin 6
Pin 7 ---- ROUT 690 Ohm ---- Arduino A0
```

Arduino AREF remains disconnected.

## Staged bring-up

1. Build and test only the 5 V and ground rails.
2. Build VREF_RAW and verify approximately half-scale ADC output.
3. Add the LM358 voltage follower and verify VREF_BUFFERED without loading the
   divider.
4. Add the signal amplifier without the LED source and confirm that its output
   sits near VREF_BUFFERED without clipping or oscillation.
5. Add the LED, RLED and CIN.
6. Capture short raw traces before extracting or interpreting the least
   significant bit.
7. Compare source-connected, source-disconnected, covered-LED and restart
   controls before retaining a dataset.

Disconnect USB power before changing any connection.
