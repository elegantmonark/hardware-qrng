# ED-3 enclosure and perfboard plan

ED-3 is the planned mechanically stable implementation of the verified ED-2 topology. It is expected to use perfboard, labelled Arduino leads, strain relief, and a 3D printed enclosure.

The first printed shell is evidence of mechanical development only. It should be described as a prototype until the internal fit, ventilation, cable access, electrical isolation, serviceability, and complete assembled operation have been checked.

## Current enclosure design

The first parametric enclosure source is under [`cad/`](cad/README.md). It is sized for an 89 × 52 mm perfboard, provides 34 mm of internal height, and has one opening for the five wire Arduino harness: 5 V, 3.3 V, GND, A0 and D7.

The board rests on raised rails and is located by edge guides, so the design does not depend on unconfirmed positions for mounting holes. The lid uses a configurable locating lip held by friction for straightforward prototype printing.
