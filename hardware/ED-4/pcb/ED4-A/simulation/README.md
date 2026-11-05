# ED4 A signal path simulation

I used ngspice to check the analogue path in the revision B PCB before ordering it. The test puts a known 2 mV peak, 1 kHz signal into the coupling capacitor through JP1 pin 2. This lets me check the reference, gain and output range without treating the LED as a known noise source.

![Simulated signal at the Arduino input and frequency response](ed4a_signal_path_review.png)

| Check | Simulated result |
| --- | --- |
| Midpoint reference | 2.500 V raw and about 2.500 V buffered |
| Arduino A0 with the test signal | About 2.497 V average with a 0.201 V peak swing |
| Gain around 1 kHz | About 100 times |
| Low frequency corner | Around 16 Hz, set mainly by C4 and R4 |
| Upper corner | Around 10 kHz in this approximate model |

## Supply ripple with the input grounded

I also tested what happens when the 5 V supply has a 100 mV peak ripple at
100 Hz. The source input is grounded in this run, so there is no LED signal.
The [supply ripple netlist](ed4a_supply_ripple.cir) uses the same component
values and op amp approximation as the first check.

![Simulated supply ripple, reference and Arduino input](ed4a_supply_ripple.png)

After the initial settling period, the raw midpoint moves by about 1.75 mV
peak while A0 moves by about 160 mV peak. C1 filters the divider voltage, but
the gain stage can still turn reference movement into a much larger output
change. The size of this effect depends on the assumed ripple and model. I
need to measure the actual supply, reference and A0 with the input grounded
before interpreting any output variation as entropy.

## Input level and output headroom

The [headroom netlist](ed4a_input_headroom.cir) compares two separate copies
of the same gain stage. One has a 2 mV peak input and the other has a 40 mV
peak input. These are test levels, not measured LED amplitudes.

![Simulated Arduino input for small and large test signals](ed4a_input_headroom.png)

The 2 mV input gives an A0 range of about 2.295 to 2.697 V. The 40 mV input
drives the approximate output model to both limits, about 0.05 and 4.95 V.
This shows why the real source amplitude and ADC range need checking before
choosing the final gain.

The [netlist](ed4a_signal_path.cir) uses the PCB resistor and capacitor values and a simple one pole op amp approximation. It is **not** Microchip's MCP6002 model. The Arduino input is represented by a light load, and the LED noise, board parasitics and USB supply noise are not modelled. The plot shows how the intended amplifier path responds to an injected signal. It does not establish that the physical LED produces useful entropy or that the populated board will work as a QRNG.

To repeat the checks with a command line installation of ngspice, open this
folder in a terminal and run `ngspice ed4a_signal_path.cir`,
`ngspice ed4a_supply_ripple.cir` and `ngspice ed4a_input_headroom.cir`.
Each netlist writes its data to local text files. The figures here are saved
views of those outputs. The next meaningful check is a breadboard measurement
with the LED source and the grounded input control, followed by raw Arduino
captures.
