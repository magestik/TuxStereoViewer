#!/usr/bin/python
# -*- coding:utf-8 -*-

import functions
import Image
import math

class Interlaced:
	"Interlaced support class"
	
	def __init__(self):
		self.vergence			= 0 # Horizontal separation
		self.vsep				= 0 # Vertical separation
		self.left 	= self.right = ''
		self.height = self.width = 0
		
		self.conf	= functions.getConfig(self, 'interlaced')
		if self.conf == 0: # default configuration
			self.conf = {}
			self.conf['hardware'] = 'Zalman' # OR  IZ3D
			self.conf['type'] = 'h1' # adaptable
		
		self.SpecialHardware("on")

	def __del__(self):
		functions.saveConfig(self, 'interlaced', self.conf)
		self.SpecialHardware("off")

	def open(self, path, anaglyph=False): # TODO Open Anaglyph doesn't work anymore
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
			
	def make(self):
		width 		= self.width + math.fabs(self.vergence)
		height 		= self.height + math.fabs(self.vsep)
		self.stereo = Image.new('RGB', (width,height)) # Final image
		
		i = 0
		while i < self.height:
			self.copyPaste(i, self.vergence)
			i = i + 1
		return self.stereo
	
	def copyPaste(self, row, decallage):	
		if row%2 == 0:
			src = (0, row, self.width, row+1)
			region = self.left.crop(src)
			dst = (0, row, self.width, row+1)
		else:
			src = (0, row, self.width, row+1)
			region = self.right.crop(src)
			dst = (math.fabs(decallage), row, self.width+math.fabs(decallage), row+1)

		self.stereo.paste(region, dst)
	
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
				exec('edimActivator --INTERLACED') # activate eDimensionnal in Interlaced Mode
		else:
			if self.conf['hardware'] == 'eDimensionnal':
				exec('edimActivator --OFF')