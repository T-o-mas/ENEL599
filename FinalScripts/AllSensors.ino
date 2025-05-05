volatile int pulseCountInlet = 0; //Water Sensor Inlet (pin 2)
volatile int pulseCountOutlet = 0; //Water Sensor Outlet (pin 3)

float flowRateInlet = 0.0;
float flowRateOutlet = 0.0;

const float calibrationFactor = 50.25; //Pulses per liter

const int pressurePinInlet = A5; //Inlet pressure sensor
const int pressurePinOutlet = A0; //Outlet pressure sensor

float pressurePSIInlet = 0.0;
float pressurePSIOutlet = 0.0;

const float sensorMin = 0.5; //Voltage at 0 PSI
const float sensorMax = 4.5; //Voltage at max PSI
const float pressureMax = 200.0; //Max sensor PSI

//Timing
unsigned long previousMillis = 0;
const unsigned long interval = 100; // 100 ms = 0.1 second

void setup() {
  Serial.begin(9600);

  pinMode(2, INPUT_PULLUP); //Inlet flow
  pinMode(3, INPUT_PULLUP); //Outlet flow

  pinMode(pressurePinInlet, INPUT);
  pinMode(pressurePinOutlet, INPUT);

  //Flow sensor interrupts
  attachInterrupt(digitalPinToInterrupt(2), pulseCounterInlet, FALLING);
  attachInterrupt(digitalPinToInterrupt(3), pulseCounterOutlet, FALLING);

  previousMillis = millis();
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    noInterrupts(); //Disables interrupts
    int pulsesInlet = pulseCountInlet;
    int pulsesOutlet = pulseCountOutlet;
    pulseCountInlet = 0; //Reset counters 
    pulseCountOutlet = 0;
    interrupts(); //Enables interrupts

    //Flow Rates
    flowRateInlet = ((float)pulsesInlet / calibrationFactor) * 600.0;
    flowRateOutlet = ((float)pulsesOutlet / calibrationFactor) * 600.0;

    // Inlet Pressure
    int analogInlet = analogRead(pressurePinInlet);
    float voltageInlet = (analogInlet / 1023.0) * 5.0;
    if (voltageInlet >= sensorMin) {
      pressurePSIInlet = ((voltageInlet - sensorMin) / (sensorMax - sensorMin)) * pressureMax;
    } else {
      pressurePSIInlet = 0.0;
    }

    // Outlet Pressure
    int analogOutlet = analogRead(pressurePinOutlet);
    float voltageOutlet = (analogOutlet / 1023.0) * 5.0;
    if (voltageOutlet >= sensorMin) {
      pressurePSIOutlet = ((voltageOutlet - sensorMin) / (sensorMax - sensorMin)) * pressureMax;
    } else {
      pressurePSIOutlet = 0.0;
    }

    Serial.print(currentMillis);
    Serial.print(" ");
    Serial.print(flowRateInlet);
    Serial.print(" ");
    Serial.print(flowRateOutlet);
    Serial.print(" ");
    Serial.print(pressurePSIInlet, 2);
    Serial.print(" ");
    Serial.println(pressurePSIOutlet, 2);
  }
}

//Interrputs
void pulseCounterInlet() {
  pulseCountInlet++;
}

void pulseCounterOutlet() {
  pulseCountOutlet++;
}
