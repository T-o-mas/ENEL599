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
print("Base directory:", base_dir)

# Create 'outputs/<timestamp>' directory inside that base directory
timestamp_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_dir = os.path.join(base_dir, 'outputs-pressure', timestamp_folder)
os.makedirs(output_dir, exist_ok=True)
print("Output directory:", output_dir)

# Full CSV file path
csv_path = os.path.join(output_dir, 'pressure_data_log.csv')
print("CSV file path:", csv_path)

# Shared flag to signal when to stop
stop_flag = threading.Event()

def wait_for_enter():
    input("Press Enter to stop logging...\n")
    stop_flag.set()

# Start Enter-listening thread
threading.Thread(target=wait_for_enter, daemon=True).start()

first_line_skipped = False  # Flag to skip the first line

with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Pi Timestamp', 'Arduino Timestamp (s)', 'Voltage (V)', 'Pressure (PSI)'])
    file.flush()  # Flush header immediately
    
    try:
        while not stop_flag.is_set():
            # Read a line with error handling
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                # Skip the first line of Arduino output
                if not first_line_skipped:
                    print("Skipping first line:", line)
                    first_line_skipped = True
                    continue

                print("Received line:", line)
                
                now = datetime.now()
                pi_time = now.strftime('%Y-%m-%d %H:%M:%S.') + f"{now.microsecond // 1000:03d}"
                
                try:
                    parts = line.split('|')
                    # Check if there are at least 3 parts
                    if len(parts) < 3:
                        print("Skipping line, not enough parts:", line)
                        continue
                    
                    # Parse values (splitting only once after the first colon)
                    arduino_time = parts[0].split(':', 1)[1].strip()
                    voltage = parts[1].split(':', 1)[1].split('V')[0].strip()
                    pressure = parts[2].split(':', 1)[1].split('PSI')[0].strip()
                    
                    row = [pi_time, arduino_time, voltage, pressure]
                    print("Writing row:", row)
                    writer.writerow(row)
                    file.flush()  # Flush after writing each row
                except Exception as e:
                    print("Could not parse line:", line, "Error:", e)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        ser.close()
        print("Logging stopped and serial connection closed.")
