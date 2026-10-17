# ED-2 LED entropy source circuit

> [!IMPORTANT]
> This file preserves the ED-2 development circuit. During October 2026
> bring-up, its Stage A gain-reference branch pulled the unbuffered midpoint
> reference from approximately 2.5 V to approximately 1.3 V. The current ED-3
> redesign is documented in [`hardware/ED-3/circuit.md`](hardware/ED-3/circuit.md).

## Purpose

This circuit captures fluctuations from a green LED under reverse bias through a
two stage LM358 analogue amplifier. An Arduino Uno compatible board samples the
amplified signal through analogue input A0.

The present circuit is an experimental physical entropy source. Further source
characterisation and control measurements are required before attributing the
recorded fluctuations to a particular physical mechanism or using the output
for applications where security matters.

## Breadboard convention

This layout assumes a conventional solderless breadboard:

- holes `A-E` are connected horizontally within each numbered row;
- holes `F-J` are connected horizontally within each numbered row;
- the centre trench separates columns `E` and `F`;
- row numbers increase away from the observer; and
- the upper rail sections beside rows 5-40 are used.

### Power rail assignments

| Rail | Connection |
|---|---|
| Left red | Arduino 5 V |
| Left blue | Arduino GND |
| Right red | Arduino 3.3 V |
| Right blue | 2.5 V reference, labelled `VREF` |

The right blue rail is not ground. It must be labelled `VREF` before wiring.
Arduino AREF remains disconnected.

## LM358 placement and pin map

Place the LM358 across the centre trench with its notch facing the smaller row
numbers.

| LM358 pin | Breadboard hole | Function |
|---:|---|---|
| 1 | E25 | Stage A output |
| 2 | E26 | Stage A inverting input |
| 3 | E27 | Stage A noninverting input |
| 4 | E28 | Ground |
| 5 | F28 | Stage B noninverting input |
| 6 | F27 | Stage B inverting input |
| 7 | F26 | Final amplifier output |
| 8 | F25 | 5 V supply |

Pin numbering from above:

```text
             notch
          +---------+
OUT A   1 |         | 8   +5 V
IN- A   2 |  LM358  | 7   OUT B
IN+ A   3 |         | 6   IN- B
GND     4 |         | 5   IN+ B
          +---------+
```

## Resistor register

| Reference | Value | Placement | Purpose |
|---|---:|---|---|
| R1 | 10 kOhm | Left 5 V rail at row 10 to A10 | Upper half of VREF divider |
| R2 | 10 kOhm | B10 to B14 | Lower half of VREF divider |
| RLED | 10 MOhm | Right 3.3 V rail at row 16 to J16 | Reverse bias feed for the source LED |
| RBIAS-A | 100 kOhm | J18 to right VREF rail at row 18 | Biases Stage A noninverting input |
| RF-A | 220 kOhm | A25 to A26 | Stage A feedback resistor |
| RG-A | 4.7 kOhm | B26 to B22 | Stage A gain resistor to VREF |
| RBIAS-B | 100 kOhm | J28 to right VREF rail at row 28 | Biases Stage B noninverting input |
| RF-B | 47 kOhm | J26 to J27 | Stage B feedback resistor |
| RG-B | 10 kOhm | H27 to right VREF rail at row 27 | Stage B gain resistor to VREF |
| ROUT | 1 kOhm | H26 to H30 | Series protection between amplifier and A0 |
| RSTATUS | 1 kOhm | B35 to B38 | Current limiting for the collection status LED |

Stage A has a nominal noninverting gain of:

```text
Gain A = 1 + RF-A / RG-A
       = 1 + 220 kOhm / 4.7 kOhm
       = approximately 47.8
```

Stage B has a nominal noninverting gain of:

```text
Gain B = 1 + RF-B / RG-B
       = 1 + 47 kOhm / 10 kOhm
       = 5.7
```

The nominal combined gain is approximately 273. Actual usable gain is
limited by the LM358 supply voltage, bandwidth, output swing and the amplitude
of the input signal.

## Capacitor register

| Reference | Value | Placement | Purpose |
|---|---:|---|---|
| CREF | 10 uF electrolytic | Positive at D10; leg marked with the negative stripe at D14 | Stabilises VREF |
| C1 | 100 nF | G16 to G18 | AC-couples the LED source into Stage A |
| C2 | 100 nF | C25 to C23 | AC-couples Stage A into Stage B |
| CDEC | 100 nF | G25 to D28 | LM358 supply decoupling |

The 100 nF capacitors are not polarised. CREF is polarised and must be installed
with its positive leg toward VREF and its marked negative leg toward ground.

## Complete assembly

Disconnect USB and all external power before changing the circuit.

### 1. Power rails

1. Connect Arduino 5 V to the left red rail beside row 5.
2. Connect Arduino GND to the left blue rail beside row 5.
3. Connect Arduino 3.3 V to the right red rail beside row 5.
4. Leave the right blue VREF rail isolated from ground.

Only the upper rail sections are required. If a different breadboard or lower
rail section is used, test rail continuity before relying on it.

### 2. VREF generator

1. Install R1 from the left 5 V rail at row 10 to A10.
2. Install R2 from B10 to B14.
3. Connect A14 to the left GND rail at row 14.
4. Install CREF with its positive leg at D10 and its marked negative leg at D14.
5. Connect E10 to the right blue VREF rail at row 10.

The connected holes A10-E10 form the local 2.5 V reference node.

### 3. LM358 power and decoupling

1. Place the LM358 in E25-E28 and F25-F28 using the pin map above.
2. Connect J25 to the left 5 V rail at row 25. This powers pin 8 through row 25.
3. Connect A28 to the left GND rail at row 28. This grounds pin 4 through row 28.
4. Install CDEC between G25 and D28.

### 4. LED source under reverse bias

1. Install RLED from the right 3.3 V rail at row 16 to J16.
2. Insert the source LED cathode, identified by its shorter leg or flat package
   side, at H16.
3. Insert the source LED anode, normally the longer leg, at H17.
4. Connect F17 to the left GND rail at row 17.

The source LED is under reverse bias and should remain dark.

### 5. Stage A input and amplifier

1. Install C1 from G16 to G18.
2. Connect F18 to D27, which reaches LM358 pin 3 through row 27.
3. Install RBIAS-A from J18 to the right VREF rail at row 18.
4. Install RF-A from A25 to A26. It may be mounted vertically.
5. Install RG-A from B26 to B22.
6. Connect E22 to the right VREF rail at row 22.

### 6. Stage B input and amplifier

1. Install C2 from C25 to C23.
2. Connect E23 to I28, which reaches LM358 pin 5 through row 28.
3. Install RBIAS-B from J28 to the right VREF rail at row 28.
4. Install RF-B from J26 to J27. It may be mounted vertically.
5. Install RG-B from H27 to the right VREF rail at row 27.

### 7. Arduino analogue output

1. Install ROUT from H26 to H30.
2. Connect J30 to Arduino A0 only after the voltage checks below pass.
3. Leave Arduino AREF disconnected so the normal board reference is retained.

### 8. Collection status indicator

The status indicator is electrically separate from the analogue source.

1. Connect Arduino digital pin D7 to A35.
2. Install RSTATUS from B35 to B38.
3. Insert the status LED anode at D38.
4. Insert the status LED cathode at D39.
5. Connect A39 to the left GND rail at row 39.

The indicator remains steadily on while the sampler firmware is running. It
does not toggle for every ADC sample because rapid digital switching can couple
into the analogue measurement.

## Electrical checks

Perform these checks with a multimeter before connecting Arduino A0.

| Test point | Expected DC voltage relative to GND |
|---|---:|
| Left red rail | Approximately 5 V |
| Right red rail | Approximately 3.3 V |
| Right blue VREF rail | 2.4-2.6 V |
| LM358 pin 8 / row F25 | Approximately 5 V |
| LM358 pin 4 / row E28 | 0 V |
| LED source node / row 16 | Between 0 V and 3.3 V; typically near 3.3 V |
| LM358 pin 3 / row E27 | Approximately VREF |
| LM358 pin 2 / row E26 | Approximately VREF |
| LM358 pin 1 / row E25 | Near VREF; not fixed against a supply rail |
| LM358 pin 5 / row F28 | Approximately VREF |
| LM358 pin 6 / row F27 | Approximately VREF |
| LM358 pin 7 / row F26 | Near VREF; not fixed against a supply rail |
| Protected output / row 30 | Safely within the Arduino 0-5 V input range |

If either amplifier output remains near a supply rail, disconnect power and
inspect the IC orientation, VREF connections, feedback paths and resistor
values before connecting A0.

## Arduino connections summary

| Arduino pin | Circuit connection |
|---|---|
| 5 V | Left red rail |
| 3.3 V | Right red rail |
| GND | Left blue rail |
| A0 | J30 after ROUT |
| D7 | A35 for status indication |
| AREF | Not connected |

## Initial acquisition procedure

1. Verify every DC checkpoint.
2. Connect J30 to Arduino A0.
3. Keep the status output constant throughout each sample interval.
4. Record both the raw 10-bit ADC value and any derived bit.
5. Save every capture under a new dated filename rather than overwriting an
   earlier dataset.
6. Record the circuit revision, sample count, supply voltages and relevant
   measurement conditions alongside the capture.

The circuit should be validated on the breadboard before it is transferred to
perfboard or enclosed.
