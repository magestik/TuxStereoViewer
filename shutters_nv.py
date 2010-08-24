#!/usr/bin/env python
import usb # importa o nosso modulo
import sys
from time import sleep

# In "/var/log/syslog" :
# Aug 13 20:07:48 desktop01 kernel: [35638.636030] usb 1-8: new high speed USB device using ehci_hcd and address 5
# Aug 13 20:07:48 desktop01 kernel: [35638.773155] usb 1-8: New USB device found, idVendor=0955, idProduct=0007
# Aug 13 20:07:48 desktop01 kernel: [35638.773160] usb 1-8: New USB device strings: Mfr=1, Product=2, SerialNumber=0
# Aug 13 20:07:48 desktop01 kernel: [35638.773163] usb 1-8: Product: NVIDIA stereo controller
# Aug 13 20:07:48 desktop01 kernel: [35638.773172] usb 1-8: Manufacturer: Copyright (c) 2008 NVIDIA Corporation
# Aug 13 20:07:48 desktop01 kernel: [35638.773288] usb 1-8: configuration #1 chosen from 1 choice

class Nvidia:
	"Abstract class for Nvidia 3D Vision controll"
	
	def __init__(self):
		self.validRefreshRate 	= [85, 100, 75, 72, 70, 60]
		self.currentRefreshRate	= 0
		self.eye				= 'left'
		
		self.busses		= usb.busses()

		#try:
		self.pipe0 = self.getDevice()
		self.pipe1 = self.getDevice()
		self.refresh()
		#except:
		#	print "Can't initialise Nvidia 3D Vision"
	
	def __del__(self):
		self.pipe0.reset()
		del self.pipe0
		
		self.pipe1.reset()
		del self.pipe1
	
	def getDevice(self):
		dev = self.findDevice(self.busses, 0x0007, 0x0955)
		if dev is None:
			print 'Nvidia 3D Vision not detected'
			#raise ValueError('Nvidia 3D Vision not detected')
		return dev.open()
	
	def findDevice(self, busses, idProduct, idVendor):
		for bus in busses:
			for dev in bus.devices:
				if dev.idProduct == idProduct and dev.idVendor == idVendor:
					return dev
	
	def refresh(self): # refresh variables and initialize usb device
		rate = self.validRefreshRate[self.currentRefreshRate]
		a = (0.1748910 * (rate*rate*rate) - 54.5533 * (rate*rate) + 6300.40 * (rate) - 319395.0)
		b = (0.0582808 * (rate*rate*rate) - 18.1804 * (rate*rate) + 2099.82 * (rate) - 101257.0)
		c = (0.3495840 * (rate*rate*rate) - 109.060 * (rate*rate) + 12597.3 * (rate) - 638705.0)
		
		sequence = [ 0x00031842, 0x00180001, a, b, 0xfffff830, 0x22302824, 0x040a0805, c, 0x00021c01, 0x00000002, 0x00021e01, rate*2, 0x00011b01, 0x00000007, 0x00031840 ]
		
		readPipe = self.dev.open()				
		
		#writeToPipe(pipe0, sequence, 4);
		#readFromPipe(readPipe, readBuffer, 7);
		#writeToPipe(pipe0, sequence+1, 28);
		#writeToPipe(pipe0, sequence+8, 6);
		#writeToPipe(pipe0, sequence+10, 6);
		#writeToPipe(pipe0, sequence+12, 5);
		#writeToPipe(pipe0, sequence+13, 4);
		
		self.readPipe.reset()
		del self.readPipe
	
	def toggleEyes(self, offset):
		if(self.eye == 'left'):
			sequence = [ 0x0000feaa, offset ]
		else:
			sequence = [ 0x0000ffaa, offset ]
		
		#writeToPipe(pipe1, sequence, 8)
		self.eye = 'right'
	
	def nextRefreshRate(self, offset):
		self.currentRefreshRate = self.currentRefreshRate + 1
		if (self.currentRefreshRate >= len(self.validRefreshRate)):
			self.currentRefreshRate = 0
		
		self.refresh()
		
print "enumeration device test..." 			
nv = Nvidia()
print "enumeration test ok..."

sleep(10)
