#!/usr/bin/python
# -*- coding:utf-8 -*-

import functions
import Image
import math, time

from threading import dbus
import gobject
gobject.threads_init() # For prevent GTK freeze

import dbus

class controller(Thread):
	def __init__(self, shutters, interface, left, right, rate):
		Thread.__init__(self)
		# Display variables
		self.canvas = interface
		self.left 	= left
		self.right 	= right
		self.rate	= rate
		self.quit 	= False
	
	def loop(self):
		start = shutters.get_dbus_method('start', 'org.stereo3d.shutters')
		swap = shutters.get_dbus_method('swap', 'org.stereo3d.shutters')
		stop = shutters.get_dbus_method('stop', 'org.stereo3d.shutters')
		
		start() # starting the USB IR emitter
		
		i 		= 0
		eye 	= 0
		count 	= 0
		timeout = (1. / self.rate)
		marge 	= 0.008 * timeout # 0.8% d'erreur
		while not self.quit:
			if count == 0:
				c0 = time.time()
			count = count + 1
			
			t1 = time.time()
			
			if(i == 0):
				eye = swap('left')
				self.canvas.set_from_pixbuf(self.left) # Display
				i = 1
			else:
				eye = swap('right')
				self.canvas.set_from_pixbuf(self.right) # Display
				i = 0
			
			delay = timeout - marge - time.time() + t1 
			if delay > 0:
				time.sleep(delay)
			
			if count == self.rate:
				print time.time() - c0
				count = 0
		
		stop() # stopping the USB IR emitter
		
	def run(self):
		self.loop()

class Shutter:
	"Shutter Glasses support class"
	
	def __init__(self):	
		self.vergence			= 0  # Horizontal separation
		self.vsep				= 0  # Vertical separation
		self.left 	= self.right = '' # Right and left Images
		self.height = self.width = 0  # Height and Width
		
		self.conf	= functions.getConfig(self, 'shutter')
		if self.conf == 0: # default configuration
			self.conf = {}
			self.conf['hardware'] = 'Nvidia3D' # OR eDimensionnal
			self.conf['rate'] 	= '60'
		
		self.SpecialHardware("off")
		
	def __del__(self):
		functions.saveConfig(self, 'shutter', self.conf)
		self.RefreshControl.quit = True
	
	def open(self, path, anaglyph=False):
		try:
			self.left, self.right 	= functions.set_sources_from_stereo(self, path, anaglyph)
			self.oleft, self.oright = self.left, self.right # Back-up
			size = self.left.size
			self.height, self.width = size[1], size[0]
		except:
			print "Image doesn't exist !"
	
	def open2(self, path='None', image='None'):
		 if path != 'None':
		 	functions.set_sources_from_images(self, path[0], path[1])
		 elif image[0] != '':
		 	self.left, self.right 	= image[0], image[1]
			self.oleft, self.oright = image[0], image[1] # Back-up
			taille = self.right.size
			self.height, self.width = taille[1], taille[0]

	def make(self, parent, fullscreen):
		left 	= functions.image_to_pixbuf(self, self.left)
		right 	= functions.image_to_pixbuf(self, self.right)
		
		try:
			bus = dbus.SessionBus()
			shutters = bus.get_object('org.stereo3d.shutters', '/org/stereo3d/shutters')
			self.RefreshControl = controller(parent.stereo, shutters, left, right, int(self.conf['rate']))
		except:
			print "Can't connect to the daemon !" # GTK POP-UP ?
		else:
			self.RefreshControl.start()
		
	def swap_eyes(self):
		self.left, self.right = self.right, self.left
	
	def resize(self, maxw, maxh, force=0, normal=0):
		if normal == 1: # Scale 1:1
			self.right, self.left 	= self.oright, self.oleft  # Backup
			taille = self.right.size
			self.height, self.width = taille[1], taille[0]
		
		elif self.height > 0 and self.width > 0:
			if self.height > maxh or self.width > maxw or force == 1:
				qrh, qrw			= (self.height + 0.00000000) / maxh, (self.width + 0.00000000) / maxw
				qrmax 			= max(qrh, qrw)
				height, width 	= int(math.ceil(self.height / qrmax)), int(math.ceil(self.width / qrmax))
				
				self.right, self.left 	= self.oright, self.oleft  # Backup
				self.right, self.left 	= self.right.resize((width, height), Image.ANTIALIAS), self.left.resize((width, height), Image.ANTIALIAS)
				self.height, self.width = height, width
