#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class Interlaced:
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.max_img_height 	= 1680
		self.max_img_width	= 1050
		self.vergence			= 0
		self.hardware 			= '' # Zalman, iZ3D ...
		self.mode 				= 'h1' # Horizontal 1 ; TODO hx and Vertical interlacement...
		
	def make(self):
		self.image.make_stereo(self.max_img_height, self.max_img_width, self.vergence, 'INTERLACED')
		self.SpecialHardware()
		return self.image.get_image()

	def SpecialHardware(self): # Special Hardware actvation
		if self.hardware == 'eDimensionnal':
			exec('edimActivator --INTERLACED') # activate eDimensionnal in Interlaced Mode