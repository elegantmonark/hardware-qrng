# Safety

The documented Arduino prototype is low voltage, but reverse bias experiments and permanent assembly still require normal electronics safety practice.

- Power down before rewiring the breadboard or perfboard.
- Check IC orientation, capacitor polarity, resistor values, rail polarity, and continuity before applying power.
- Use a supply with a current limit when characterising a junction or changing its bias.
- Keep the Arduino analogue input within its rated range and retain explicit input protection.
- Do not connect independently powered analogue equipment to computer USB ground without checking the grounding arrangement.
- Stop immediately if a component heats, smells, discolours, or behaves unexpectedly.
- Keep exposed conductors from shorting against enclosure hardware.
- Treat the printed enclosure as a mechanical prototype until clearances, strain relief, ventilation, and service access are checked.

This repository does not replace component datasheets, supervision, or laboratory safety procedures.
