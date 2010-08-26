#!/usr/bin/env python
import usb # importa o nosso modulo
import sys
from time import sleep


class Nvidia:
	"Abstract class for Nvidia 3D Vision controll"
	
	def __init__(self):
		self.validRefreshRate 	= [85, 100, 75, 72, 70, 60]
		self.currentRefreshRate	= 0
		self.eye				= 'left'

		try:
			self.handle = self.getDevice()
		except:
			print "Can't initialise Nvidia 3D Vision"
		
		try:
			self.handle.setConfiguration(1) 
			self.handle.claimInterface(0) 
		except:
			print "Error during initialisation"
		
	def __del__(self):
		try:
			self.handle.releaseInterface()
			del self.handle
		except: # n'existe pas
			pass

	#
	# Functions for Writing/Reading in USB
	#
	def write(self, endpoint, data, size = 0):
		self.handle.bulkWrite(endpoint, data, 1000)
	
	def read(self, endpoint, size):
		return self.handle.bulkWrite(endpoint, size, 1000)

	
	#
	# Functions for initialising the Controller
	#
	def getDevice(self): # Make the link with the controller
		dev = self.findDevice(0x0007, 0x0955)	
		if dev is None:
			raise ValueError('Nvidia 3D Vision not detected')
		
		ep = self.checkDevice(dev)
		if ep == 0:
			self.loadFirmware()
		
		return dev.open()
	
	def findDevice(self, idProduct, idVendor): # Find the controller
		busses		= usb.busses() # List of all USB devices
		for bus in busses: # Search for Nvidia 3D Vision
			for dev in bus.devices:
				if dev.idProduct == idProduct and dev.idVendor == idVendor:
					return dev
	
	def checkDevice(self, dev): # Get Endpoints
		configs 		= dev.configurations[0]
		interface 		= configurats.interfaces[0][0]
		self.endpoints 	= []
		self.pipes 		= []
		count 			= 0
		for endpoint in interface:
			count = count + 1
			self.endpoints.append(endpoint)
			self.pipes.append(endpoint.address)
		return count

	def loadFirmware(self):
		print "Trying to load Firmware ..."
		pass # TODO
	
	#
	# Functions for controlling the Dongle
	#	
	def refresh(self): # refresh variables and initialize usb device
		rate = self.validRefreshRate[self.currentRefreshRate]
		a = (0.1748910 * (rate*rate*rate) - 54.5533 * (rate*rate) + 6300.40 * (rate) - 319395.0)
		b = (0.0582808 * (rate*rate*rate) - 18.1804 * (rate*rate) + 2099.82 * (rate) - 101257.0)
		c = (0.3495840 * (rate*rate*rate) - 109.060 * (rate*rate) + 12597.3 * (rate) - 638705.0)
		
		sequence = [ 0x00031842, 0x00180001, a, b, 0xfffff830, 0x22302824, 0x040a0805, c, 0x00021c01, 0x00000002, 0x00021e01, rate*2, 0x00011b01, 0x00000007, 0x00031840 ]
		
		readPipe = self.getDevice()			
		
		#self.write(self.pipe0, sequence, 4);
		#self.read(readPipe, readBuffer, 7);
		#self.write(self.pipe0, sequence+1, 28);
		#self.write(self.pipe0, sequence+8, 6);
		#self.write(self.pipe0, sequence+10, 6);
		#self.write(self.pipe0, sequence+12, 5);
		#self.write(self.pipe0, sequence+13, 4);

		del readPipe

	def nextRefreshRate(self, offset):
		self.currentRefreshRate = self.currentRefreshRate + 1
		if (self.currentRefreshRate >= len(self.validRefreshRate)):
			self.currentRefreshRate = 0
		
		self.refresh()
	
	def toggleEyes(self, offset):
		if(self.eye == 'left'):
			sequence = [ 0x0000feaa, offset ]
		else:
			sequence = [ 0x0000ffaa, offset ]
		
		#self.write(self.pipe1, sequence, 8)
		self.eye = 'right'

	def eventKeys(self): # Ask for key whiwh have been pressed
		cmd1 = [NVSTUSB_CMD_READ | NVSTUSB_CMD_CLEAR, 0x18, 0x03, 0x00]
		self.write(2, cmd1);
		
		data = self.read(4, len(readBuf))
		
		key 				= []
		key["wheelNormal"] 	= data[4] # Roulement de la molette
		key["wheelPressed"]	= data[5] # Appui sur la molette
		key["frontButton"]	= readBuf[6] & 0x01; # ???

if __name__ == "__main__":
	nv = Nvidia()
