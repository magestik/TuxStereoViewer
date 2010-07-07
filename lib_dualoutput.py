#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class DualOutput:
	"DualOutput support class"

	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0 # Horizontal separation
		self.vsep				= 0 # Vertical separation
		self.hardware 			= '' # planar, eDim, projectors ...
		self.mode 				= 'left/right'
		self.left = self.right = '' # Right and left Images
		self.height = self.width = 0 # Height and Width
		self.SpecialHardware("on")
		
	def __del__(self):
		self.SpecialHardware("off") # Shut Down Special Hardware
		print "del dual"
		
	def open(self, path, anaglyph=False):
		try:
			self.left, self.right 	= self.image.set_sources_from_stereo(path, anaglyph)
			self.oleft, self.oright = self.left, self.right # Back-up
			size = self.left.size
			self.height, self.width = size[1], size[0]
		except:
			print "Image doesn't exist !"
	
	def open2(self, path='None', image='None'):
		 if path != 'None':
		 	self.image.set_sources_from_images(path[0], path[1])
		 elif image[0] != '':
		 	self.left, self.right 	= image[0], image[1]
			self.oleft, self.oright = image[0], image[1] # Back-up
			taille = self.right.size
			self.height, self.width = taille[1], taille[0]
					 
	def make(self):
		return [self.left, self.right]
	
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
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --DUALOUTPUT') # activate eDimensionnal in Side-by-side Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')