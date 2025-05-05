from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.Encoder import *
from Phidget22.Devices.CurrentInput import *
from Phidget22.Devices.VoltageInput import *


import traceback
import time

def onPositionChange(self, positionChange, timeChange, indexTriggered):
    #Measured timeChange in ms
	#Amount of position changed since last event

	print("PositionChange: " + str(positionChange)) 
	print("TimeChange: " + str(timeChange)) 
	print("getPosition: " + str(self.getPosition()))
	
	rpm = ((positionChange/1200)/(timeChange/1000))*60 #Calculating RPM with applied rescale factors
	print(f"RPM: {rpm}")
	print("----------")

def onCurrentChange(self, current):
	print("Current: " + str(current))

def onVoltageChange(self, voltage):
	print("Voltage: " + str(voltage))
    

	
def main():
	dcMotor0 = DCMotor()
	encoder0 = Encoder()
	ch = CurrentInput()
	chv = VoltageInput()

	encoder0.setOnPositionChangeHandler(onPositionChange)
	encoder0.openWaitForAttachment(5000)

	dcMotor0.openWaitForAttachment(5000)
	dcMotor0.setTargetVelocity(0.7)

	ch.openWaitForAttachment(1000)
	ch.setOnCurrentChangeHandler(onCurrentChange)

	chv.setOnVoltageChangeHandler(onVoltageChange)
	chv.open()

	try:
		input("Press Enter to Stop\n")
	except (Exception, KeyboardInterrupt):
		pass

	dcMotor0.close()
	encoder0.close()


main()
