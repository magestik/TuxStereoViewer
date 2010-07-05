#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG
import Image

class CheckerBoard:
	"Checkerboard support class"
	
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0
		self.hardware 			= '' 
		self.mode 				= ''
	
	def __del__(self):
		print "del checkerboard"
	
	def open(self, path, anaglyph):
		try:
			self.left, self.right 	= self.image.set_sources_from_stereo(path, anaglyph)
			self.oleft, self.oright = self.left, self.right # Back-up
			size = self.left.size
			self.height, self.width = size[1], size[0]
		except:
			print "Image doesn't exist !"
	
	def make(self, decallage):
		self.stereo = Image.new('RGB', (self.width, self.height))
		
		leftpix = self.left.getdata()
		rightpix = self.right.getdata()
		destpix = list(self.stereo.getdata())
		i = 0
		offset = (self.width+1)%2
		while i < len(destpix)-offset:
			if self.width%2 == 0:
				offset = (i//self.width)%2
			if i%2 == 0:
				destpix[i+offset] = leftpix[i]
			else:
				destpix[i+offset] = rightpix[i]
			i = i + 1
		self.stereo.putdata(destpix) 	
		
		return self.stereo