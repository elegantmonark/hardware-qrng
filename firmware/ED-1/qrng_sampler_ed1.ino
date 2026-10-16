// ED-1 archived sampler -- Arduino Uno
// Author: Trishan Biswas
// Created: 14 April 2026
//
// This file records the firmware used by the first demonstrator. The comments
// describe the original experimental interpretation and should be read with
// firmware/ED-1/README.md and the limitations documented for the ED-1 data.

#define LED_PIN 13
#define BUZZER_PIN 12

void buzz(int duration_ms) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration_ms);
    digitalWrite(BUZZER_PIN, LOW);
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    buzz(200);
}

void loop() {
    int raw = analogRead(A0);
    int lsb = raw & 1;
    digitalWrite(LED_PIN, lsb);
    Serial.print(raw);
    Serial.print(",");
    Serial.println(lsb);
    delay(1);
}
