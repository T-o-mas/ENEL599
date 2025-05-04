from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.Encoder import *
from Phidget22.Devices.CurrentInput import *
import traceback
import time
import csv
import matplotlib.pyplot as plt
import pandas as pd

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