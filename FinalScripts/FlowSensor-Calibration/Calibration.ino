volatile int pulseCount = 0;

const byte inletFlowSensorPin = 3;
unsigned long lastPrintTime = 0;
const unsigned long printInterval = 500; // 0.5 seconds

void setup() {
  Serial.begin(9600);
  pinMode(inletFlowSensorPin, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(inletFlowSensorPin), countPulse, FALLING);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastPrintTime >= printInterval) {
    lastPrintTime = currentMillis;

    noInterrupts();
    int currentCount = pulseCount;
    interrupts();

    Serial.print(currentMillis);
    Serial.print(" ");
    Serial.println(currentCount);

    pulseCount = 0;
  }
}

void countPulse() {
  pulseCount++;
}
