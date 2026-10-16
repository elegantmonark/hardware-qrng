# ED-1 firmware

`qrng_sampler_ed1.ino` is retained to document the first demonstrator and the acquisition path associated with the preserved ED-1 dataset.

The firmware samples A0, extracts the ADC least significant bit, transmits `raw,bit` at 115200 baud, drives the D13 LED built into the board from the extracted bit, and uses D12 for a startup buzzer.

Its presence is historical evidence, not proof that every captured least significant bit had a quantum origin. The raw ED-1 signal contained strong correlation and periodic structure, so the dataset must be interpreted with the repository's stated limitations.
