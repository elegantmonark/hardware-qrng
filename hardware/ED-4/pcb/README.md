# ED 4 PCB revisions

| Revision | Interface | Status |
| --- | --- | --- |
| [ED4 A](ED4-A/README.md) | Arduino with a 5 V ADC interface | Routed review prototype; bench validation and physical fit pending |
| ED4 E | ESP32 | Planned separately; no ESP32 board has been designed or tested |

Both revisions target the existing enclosure with a nominal 89 by 52 mm PCB
outline and 1.6 mm thickness. ED4 E will require its own power, ADC input range
and connector review. The ED4 A output must not be assumed suitable for direct
connection to an ESP32 ADC.

The routed ED4 A project supersedes the earlier perfboard placement draft.
The enclosure and its physical fit photographs remain under the ED 4 hardware record.
