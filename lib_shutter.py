#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class Shutter:
	"Shutter Glasses support class"
	
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0  # Horizontal separation
		self.vsep				= 0  # Vertical separation
		self.hardware 			= '' # eDim, nvidia 3D Vision ...
		self.mode 				= 'left/right'
		self.left 	= self.right = '' # Right and left Images
		self.height = self.width = 0  # Height and Width
		self.SpecialHardware("off")
		
	def __del__(self):
		self.SpecialHardware("off") # Shut Down Special Hardware
		# exec("Genlock --off")
		print "del shutter"
	
	def open(self, path, anaglyph):
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

	def make(self, size):
		# exec("Genlock --on")
		return [self.left, self.right]
	
	def swap_eyes(self):
		self.left, self.right = self.right, self.left
	
	def resize(self, maxw, maxh):
		try:
			self.right, self.left 	= self.oright, self.oleft  # Backup
			self.right, self.left 	= self.right.resize((maxw, maxh), Image.ANTIALIAS), self.left.resize((maxw, maxh), Image.ANTIALIAS)
			self.height, self.width = maxh, maxw
		except:
			"bug"

	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --SHUTTER') # activate eDimensionnal in Shutter Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')