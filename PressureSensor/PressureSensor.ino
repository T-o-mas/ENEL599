const int pressurePin = A0;      // Analog pin connected to pressure transducer
float pressurePSI = 0.0;         // Calculated pressure in PSI

// Calibration values — based on sensor's spec
const float sensorMin = 0.5;     // Volts at 0 PSI
const float sensorMax = 4.5;     // Volts at max PSI (e.g., 200 PSI)
const float pressureMax = 200.0; // Max pressure rating of sensor

unsigned long previousMillis = 0;
unsigned long interval = 1000; // Log every 1000ms (1 second)

void setup() {
  Serial.begin(9600);
}
 
void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Read raw analog voltage
    int analogValue = analogRead(pressurePin);
    float voltage = (analogValue / 1023.0) * 5.0; //arduino analogue read is between 0-1023 due to 10-bit 2^10 or 1024 levels  
 
    // Convert voltage to pressure
    if (voltage >= sensorMin) {
      pressurePSI = ((voltage - sensorMin) / (sensorMax - sensorMin)) * pressureMax;
    } else {
      pressurePSI = 0.0;
    }

    // Print output with Arduino timestamp
    Serial.print("Timestamp (s): ");
    Serial.print(currentMillis / 1000.0, 3);  // 3 decimal places
    Serial.print(" | Voltage: ");
    Serial.print(voltage, 3);
    Serial.print(" V | Pressure: ");
    Serial.print(pressurePSI, 2);
    Serial.println(" PSI");
  }
}
