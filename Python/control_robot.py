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
import numpy as np
import pandas as pd
import NNet
import sys,termios
import Map as mp


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

	def turnOnBackward(self):
		self.wheel_status = "On"
		self.wheel_sense = "Backward"
		self.wheel_code_control = 0x02 << (2 * self.wheel_position)

	def turnOff(self):
		self.wheel_status = "Off"
		self.wheel_sense = ""
		self.wheel_code_control = 0x00 << (2 * self.wheel_position)

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

	def __init__(self, connectionPort, baud, opnfile):
		self.connectionPort = connectionPort
		#self.command = 0
		self.opnfile = opnfile
		self.sample = 0
		self.waiting_range = False
		try:
			self.ser = serial.Serial(port = self.connectionPort, baudrate = baud)
		except serial.SerialException as e:
			print(f'Error {e}')

		#self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		#self.mydb = self.myclient["VehicleData"]
		#self.mycol = self.mydb["VehicleSensors"]
		self.odometry = []
		self.ranges = []
        
		if self.opnfile:
			self.file_name = "./results/DataCollector.txt"
			self.file_connection = open(self.file_name, "w", encoding='utf-8')
			if self.file_connection != None:
				print("File open successfull!")

	def sendCommand(self, command, time):
		values = bytearray([command])
		retVal = self.ser.write(values)

	def sendLetter(self, letter):
		retVal = self.ser.write(bytearray(letter, 'ascii'))

	def readData(self):
		if self.ser.in_waiting > 0 and self.ser.is_open:
			data = self.ser.readline()
			data = data.decode(('utf-8;')).rstrip()
			data_float = map(lambda x: float(x), str(data).split(" "))
			data_df = pd.DataFrame(data_float)
			data_df = data_df[0]
			print(data_df.to_numpy())
			buffer_len = len(data_df)
			if buffer_len == 4:
				# Odometry data
				self.odometry.append(data_df.to_numpy())
			elif buffer_len == 22:
				# Range sensors data
				self.ranges.append(data_df.to_numpy())
			if self.waiting_range == False and estimate_NNet:
				if data != "" and data != "\n":
					data_df = NNet.normalize(data_df)
					nnet_res = NNet.eval_NN(data_df)
					self.sample = self.sample + 1
					termios.tcflush(sys.stdin, termios.TCIOFLUSH)
					real_measure = input("Measure: ")
					print(f'{self.sample} {data} {nnet_res}')
					if self.opnfile:
						self.file_connection.write(
					    str(data) + " " + str(nnet_res) + " " + real_measure + "\n")
			else:
				self.waiting_range = False
				#if self.opnfile:
				#		self.file_connection.write(
				#	    str(data) + "\n")

			#mydict = {"Encoders":{"WFR":data[0].decode(), "WFL" : data[1].decode(),
	     	#"WBR":data[2].decode(), "WBL":data[3].decode()}}
			#resp = self.mycol.insert_one(mydict)
			
			#print(mydict)
	def closeConnections(self):
		print(self.odometry)
		print(self.ranges)
		if self.opnfile:
			for entry_block in self.odometry:
				self.file_connection.write("[")
				for entry in entry_block:
					self.file_connection.write(str(entry) + ",")
				self.file_connection.write("],\n")

			for entry_block in self.ranges:
				self.file_connection.write("[")
				for entry in entry_block:
					self.file_connection.write(str(entry) + ",")
				self.file_connection.write("],\n")

		self.ser.close()
		if self.opnfile == True:
		    self.file_connection.close()



class Vehicle:

	def __init__(self, vehicle_id, numberOfWheels, wheel_id):
		self.numberOfWheels = numberOfWheels
		self.wheels = []
		self.vehicleID = vehicle_id
		self.printInData = False
		self.timeOn = 25

		#os.system('clear')
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
		controlConn.sendCommand(command,self.timeOn)


	def stopVehicle(self, controlConn):
		for x in range(self.numberOfWheels):
			self.updateWheel(x,0)
		self.updateVehicle(controlConn)

	def goVehicle(self, controlConn):
		for x in range(self.numberOfWheels):
			self.updateWheel(x,1)
		self.updateVehicle(controlConn)

	def backVehicle(self, controlConn):
		for x in range(self.numberOfWheels):
			self.updateWheel(x,2)
		self.updateVehicle(controlConn)

	def turnLeft(self, controlConn):
		for x in range(self.numberOfWheels):
			if (x%2) == 0: 
				self.updateWheel(x,2)
			else:
				self.updateWheel(x,1)
		self.updateVehicle(controlConn)

	def turnRight(self, controlConn):
		for x in range(self.numberOfWheels):
			if (x%2) == 0: 
				self.updateWheel(x,1)
			else:
				self.updateWheel(x,2)
		self.updateVehicle(controlConn)

	def takeRange(self, controlConn):
		for x in range(self.numberOfWheels):
			self.updateWheel(x, 3)
		self.updateVehicle(controlConn)

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
			#serial_connection.file_connection.close()
			serial_connection.closeConnections()
			break
	return False

def keyOnRelease(key):
	if key == keyboard.Key.esc:
		return False
	elif key == keyboard.Key.up:
		print("")	
		vehicle.goVehicle(controlConn)
		if stm32_serial_selector:
			stm32_serial.sendLetter('a')
			sleep(8)
			stm32_serial.sendLetter('b')
	elif key == keyboard.Key.right:
		print("")
		vehicle.turnRight(controlConn)
	elif key == keyboard.Key.down:
		print("")
		vehicle.backVehicle(controlConn)
		if stm32_serial_selector:
			stm32_serial.sendLetter('a')
			sleep(8)
			stm32_serial.sendLetter('b')
	elif key == keyboard.Key.left:
		print("")
		vehicle.turnLeft(controlConn)
	elif key == keyboard.Key.f1:
		vehicle.incTimeOn()
	elif key == keyboard.Key.space:
		# Take distance
		controlConn.waiting_range = True
		controlConn.sendCommand(255, 25)
		#vehicle.takeRange(controlConn)

def select_devices(stm32_serial_selector):
	serial_open = False
	serial_bth_open = False
	serial_stm = ""
	serial_bth = ""
	try:
		dev_list = os.listdir('/dev/')
		if 'serial' in dev_list and stm32_serial_selector == True:
			cmd = 'ls -l /dev/serial/by-id/' 
			os.system(cmd)
			#for dev in serie_list:
			#	print(dev)
			while serial_stm == "":
				serial_stm = input("Enter the STM32 Serial Port: ")
			cmd = 'sudo chown ruben ' + '/dev/' + serial_stm 
			os.system(cmd)
			serial_open = True
		elif stm32_serial_selector == False:
			serial_open = True
			serial_stm = "STM32 Serial Disabled"
		else:
			print("There are not serial interfaces!")
		if 'rfcomm0' not in dev_list:
			print("There is not bluetooth interface open!")
			try:
				print("Trying to start Bluetooth connection...")
				cmd = 'sudo rfcomm bind 0 "98:D3:61:F5:E1:50" 1 && sudo chown ruben /dev/rfcomm0'
				os.system(cmd)
				serial_bth = "rfcomm"
				serial_bth_open = True
			except:
				print("Cannot open Bluetooth Interface!")
				serial_bth_open = False
		else:
			print("Setting up interface")
			serial_bth = 'rfcomm0'
			cmd = "sudo chown ruben /dev/rfcomm0"
			os.system(cmd)
			serial_bth_open = True
	except:
		print("Cannot open /dev folder!")
		serial_open = False
		serial_bth_open = False
		
	return (serial_open, serial_bth_open, serial_stm, serial_bth)

def kinematic_model(ticks_left, ticks_right, drive_time, t_old):
	pulses_per_turn = 20
	wheel_radius = 6.96
	rear_length = 20
	x_icr = 1
	wl = (ticks_left * 3.1415 / pulses_per_turn) / drive_time
	wr = (ticks_right * 3.1415 / pulses_per_turn) / drive_time
	vx = wheel_radius * ((wl + wr) / 2)
	wz = wheel_radius * ((wr - wl) / rear_length)
	x = (np.cos(t_old) * vx) + (x_icr * np.sin(t_old) * wz)
	y = (np.sin(t_old) * vx) + (-x_icr * np.cos(t_old) * wz)
	t = wz
	print(f'x={x} y={y} orientation={t}')

#---Code---
if __name__ == "__main__":
	stm32_serial_selector = False
	save_in_file = True
	estimate_NNet = False
	devs = select_devices(stm32_serial_selector)
	
	if devs[0] & devs[1] == True:
		print("Running Controller")
		serialPortSTM32 = "/dev/" + devs[2]
		serialPort = "/dev/" + devs[3]
		print(serialPortSTM32)
		print(serialPort)
		
		wheelsN = 4
		#The wheel position specification must follow Right - Left
		wheelsIDs = ["Front Right", "Front Left", "Back Right", "Back Left"]
		vehicle = Vehicle("Vehicle 1", wheelsN, wheelsIDs)

		controlConn = Control_Connection(serialPort, 9600, save_in_file)
		
		if stm32_serial_selector:
			stm32_serial = Control_Connection(serialPortSTM32, 115200) #This section still doesn't apply the file flag
		
		input("Successful Configuration!\n")
		os.system('clear')
		print("Robot's Controller")
		eventStop = Event()
		t1 = Thread(target=serialInThread, args=(eventStop, controlConn, ))
		t1.start()
		if stm32_serial_selector:
			t2 = Thread(target=serialInThread, args=(eventStop, stm32_serial, ))
			t2.start()
		print("Waiting for a key...")
		with keyboard.Listener(on_release=keyOnRelease) as listener:
			listener.join()
		eventStop.set()
		t1.join()
		if stm32_serial_selector:
			t2.join()
		input(" Control Exit! ")
	else:
		print("There are not an available connection!")
