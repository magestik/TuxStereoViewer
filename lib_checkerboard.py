#!/usr/bin/python
# -*- coding:utf-8 -*-

import functions
import Image
import math

class CheckerBoard:
	"Checkerboard support class"
	
	def __init__(self):
		self.vergence			= 0 # Horizontal separation
		self.vsep				= 0 # Vertical separation
		self.left 	= self.right = '' # Right and left Images
		self.height = self.width = 0 # Height and Width
		
		self.conf	= functions.getConfig(self, 'checkerboard')
		if self.conf == 0: # default configuration
			self.conf = {}
			self.conf['hardware'] = '3DTV'
			
	def __del__(self):
		functions.saveConfig(self, 'checkerboard', self.conf)
	
	def open(self, path, anaglyph=False):
		try:
			self.left, self.right 	= functions.set_sources_from_stereo(self, path, anaglyph)
			self.oleft, self.oright = self.left, self.right # Back-up
			size = self.left.size
			self.height, self.width = size[1], size[0]
		except:
			print "Image doesn't exist !"
	
	def open2(self, path='None', image='None'):
		 if path != 'None':
		 	functions.set_sources_from_images(self, path[0], path[1])
		 elif image[0] != '':
		 	self.left, self.right 	= image[0], image[1]
			self.oleft, self.oright = image[0], image[1] # Back-up
			taille = self.right.size
			self.height, self.width = taille[1], taille[0]

	def make(self):
		width 		= self.width + math.fabs(self.vergence)
		height 		= self.height + math.fabs(self.vsep)
		self.stereo = Image.new('RGB', (width,height)) # Final image
		
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
	
	def resize(self, maxw, maxh, force=0, normal=0):
		if normal == 1: # Scale 1:1
			self.right, self.left 	= self.oright, self.oleft  # Backup
			taille = self.right.size
			self.height, self.width = taille[1], taille[0]
		
		elif self.height > 0 and self.width > 0:
			if self.height > maxh or self.width > maxw or force == 1:
				qrh, qrw			= (self.height + 0.00000000) / maxh, (self.width + 0.00000000) / maxw
				qrmax 			= max(qrh, qrw)
				height, width 	= int(math.ceil(self.height / qrmax)), int(math.ceil(self.width / qrmax))
				
				self.right, self.left 	= self.oright, self.oleft  # Backup
				self.right, self.left 	= self.right.resize((width, height), Image.ANTIALIAS), self.left.resize((width, height), Image.ANTIALIAS)
				self.height, self.width = height, width
				
	def swap_eyes(self):
		self.left, self.right = self.right, self.left