#!/usr/bin/env python
import usb
import sys
from time import sleep
from time import clock

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
		self.cmd['SET_EYE']	= 0xAA
		
		self.cmd['CLOCK']	 = 48000000
		self.cmd['T0_CLOCK'] = self.cmd['CLOCK'] / 12
		self.cmd['T2_CLOCK'] = self.cmd['CLOCK'] / 4
		print self.cmd
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

			while inline:
				lenPos 	= fw.read(4)
				length 	= (lenPos[0]<<8) | lenPos[1]
				pos    	= (lenPos[2]<<8) | lenPos[3]
				buf 	= fw.read(lenght)
				
				if buf != 1:
					raise ValueError("Error while loading firmware (buf != 1)")
				
				LIBUSB_REQUEST_TYPE_VENDOR = (0x02 << 5)
				control_res = self.handle.controlMsg(LIBUSB_REQUEST_TYPE_VENDOR, 0xA0, buf, pos)
				
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
		# 01 00 18 00 - E1 29 FF FF - 68 B5 FF FF - 81 DF FF FF
		# 30 28 24 22 - 0A 08 05 04 - 61 79 F9 FF
		T0_COUNT = lambda x: (-(x)*(self.cmd['T0_CLOCK']/1000000)+1) 
		T2_COUNT = lambda x: (-(x)*(self.cmd['T2_CLOCK']/1000000)+1) 

		
		w = int( T2_COUNT(4568.50))
		x = int( T0_COUNT(4774.25))
		y = int( T0_COUNT(self.frameTime))
		z = int( T2_COUNT(self.activeTime))

		cmdTimings = [ self.cmd['WRITE'], 0x00, 0x18, 0x00, 
						w, w>>8, w>>16, w>>24,
						x, x>>8, x>>16, x>>24, 
						y, y>>8, y>>16, y>>24,
						0x30, 0x28, 0x24, 0x22,
						0x0a, 0x08, 0x05, 0x04,
						z, z>>8, z>>16, z>>24 ]
		
		self.write(2, cmdTimings)
		
		# Second command
		# 01 1C 02 00 02 00
		cmd0x1c = [ self.cmd['WRITE'], 0x1c, 0x02, 0x00, 0x02, 0x00 ]
		self.write(2, cmd0x1c)
		
		# Third command
		# 01 1E 02 00 F0 00
		timeout = self.rate * 2
		cmdTimeout = [ self.cmd['WRITE'], 0x1e, 0x02, 0x00, timeout, timeout>>8 ]
		self.write(2, cmdTimeout)
		
		# Fourth command
		# 01 1B 01 00 07
		cmd0x1b = [ self.cmd['WRITE'], 0x1b, 0x01, 0x00, 0x07 ]
		self.write(2, cmd0x1b)

	def setEye(self, first = 0, r = 0): # Swap Eye
		if first == 0:
			eye = 0xFE
		else:
			eye = 0xFF
			
		# AA FF 00 00 .. .. FF FF
		# AA FE 00 00 .. .. FF FF
		buf = [ self.cmd['SET_EYE'], eye, 0x00, 0x00, r, r>>8, 0xFF, 0xFF ]
		self.write(1, buf)
	
	# Magestik add
	def stopDevice(self, first = 0, r = 0): # stop shuttering ^^
		cmd1 = [ self.cmd['READ'], 0x1b, 0x01, 0x00 ]
		self.write(2, cmd1)
		
		data = self.read(4, 5) # 1b 01 00 04 07
		
		cmd0x1b = [ self.cmd['WRITE'], 0x1b, 0x01, 0x00, 0x03 ]
		self.write(2, cmd0x1b)	
		
		buf = [ self.cmd['SET_EYE'], 0xFF, 0x00, 0x00, 0x71, 0xD9, 0xFF, 0xFF ]
		self.write(1, buf)		
	
	def eventKeys(self): # Ask for key which have been pressed	
		# Time beetween calling this functions in the usblog
		# 0.300 / 0.845 / 0.498 / 0.132 / 0.099 / 0.131 / 0.132 / 0.099 / 0.132 / 0.1 / 0.132 / 0.132 / 0.131 / 0.132 / 0.242
		# When constant it's about every 16 eye swap
		
		# self.cmd['READ'] | self.cmd['CLEAR'] = 0x42 
		cmd1 = [self.cmd['READ'] | self.cmd['CLEAR'], 0x18, 0x03, 0x00] # OK
		self.write(2, cmd1)
		
		data = self.read(4, 4+cmd1[2])
		
		try:
			key 	= {}
		
			key[1] 	= int(data[4]) 	# Scroll 
			# PRINT => vers le bas = {1: 255, 2: 0, 3: 0} ou vers le haut = {1: 1, 2: 0, 3: 0}
		
			key[2]	= int(data[5]) # Scroll + button 
			# PRINT => vers le bas =  {1: 0, 2: 255, 3: 0} ou vers le haut = {1: 0, 2: 1, 3: 0}
		
			key[3]	= int(data[6] & 0x01) # Button
			# PRINT => {1: 0, 2: 0, 3: 1}

			if key[1] > 0:
				print key
		except:
			print "Key event Error"

if __name__ == "__main__":
	nv = Nvidia()
	
	nv.eventKeys() # Yeah we ask for keys here ... like in my usb log (I think it's for the "clear" command)
	
	nv.setRefreshRate()
	
	eye = 0
	key = 0
	while True:
		nv.setEye(eye)
		eye = 1 - eye
		
		if key == 16:
			nv.eventKeys()
			key = 0
		else:
			key = key + 1
		
		sleep(1.0 / nv.rate)
