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
		self.mode 				= 'h1' # Horizontal Interlacement from 1 px
		self.left 	= self.right = ''
		self.height = self.width = 0
		self.SpecialHardware("on")

	def __del__(self):
		self.SpecialHardware("off")
		print "del int"

	def open(self, path, anaglyph): # TODO Open Anaglyph doesn't work anymore
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
		width 		= self.width + math.fabs(self.vergence)
		height 		= self.height + math.fabs(self.vsep)
		self.stereo = Image.new('RGB', (width,height)) # Final image
		
		i = 0
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
	
	def swap_eyes(self):
		self.left, self.right = self.right, self.left
	
	def resize(self, maxw, maxh):
		if self.height > 0 and self.width > 0:
			if self.height > maxh or self.width > maxw:
				qrh, qrw			= round(self.height / maxh, 6), round(self.width / maxw, 6)
				qrmax 			= max(qrh, qrw)
				height, width 	= math.ceil(self.height / qrmax), math.ceil(self.width / qrmax)
				
				self.right, self.left 	= self.oright, self.oleft  # Backup
				self.right, self.left 	= self.right.resize((width, height), Image.ANTIALIAS), self.left.resize((width, height), Image.ANTIALIAS)
				self.height, self.width = height, width
			else:
				print "resize is no longer needed"
				
	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --INTERLACED') # activate eDimensionnal in Interlaced Mode
		else:
			if self.hardware == 'eDimensionnal':
				exec('edimActivator --OFF')