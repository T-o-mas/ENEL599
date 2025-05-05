import serial
import time
import csv
from datetime import datetime
import os
import threading

from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.Encoder import *
from Phidget22.Devices.CurrentInput import *
from Phidget22.Devices.VoltageInput import *

dcMotor0 = DCMotor()
encoder0 = Encoder()
ch = CurrentInput()
chv = VoltageInput()

latest_rpm = 0.0
latest_current = 0.0
latest_voltage = 0.0
data_lock = threading.Lock()

def onPositionChange(self, positionChange, timeChange, indexTriggered):
    global latest_rpm
    rpm = ((positionChange / 1200) / (timeChange / 1000)) * 60
    with data_lock:
        latest_rpm = rpm

def onCurrentChange(self, current):
    global latest_current
    with data_lock:
        latest_current = current

def onVoltageChange(self, voltage):
    global latest_voltage
    with data_lock:
        latest_voltage = voltage

def motor_control():
    try:
        encoder0.setOnPositionChangeHandler(onPositionChange)
        encoder0.openWaitForAttachment(5000)

        dcMotor0.openWaitForAttachment(5000)
        dcMotor0.setTargetVelocity(1.0)  # Adjust speed of motor from 0.0-1.0

        ch.setOnCurrentChangeHandler(onCurrentChange)
        ch.openWaitForAttachment(1000)

        chv.setOnVoltageChangeHandler(onVoltageChange)
        chv.open()

    except Exception as e:
        print("Motor control setup failed:", e)

def sensor_logging(stop_flag):
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_dir = os.path.join(base_dir, 'outputs-flow-pressure', timestamp_folder)
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'flow_pressure_data_log.csv')
    print(f"Logging to: {csv_path}")

    first_line_skipped = False

    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Pi Timestamp',
            'Arduino Time (ms)',
            'Inlet Flow (L/min)',
            'Outlet Flow (L/min)',
            'Inlet Pressure (PSI)',
            'Outlet Pressure (PSI)',
            'Motor Current (A)',
            'Motor Voltage (V)',
            'Motor RPM'
        ])
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
                    if len(parts) != 5:
                        print("Invalid format, skipping line")
                        continue

                    arduino_time, inlet_flow, outlet_flow, inlet_psi, outlet_psi = parts

                    with data_lock:
                        row = [
                            pi_timestamp,
                            arduino_time,
                            inlet_flow,
                            outlet_flow,
                            inlet_psi,
                            outlet_psi,
                            f"{latest_current:.3f}",
                            f"{latest_voltage:.3f}",
                            f"{latest_rpm:.2f}"
                        ]

                    writer.writerow(row)
                    file.flush()

        except Exception as e:
            print("Serial logging failed:", e)
        finally:
            ser.close()
            print("Serial connection closed.")

def main():
    stop_flag = threading.Event()

    # Start motor control
    motor_thread = threading.Thread(target=motor_control, daemon=True)
    motor_thread.start()

    # Start logging
    logging_thread = threading.Thread(target=sensor_logging, args=(stop_flag,), daemon=True)
    logging_thread.start()

    # Wait for user to stop
    input("Press Enter to stop...\n")
    stop_flag.set()

    # Allow time to flush and close
    time.sleep(1)

    dcMotor0.close()
    encoder0.close()
    ch.close()
    chv.close()
    print("All devices closed. Program finished.")

if __name__ == "__main__":
    main()
