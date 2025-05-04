from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.Encoder import *
from Phidget22.Devices.CurrentInput import *
import traceback
import time
import csv
import matplotlib.pyplot as plt
import pandas as pd

# Open a CSV file for writing data
csv_file = open("current_data.csv", "w", newline='')
csv_writer = csv.writer(csv_file)
# Write header row: time (seconds) and current (Amps)
csv_writer.writerow(["Time", "Current"])

def onCurrentChange(self, current):
    # Get current time relative to the start
    current_time = time.time() - start_time
    print("Current: " + str(current))
    # Write the current time and current value to the CSV file
    csv_writer.writerow([current_time, current])
    
def main():
    global start_time  # to record a start time for our timestamps
    start_time = time.time()

    dcMotor0 = DCMotor()
    encoder0 = Encoder()
    ch = CurrentInput()

    dcMotor0.openWaitForAttachment(5000)
    dcMotor0.setTargetVelocity(-1)
    
    ch.openWaitForAttachment(1000)
    ch.setOnCurrentChangeHandler(onCurrentChange)

    # Print some basic info
    maxCurrent = ch.getMaxCurrent()
    print("MaxCurrent: " + str(maxCurrent))
    minCurrent = ch.getMinCurrent()
    print("MinCurrent: " + str(minCurrent))
    current = ch.getCurrent()
    print("Current: " + str(current))

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    dcMotor0.close()
    encoder0.close()
    csv_file.close()  # Don't forget to close the CSV file
    

main()
# Read the CSV data into a DataFrame (assumes the CSV file has headers 'Time' and 'Current')
data = pd.read_csv('current_data.csv')

# Extract the time and current columns
time_vals = data['Time']
current_vals = data['Current']

# Create a figure and plot the data
plt.figure(figsize=(10, 6))
plt.plot(time_vals, current_vals, 'b-', linewidth=2)
plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('Current (A)', fontsize=12)
plt.title('Current vs. Time', fontsize=14)
plt.grid(True)
plt.show()
