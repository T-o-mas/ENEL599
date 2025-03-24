import serial
import time
import csv
from datetime import datetime
import os
import threading

# Initialize serial connection
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

# Get the current working directory of the script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Create 'outputs/<timestamp>' directory inside that base directory
timestamp_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_dir = os.path.join(base_dir, 'outputs-flow', timestamp_folder)

# Create the directory
os.makedirs(output_dir, exist_ok=True)

# Full CSV file path
csv_path = os.path.join(output_dir, 'flow_data_log.csv')

# Shared flag to signal when to stop
stop_flag = threading.Event()

def wait_for_enter():
    input("Press Enter to stop logging...\n")
    stop_flag.set()

# Start Enter-listening thread
threading.Thread(target=wait_for_enter, daemon=True).start()

# Open CSV file for writing
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Pi Timestamp', 'Arduino Timestamp (s)', 'Flow Rate (L/min)', 'Total Liters'])

    try:
        while not stop_flag.is_set():
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(line)

                now = datetime.now()
                pi_time = now.strftime('%Y-%m-%d %H:%M:%S.') + f"{now.microsecond // 1000:03d}"

                try:
                    parts = line.split('|')
                    arduino_time = parts[0].split(':')[1].strip()
                    flow_rate = parts[1].split(':')[1].split('\t')[0].strip()
                    total_liters = parts[1].split('Total liters:')[1].strip()

                    writer.writerow([pi_time, arduino_time, flow_rate, total_liters])
                except (IndexError, ValueError) as e:
                    print("Could not parse line:", line)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        ser.close()
        print("Logging stopped and serial connection closed.")
