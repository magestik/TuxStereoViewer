#!/usr/bin/env python
import usb
import sys
from time import sleep

# ! MUST BE ROOT ! #

class Nvidia:
	"Abstract class for Nvidia 3D Vision controll"
	
	def __init__(self):
		self.validRefreshRate 	= [85, 100, 75, 72, 70, 60]
		self.currentRefreshRate	= 0
		self.eye				= 'left'
		
		self.cmd = {}
		self.cmd['WRITE']	= 0x01
		self.cmd['READ'] 	= 0x02
		self.cmd['CLEAR']	= 0x40
		
		self.cmd['CLOCK']	 = 48000000LL
		self.cmd['T0_CLOCK'] = (self.cmd['CLOCK']/12LL)
		self.cmd['T2_CLOCK'] = (self.cmd['CLOCK']/ 4LL)

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
		try:
			LIBUSB_ENDPOINT_OUT = 0x00
			self.handle.bulkWrite(endpoint | LIBUSB_ENDPOINT_OUT, data, 1000)
			#self.handle.bulkWrite(self.pipes[pipeno-1], data, 1000)
		except usb.USBError as e:
			if e.args != ('No error',): # http://bugs.debian.org/476796
				raise e
	
	def read(self, endpoint, size):
		try:
			LIBUSB_ENDPOINT_IN = 0x80
			return self.handle.bulkRead(endpoint | LIBUSB_ENDPOINT_IN, size, 1000)
			#return self.handle.bulkRead(self.pipes[pipeno-1], size, 1000)
		except usb.USBError as e:
			if e.args != ('No error',): # http://bugs.debian.org/476796
				raise e
	
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
		busses	= usb.busses() # List of all USB devices
		for bus in busses: # Search for Nvidia 3D Vision
			for dev in bus.devices:
				if dev.idProduct == idProduct and dev.idVendor == idVendor:
					return dev
	
	def checkDevice(self, dev): # Get Endpoints
		configs 		= dev.configurations[0]
		interface 		= configs.interfaces[0][0]
		self.endpoints 	= []
		self.pipes 		= []
		count 			= 0
		for endpoint in interface.endpoints:
			count = count + 1
			self.endpoints.append(endpoint)
			self.pipes.append(endpoint.address)
		return count

	def loadFirmware(self,filename):
		try:
			fw = open(filename, "rb")
		except:
			raise ValueError("Firmware not found !")
		else:
			print "Try to loading Firmware ..."
			#uint8_t lenPos[4];
			#uint8_t buf[1024];
			while inline:
				lenPos 	= fw.read(4)
				length 	= (lenPos[0]<<8) | lenPos[1]
				pos    	= (lenPos[2]<<8) | lenPos[3]
				buf 	= fw.read(lenght)
				
				if buf != 1:
					raise ValueError("Error while loading firmware (buf != 1)")
				
				LIBUSB_REQUEST_TYPE_VENDOR = (0x02 << 5)
				control_res = self.handle.controlMsg(LIBUSB_REQUEST_TYPE_VENDOR, 0xA0, buf, pos) 
				#res = libusb_control_transfer(LIBUSB_REQUEST_TYPE_VENDOR, 0xA0, pos, 0x0000, buf, length, 0 );
				
				if control_res < 0:
					raise ValueError("Error while loading firmware (res = %s)" % control_res)
			
			fw.close()
			
			# Disconnecting
			self.handle.reset() 
			self.handle.releaseInterface()
			del self.handle
			sleep(250000 / 1000000.0)
			
			# Reconnecting
			dev = self.findDevice(0x0007, 0x0955)
			self.handle = dev.open()
			self.handle.reset() 
			sleep(250000 / 1000000.0)
			
	#
	# Functions for controlling the Dongle
	#
	def setRefreshRate(self, rate = 120): # refresh variables and initialize usb device
		self.rate 		= rate
		self.frameTime	= 1000000 / self.rate
		self.activeTime	= 2080
		
		# First command
		T0_COUNT = lambda x: (-(x)*(self.cmd['T0_CLOCK']/1000000)+1)
		T2_COUNT = lambda x: (-(x)*(self.cmd['T2_CLOCK']/1000000)+1)

		
		w = T2_COUNT(4568.50)
		x = T0_COUNT(4774.25)
		y = T0_COUNT(self.frameTime)
		z = T2_COUNT(self.activeTime)

		cmdTimings = [ self.cmd['WRITE'], 0x00, 0x18, 0x00, 
						w, w>>8, w>>16, w>>24,
						x, x>>8, x>>16, x>>24, 
						y, y>>8, y>>16, y>>24,
						0x30, 0x28, 0x24, 0x22,
						0x0a, 0x08, 0x05, 0x04,
						z, z>>8, z>>16, z>>24 ]
		
		self.write(2, cmdTimings)
		
		# Second command
		cmd0x1c = [ self.cmd['WRITE'], 0x1c, 0x02, 0x00, 0x02, 0x00 ]
		self.write(2, cmd0x1c)
		
		# Third command
		timeout = self.rate * 2 
		cmdTimeout = [ self.cmd['WRITE'], 0x1e, 0x02, 0x00, timeout, timeout>>8 ]
		self.write(2, cmdTimeout)
		
		# Fourth command
		cmd0x1b = [ self.cmd['WRITE'], 0x1b, 0x01, 0x00, 0x07 ]
		self.write(2, cmd0x1b)


	def eventKeys(self): # Ask for key which have been pressed	
		cmd1 = [self.cmd['READ'] | self.cmd['CLEAR'], 0x18, 0x03, 0x00]
		self.write(2, cmd1)
		
		data = self.read(4, 4+cmd1[2])
		
		key 	= []
		key[1] 	= data[4] 			# Scroll
		key[2]	= data[5] 			# Scroll + button
		key[3]	= data[6] & 0x01; 	# Button
		print key

if __name__ == "__main__":
	nv = Nvidia()
	sleep(2)
	nv.eventKeys()
