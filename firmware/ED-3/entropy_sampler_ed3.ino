// ED-3 entropy-source sampler for an Arduino Uno-compatible board.
// Author: Trishan Biswas
// Created: 17 October 2026
//
// PlatformIO CLI commands (run from the qrng_final directory):
//   pio run -e uno
//   pio run -e uno -t upload --upload-port COM3
//   pio device monitor -p COM3 -b 115200
//
// The amplified analogue signal enters through A0. Each serial row contains
// the raw 10-bit ADC reading and its least significant bit:
//
//     raw,bit

// Raw ADC behaviour must be evaluated before the extracted bit is interpreted.

constexpr uint8_t SIGNAL_PIN = A0;
constexpr unsigned long BAUD_RATE = 115200;
constexpr unsigned long SAMPLE_DELAY_US = 1000;
constexpr unsigned long ANALOG_SETTLE_MS = 1000;

void setup() {
  pinMode(SIGNAL_PIN, INPUT);
  Serial.begin(BAUD_RATE);
  delay(ANALOG_SETTLE_MS);
}

void loop() {
  const int raw = analogRead(SIGNAL_PIN);
  const int bit = raw & 1;

  Serial.print(raw);
  Serial.print(',');
  Serial.println(bit);

  delayMicroseconds(SAMPLE_DELAY_US);
}
