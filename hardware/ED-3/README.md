# ED 3 breadboard and optional perfboard prototype

ED-3 is a fresh breadboard build designed to correct the reference loading and
wiring ambiguity found during ED-2 bring-up. It uses one half of the LM358 to
buffer the midpoint reference and the other half as a single signal amplifier.

The design is documented in [`circuit.md`](circuit.md). It remains an unverified
prototype until the staged voltage checks, source controls and repeat captures
have been completed. A promising ADC trace alone will not be treated as proof of
entropy or quantum behaviour.

Photographs added under [`photos/`](photos/README.md) must show the exact circuit
revision associated with any published capture.

## Optional perfboard transfer

Once the breadboard passes its staged electrical checks and control captures,
the verified circuit may be transferred to perfboard as part of ED 3. Record
the wiring and component values, then repeat the reference, amplifier and
capture checks after transfer. Perfboard assembly is optional and has not begun.

The later custom PCB and printed enclosure belong to [ED 4](../ED-4/README.md).
