#!/usr/bin/python
# -*- coding:utf-8 -*-

import functions
import Image
import math, time

from threading import Thread
import gobject
gobject.threads_init() # For prevent GTK freeze

import socket

class controller(Thread):
	def __init__(self, interface, left, right, rate):
		Thread.__init__(self)
		# Display variables
		self.canvas = interface
		self.left 	= left
		self.right 	= right
		self.rate	= rate
		self.quit 	= False
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(("localhost", 5000))

	def loop(self):
		i 	= 0
		eye = 0
		count = 0
		while not self.quit:
			if count == 0:
				c0 = time.time()
			count = count + 1
			
			t1 = time.time()
			
			if(i == 0):
				self.socket.send('L')
				self.canvas.set_from_pixbuf(self.left) # Display
				i = 1
			else:
				self.socket.send('R')
				self.canvas.set_from_pixbuf(self.right) # Display
				i = 0
			
			delay = (1./self.rate) - time.time() + t1
			if delay > 0:
				time.sleep(delay)
			
			if count == 120:
				print time.time() - c0
				count = 0
		# Escaping from the loop
		self.socket.send('q') # Tell the daemon we are going to quit
		self.socket.close() # Quit
		
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
			self.conf['rate'] 	= '120'
		
		self.SpecialHardware("off")
		
	def __del__(self):
		functions.saveConfig(self, 'shutter', self.conf)
		self.RefreshControl.quit = True
		#self.SpecialHardware("off") # Shut Down Special Hardware
		# exec("Genlock --off")
	
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
		
		self.RefreshControl = controller(parent.stereo, left, right, int(self.conf['rate']))
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

	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.conf['hardware'] == 'eDimensionnal':
				exec('edimActivator --SHUTTER') # activate eDimensionnal in Shutter Mode
		else:
			if self.conf['hardware'] == 'eDimensionnal':
				exec('edimActivator --OFF')
