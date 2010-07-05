#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG
import Image
import math

class Interlaced:
	"Interlaced support class"
	
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0
		self.hardware 			= '' # Zalman, iZ3D ...
		self.mode 				= 'h1' # Horizontal 1 ; TODO hx and Vertical interlacement...
		# Special Hardware here ?
		
	def __del__(self):
		self.SpecialHardware("off") # Shut Down Special Hardware
		print "del int"

	def open(self, path, anaglyph):
		try:
			self.left, self.right 	= self.image.set_sources_from_stereo(path, anaglyph)
			self.oleft, self.oright = self.left, self.right # Back-up
			size = self.left.size
			self.height, self.width = size[1], size[0]
		except:
			print "Image doesn't exist !"

	def make(self, size):
		self.stereo = Image.new('RGB', (self.width,self.height)) # Image Finale
		
		i = 0 # on commence a zero
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

	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --INTERLACED') # activate eDimensionnal in Interlaced Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')