#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class DualOutput:
	"DualOutput support class"

	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0
		self.hardware 			= '' # planar, eDim, projectors ...
		self.mode 				= 'left/right'
	
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
		 
	def make(self, size):
		return [self.left, self.right]
			
	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --DUALOUTPUT') # activate eDimensionnal in Side-by-side Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')