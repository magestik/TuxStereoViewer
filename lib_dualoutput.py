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
	
	def __del__(self):
		self.SpecialHardware("off") # Shut Down Special Hardware
		print "del dual"
		
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
		return [self.left, self.right]
	
	def swap_eyes(self):
		self.left, self.right = self.right, self.left
					
	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --DUALOUTPUT') # activate eDimensionnal in Side-by-side Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')