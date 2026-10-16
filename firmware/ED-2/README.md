# ED-2 firmware

`entropy_sampler_ed2.ino` is the sampler for the circuit documented in the root `circuit.md`.

It reads A0, emits `raw,bit` rows at 115200 baud, and uses D7 as a steady acquisition status indicator. The indicator does not display the extracted bitstream. The nominal delay is one millisecond, but the effective rate must be measured from capture timestamps rather than assumed from the delay alone.
