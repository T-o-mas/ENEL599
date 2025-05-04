import serial
import time
import csv
from datetime import datetime
import os
import threading

# Initialize serial connection to Arduino
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow Arduino to reset

# Get the current script directory and go one level up
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)

# Create folder structure one level above
timestamp_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_dir = os.path.join(parent_dir, 'outputs-flow-pressure', timestamp_folder)
os.makedirs(output_dir, exist_ok=True)

csv_path = os.path.join(output_dir, 'flow_pressure_data_log.csv')

# Stop flag
stop_flag = threading.Event()

def wait_for_enter():
    input("Press Enter to stop logging...\n")
    stop_flag.set()

threading.Thread(target=wait_for_enter, daemon=True).start()

first_line_skipped = False

with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        'Pi Timestamp',
        'Arduino Time (ms)',
        'Inlet Flow (L/min)',
        'Outlet Flow (L/min)',
        'Inlet Pressure (PSI)',
        'Outlet Pressure (PSI)'
    ])
    file.flush()
    
    try:
        while not stop_flag.is_set():
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                if not first_line_skipped:
                    print("Skipping first line:", line)
                    first_line_skipped = True
                    continue

                print("Received line:", line)
                now = datetime.now()
                pi_timestamp = now.strftime('%Y-%m-%d %H:%M:%S.') + f"{now.microsecond // 1000:03d}"
                
                try:
                    parts = line.split()
                    if len(parts) != 5:
                        print("Invalid format, skipping:", line)
                        continue

                    arduino_time = parts[0]
                    inlet_flow = parts[1]
                    outlet_flow = parts[2]
                    inlet_psi = parts[3]
                    outlet_psi = parts[4]

                    row = [pi_timestamp, arduino_time, inlet_flow, outlet_flow, inlet_psi, outlet_psi]
                    print("Writing row:", row)
                    writer.writerow(row)
                    file.flush()

                except Exception as parse_error:
                    print("Parsing failed:", line, "Error:", parse_error)
    except Exception as e:
        print("Error during logging:", e)
    finally:
        ser.close()
        print("Serial connection closed. Logging stopped.")
