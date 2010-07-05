#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class Shutter:
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.max_img_height 	= 1680
		self.max_img_width	= 1050
		self.vergence			= 0
		self.hardware 			= '' # eDim, nvidia 3D Vision ...
		self.mode 				= 'left/right'

	def make(self):
		self.image.make_stereo(self.max_img_height, self.max_img_width, self.vergence, 'DUAL-OUTPUT')
		# exec('genlock')
		self.SpecialHardware()
		return self.image.get_images()

	def SpecialHardware(self): # Special Hardware actvation
		if self.hardware == 'eDimensionnal':
			exec('edimActivator --SHUTTER') # activate eDimensionnal in Shutter Mode