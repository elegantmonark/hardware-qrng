# ED-3 simplified breadboard prototype

ED-3 is a fresh breadboard build designed to correct the reference loading and
wiring ambiguity found during ED-2 bring-up. It uses one half of the LM358 to
buffer the midpoint reference and the other half as a single signal amplifier.

The design is documented in [`circuit.md`](circuit.md). It remains an unverified
prototype until the staged voltage checks, source controls and repeat captures
have been completed. A promising ADC trace alone will not be treated as proof of
entropy or quantum behaviour.

Photographs added under [`photos/`](photos/README.md) must show the exact circuit
revision associated with any published capture.
