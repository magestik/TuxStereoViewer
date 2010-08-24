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
		self.currentRefreshRate	= self.validRefreshRate[0]
		self.eye				= 'left'
		
		busses = usb.busses()
		self.device = self.findDevice(busses, 0x000c, 0x0555)
		# self.device = usb.core.find(idVendor=0955, idProduct=0007) pyUSB 1.0

		if self.device is None:
			print "enumeration test failed..." 
			sys.exit(1) 
			raise ValueError('Nvidia 3D Vision not detected')
		
		self.device.set_configuration() # set the active configuration. With no arguments, the first configuration will be the active one
		#self.getEndpoint()
	
	def findDevice(self, busses, idProduct, idVendor):
		for bus in busses:
			for dev in bus.devices:
				if dev.idProduct == idProduct and dev.idVendor == idVendor:
					return dev

print "enumeration device test..." 			
nv = Nvidia()
print "enumeration test ok..."

sleep(10)
