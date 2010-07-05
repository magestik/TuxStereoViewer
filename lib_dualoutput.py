#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class DualOutput:
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.max_img_height 	= 1680
		self.max_img_width	= 1050
		self.vergence			= 0
		self.hardware 			= '' # planar, eDim, projectors ...
		self.mode 				= 'left/right'
		 
	def make(self):
		self.image.make_stereo(self.max_img_height, self.max_img_width, self.vergence, 'DUAL-OUTPUT')
		self.SpecialHardware()
		return self.image.get_images() # two images
			
	def SpecialHardware(self): # Special Hardware actvation
		if self.hardware == 'eDimensionnal':
			exec('edimActivator --DUAL '+ self.mode) # activate eDimensionnal in Sie-By-Side Mode