#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG
import Image
import math

class Interlaced:
	"Interlaced support class"
	
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0 # Horizontal separation
		self.vsep				= 0 # Vertical separation
		self.hardware 			= '' # Zalman, iZ3D ...
		self.mode 				= 'h1' # Horizontal 1 ; TODO hx and Vertical interlacement...
		self.left = self.right = '' # Right and left Images
		
	def __del__(self):
		self.SpecialHardware("off") # Shut Down Special Hardware
		print "del int"

	def open(self, path, anaglyph):
		self.left, self.right 	= self.image.set_sources_from_stereo(path, anaglyph)
		try:
			
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
		width 		= self.width + math.fabs(self.vergence)
		height 		= self.height + math.fabs(self.vsep)
		self.stereo = Image.new('RGB', (width,height)) # Final image
		
		i = 0
		while i < self.height:
			self.copyPaste(i, self.vergence)
			i = i + 1

		self.SpecialHardware()
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
		
	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --INTERLACED') # activate eDimensionnal in Interlaced Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')