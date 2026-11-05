# ED4 A revision B JLCPCB files

These files are for ordering the revision B board with JLCPCB assembly on the top side:

| File | Use |
| --- | --- |
| [Gerber ZIP](ED4_A_RevB_Gerbers.zip) | Upload for PCB manufacture |
| [Assembly BOM](ED4_A_RevB_JLCPCB_BOM.csv) | Upload for component matching |
| [Placement file](ED4_A_RevB_JLCPCB_CPL.csv) | Upload for component positions and rotation |

The assembly BOM and placement file contain the same 11 components. JLCPCB fits
those components. Four positions are deliberately left out because I will fit
the parts myself after the board arrives:

| Position | Part to fit |
| --- | --- |
| R3 | 10 MOhm resistor |
| R4 and R6 | 100 kOhm resistors |
| D1 | Kingbright WP7113GD green LED |

The removable 2.54 mm shunt for JP1 is also separate. The [full design BOM](../BOM.csv)
lists every board part, including the four parts above. C1 and C3 in the JLCPCB
assembly BOM use Aishi 10 uF capacitors, and C2 uses a Murata 100 nF capacitor.
They have the same electrical values and lead spacing specified for the board.

Before paying, check that JLCPCB selected all 11 BOM entries and that every
rendered part lines up with its pads. In particular, check U1 pin 1, the polarity
of C1 and C3, and the orientation of J1 and JP1. D1 pad 1 is the cathode and is
marked K on the board. All components are on the top side.

The PCB layout has passed KiCad checks, but the circuit and fitted enclosure
still need physical testing. The LED noise source has not been validated.
