#From Github repository2
import os
import copy
import serial
#import pymongo
#from entities.Vehicle import *
from pynput import keyboard
from threading import Thread, Event
from time import sleep
from colorama import Fore, Back, Style


#---Classes---

class Wheel:

	def __init__(self, wheel_id, wheel_position):
		self.wheel_id = wheel_id
		self.wheel_position = wheel_position
		self.wheel_status = "Off"
		self.wheel_sense = ""
		self.wheel_code_control = 0x00

		print("Wheel " +  self.wheel_id + " Ready")

	def turnOnForward(self):
		self.wheel_status = "On"
		self.wheel_sense = "Forward"
		self.wheel_code_control =  0x01 << (2 * self.wheel_position)
		#print("Turning On Wheel " +  self.wheel_id + " Forward")

	def turnOnBackward(self):
		self.wheel_status = "On"
		self.wheel_sense = "Backward"
		self.wheel_code_control = 0x02 << (2 * self.wheel_position)
		#print("Turning On Wheel " +  self.wheel_id + " Backward")

	def turnOff(self):
		self.wheel_status = "Off"
		self.wheel_sense = ""
		self.wheel_code_control = 0x00 << (2 * self.wheel_position)
		#print("Turning Off Wheel " +  self.wheel_id)

	def printStatus(self):
		print("Wheel " + self.wheel_id + " " + self.wheel_status + " " + self.wheel_sense)

	def getWheelID(self):
		return self.wheel_id

	def getWheelStatus(self):
		return self.wheel_status

	def getWheelSense(self):
		return self.wheel_sense

	def getWheelControl(self):
		return self.wheel_code_control


class Control_Connection:

	def __init__(self, connectionPort, baud):
		self.connectionPort = connectionPort
		#self.command = 0
		self.ser = serial.Serial(port = self.connectionPort, baudrate = baud)

		#self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		#self.mydb = self.myclient["VehicleData"]
		#self.mycol = self.mydb["VehicleSensors"]

	def sendCommand(self, command, time):
		#self.command = command
		#values = bytearray([self.command])
		values = bytearray([command])
		retVal = self.ser.write(values)

	def sendLetter(self, letter):
		#self.command = command
		#values = bytearray([letter])
		retVal = self.ser.write(bytearray(letter, 'ascii'))

	def readData(self):
		if self.ser.in_waiting > 0 :
			data = self.ser.readline()
			print(str(data))
			#mydict = {"Encoders":{"WFR":data[0].decode(), "WFL" : data[1].decode(),
	     	#"WBR":data[2].decode(), "WBL":data[3].decode()}}
			#resp = self.mycol.insert_one(mydict)
			
			#print(mydict)


class Vehicle:

	def __init__(self, vehicle_id, numberOfWheels, wheel_id):
		self.numberOfWheels = numberOfWheels
		self.wheels = []
		self.vehicleID = vehicle_id
		self.printInData = False
		self.timeOn = 25

		os.system('clear')
		print("Setting Up Vehicle...\n")
		for x in range(self.numberOfWheels):
			self.wheels.append(Wheel(wheel_id[x], x))

	def updateWheel(self, wheel_id, wheel_sense):
		if wheel_sense == 1:
			self.wheels[wheel_id].turnOnForward()
		
		elif wheel_sense == 2:
			self.wheels[wheel_id].turnOnBackward()

		elif wheel_sense == 0:
			self.wheels[wheel_id].turnOff()

	def updateVehicle(self, controlConn):
		command = 0
		for x in range(self.numberOfWheels):
			comm = self.wheels[x].getWheelControl()
			command = command | comm
		#print(str(command))
		controlConn.sendCommand(command,self.timeOn)


	def stopVehicle(self, controlConn):
		#command = 0
		for x in range(self.numberOfWheels):
			self.updateWheel(x,0)
		self.updateVehicle(controlConn)

	def goVehicle(self, controlConn):
		#command = 0
		for x in range(self.numberOfWheels):
			self.updateWheel(x,1)
		self.updateVehicle(controlConn)

	def backVehicle(self, controlConn):
		#command = 0
		for x in range(self.numberOfWheels):
			self.updateWheel(x,2)
		self.updateVehicle(controlConn)

	def turnLeft(self, controlConn):
		#command = 0
		for x in range(self.numberOfWheels):
			if (x%2) == 0: 
				self.updateWheel(x,2)
			else:
				self.updateWheel(x,1)
		self.updateVehicle(controlConn)

	def turnRight(self, controlConn):
		#command = 0
		for x in range(self.numberOfWheels):
			if (x%2) == 0: 
				self.updateWheel(x,1)
			else:
				self.updateWheel(x,2)
		self.updateVehicle(controlConn)

	#def controlVehicle(self, control, command):
	#	control.sendCommand(command)

	def incTimeOn(self):
		self.timeOn = self.timeOn + 1
		print(f'Time on {self.timeOn}')

	def decTimeOn(self):
		self.timeOn = self.timeOn - 1
		print(f'Time on {self.timeOn}')

#---Functions---

def printMenu(vehicle):
	print(Fore.GREEN + "---Vehicle Status---\n")
	print(Style.RESET_ALL)
	for x in range(wheelsN):
		print(str(x) + ". Wheel " + vehicle.wheels[x].getWheelID() + " " + 
			vehicle.wheels[x].getWheelStatus() + " " + vehicle.wheels[x].getWheelSense())

#Modified to receive a serial connection object as parameter
def serialInThread(event, serial_connection):
	print(f'Running Background Serial RX for {serial_connection.connectionPort}...\n')
	while True:
		serial_connection.readData()
		if event.is_set():
			break
	return False

def keyOnRelease(key):
	#bandFlag = False
	if key == keyboard.Key.esc:
		return False
	elif key == keyboard.Key.up:	
		#print(" UP ")
		#print("\n")
		#bandFlag=True
		vehicle.goVehicle(controlConn)
		stm32_serial.sendLetter('a')
		sleep(1)
		stm32_serial.sendLetter('b')
	elif key == keyboard.Key.right:
		#print(" RIGHT ")
		#print("\n")
		#bandFlag=True
		vehicle.turnRight(controlConn)
	elif key == keyboard.Key.down:
		#print(" DOWN ")
		#print("\n")
		#bandFlag=True
		vehicle.backVehicle(controlConn)
		stm32_serial.sendLetter('a')
		sleep(8)
		stm32_serial.sendLetter('b')
	elif key == keyboard.Key.left:
		#print(" LEFT ")
		#print("\n")
		#bandFlag=True
		vehicle.turnLeft(controlConn)

	elif key == keyboard.Key.space:
		vehicle.incTimeOn()

	#if bandFlag:
		#bandFlag = False		
		#sleep(0.28)
		#vehicle.stopVehicle(controlConn)

#---Code---

resp = 0
wheelsN = 4
serialPort = "/dev/rfcomm0"

#Open port for connection with stm32 serial.
serialPortSTM32 = '/dev/ttyACM0'

#The wheel position specification must follow Right - Left
wheelsIDs = ["Front Right", "Front Left", "Back Right", "Back Left"]

vehicle = Vehicle("Vehicle 1", wheelsN, wheelsIDs)
controlConn = Control_Connection(serialPort, 9600)

#Create a new serial object to connect with stm32
stm32_serial = Control_Connection(serialPortSTM32, 115200)

input("Successful Configuration!\n")


#---------Main--------

while resp != "X":
	os.system('clear')
	
	printMenu(vehicle)

	print(Fore.RED + "\nE. Edit    X. Exit   D. Control   S. Stop Vehicle \n")
	print(Style.RESET_ALL)
	resp = input("Enter an option: ")
	resp.upper()

	if resp == "E":
		vehicle_copy = copy.deepcopy(vehicle)

		while resp != "S" and resp != "C":
			os.system('clear')
			print(Fore.RED + "In Edition!")
			print(Style.RESET_ALL)
			printMenu(vehicle)

			print(Fore.RED + "\nC. Cancel    S. Save")
			print(Style.RESET_ALL)
			resp = input("Select Wheel: ")		

			if resp != "S" and resp != "C":
				os.system('clear')
				print("0. Stop")
				print("1. Move Forward")
				print("2. Move Backward")
		
				respMove = input("\nEnter an option: ")
				vehicle.updateWheel(int(resp), int(respMove))

			if resp == "C":
				vehicle = copy.deepcopy(vehicle_copy)
				resp = ""
				break

			if resp == "S":
				vehicle.updateVehicle(controlConn)
				resp = ""
				input("Done!")
				break

	elif resp == "S":
		vehicle.stopVehicle(controlConn)
		input("Vehicle Stoped!")

	elif resp == "D":
		print("Vehicle Controller")
		eventStop = Event()
		#Send controlConn object as parameter
		t1 = Thread(target=serialInThread, args=(eventStop, controlConn, ))
		t1.start()

        #Start thread for to listening to RX STM32
		t2 = Thread(target=serialInThread, args=(eventStop, stm32_serial, ))
		t2.start()

		print("Waiting for a key...")

		with keyboard.Listener(on_release=keyOnRelease) as listener:
			listener.join()

		eventStop.set()
		t1.join()
		t2.join()	
		input(" Control Exit! ")

