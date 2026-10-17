# ED-3 firmware

`entropy_sampler_ed3.ino` is the bring-up sampler for the simplified ED-3
breadboard. It reads A0 and emits `raw,bit` rows at 115200 baud.

The firmware deliberately avoids a switching status output near the analogue
circuit. The nominal one millisecond delay is not a measured sampling rate;
retained captures must use collector timestamps.
