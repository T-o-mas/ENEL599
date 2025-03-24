volatile int pulseCount = 0;         // Counts the pulses from the flow sensor
unsigned long previousMillis = 0;      // Tracks the last time interval
unsigned long secondsCounter = 0;      // Counts the seconds elapsed since start
float flowRate = 0.0;                  // Flow rate in liters per minute
float totalLiters = 0.0;               // Cumulative water volume in liters
const float calibrationFactor = 7.5;   // Calibration factor (pulses per liter, typical for YF-S201)
//The calibration factor is used to convert the raw pulse count from the flow sensor into a meaningful measurement of water volume. 
//For instance, if your flow meter produces 7.5 pulses for every liter of water that passes through it

void setup() {
  Serial.begin(9600); //sets serial communication
  // Configure digital pin 2 for the flow sensor input
  pinMode(2, INPUT_PULLUP); // Sets pin 2 to pull up resistor
  attachInterrupt(digitalPinToInterrupt(2), pulseCounter, FALLING);   // Set up an interrupt on digital pin 2 for the falling edge
  previousMillis = millis(); //captures current time in milliseconds
}

void loop() {
  unsigned long currentMillis = millis();
  // Check if 1 second (1000 milliseconds) has passed
  if (currentMillis - previousMillis >= 1000) {
    secondsCounter++; // Increment the timestamp counter (each unit represents 1 second)

    // Safely copy and reset the pulse count
    noInterrupts();            // Disable interrupts temporarily
    int pulses = pulseCount;   // Copy the pulse count for this second
    pulseCount = 0;            // Reset the global pulse count for the next interval
    interrupts();              // Re-enable interrupts

    // Calculate flow rate in liters per minute:
    // (pulses per second / calibrationFactor) gives liters per second, then multiply by 60.
    flowRate = ((float)pulses / calibrationFactor) * 60.0;
    
    // Calculate water volume for this interval (in liters)
    // Since the measurement is over 1 second, the volume is flowRate/60.
    totalLiters += (flowRate / 60.0);

    // Print the timestamp (in seconds), flow rate, and total water volume
    Serial.print("Timestamp (s): ");
    Serial.print(secondsCounter);
    Serial.print(" | Flow rate (L/min): ");
    Serial.print(flowRate);
    Serial.print("\tTotal liters: ");
    Serial.println(totalLiters);

    // Reset the timer for the next interval
    previousMillis = currentMillis;
  }
}

// Interrupt Service Routine: Increments the pulse count for each detected pulse
void pulseCounter() {
  pulseCount++;
}
