#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG

class Anaglyph:
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.max_img_height 	= 1680
		self.max_img_width	= 1050
		self.vergence			= 0
		self.hardware 			= '' # Who cares ? :p
		self.mode 				= 'red/cyan'
		
	def make(self):
		self.image.make_stereo(self.max_img_height, self.max_img_width, self.vergence, 'ANAGLYPH')
		return self.image.get_image()