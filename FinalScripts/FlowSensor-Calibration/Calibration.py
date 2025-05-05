import serial
import time
import csv
from datetime import datetime
import os
import threading

from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *

dcMotor0 = DCMotor()

def motor_control():
    try:
        dcMotor0.openWaitForAttachment(5000)
        dcMotor0.setTargetVelocity(0.0)  # Set motor speed (0.0 - 1.0)
    except Exception as e:
        print("Motor setup failed:", e)

def sensor_logging(stop_flag):
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino reset

    base_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_dir = os.path.join(base_dir, 'flow-calibration-counts', timestamp_folder)
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'flow_count_log.csv')
    print(f"Logging to: {csv_path}")

    first_line_skipped = False

    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pi Timestamp', 'Arduino Time (ms)', 'Pulse Count (Inlet)'])
        file.flush()

        try:
            while not stop_flag.is_set():
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    if not first_line_skipped:
                        first_line_skipped = True
                        continue

                    now = datetime.now()
                    pi_timestamp = now.strftime('%Y-%m-%d %H:%M:%S.') + f"{now.microsecond // 1000:03d}"

                    parts = line.split()
                    if len(parts) != 2:
                        print("Invalid format, skipping line")
                        continue

                    arduino_time, pulse_count = parts
                    writer.writerow([pi_timestamp, arduino_time, pulse_count])
                    file.flush()

        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            ser.close()
            print("Serial connection closed.")

def main():
    stop_flag = threading.Event()

    motor_thread = threading.Thread(target=motor_control, daemon=True)
    motor_thread.start()

    logging_thread = threading.Thread(target=sensor_logging, args=(stop_flag,), daemon=True)
    logging_thread.start()

    input("Press Enter to stop logging and shutdown...\n")
    stop_flag.set()

    time.sleep(1)
    dcMotor0.close()
    print("Motor closed. Logging stopped. Program complete.")

if __name__ == "__main__":
    main()
