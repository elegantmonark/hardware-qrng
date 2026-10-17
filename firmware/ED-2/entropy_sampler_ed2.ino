// ED-2 entropy-source sampler for an Arduino Uno-compatible board.
// Author: Trishan Biswas
// Original sampler created: 14 April 2026
// ED-2 hardware revision: 16 October 2026
//
// PlatformIO CLI commands (run from the qrng_final directory):
//   pio run -e uno
//   pio run -e uno -t upload --upload-port COM3
//   pio device monitor -p COM3 -b 115200
//
// The amplified analogue signal enters through A0. Each line sent over serial
// contains the raw 10-bit ADC reading and its least significant bit:
//
//     raw,bit
//
// An external LED on D7 stays on while the sampler is running. It is not
// toggled for individual samples because that switching could couple into the
// nearby analogue circuit.

constexpr uint8_t SIGNAL_PIN = A0;
constexpr uint8_t STATUS_LED_PIN = 7;
constexpr unsigned long BAUD_RATE = 115200;
constexpr unsigned long SAMPLE_DELAY_US = 1000;
constexpr unsigned long ANALOG_SETTLE_MS = 1000;

void setup() {
  pinMode(SIGNAL_PIN, INPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);

  Serial.begin(BAUD_RATE);

  // Give VREF and the two amplifier stages time to settle after power-up.
  delay(ANALOG_SETTLE_MS);
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void loop() {
  const int raw = analogRead(SIGNAL_PIN);
  const int bit = raw & 1;

  Serial.print(raw);
  Serial.print(',');
  Serial.println(bit);

  // Serial transmission also contributes to the real interval between samples.
  delayMicroseconds(SAMPLE_DELAY_US);
}
