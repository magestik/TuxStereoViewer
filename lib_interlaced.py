#!/usr/bin/python
# -*- coding:utf-8 -*-

import functions
import Image
import math

class Interlaced:
	"Interlaced support class"
	
	def __init__(self):
		self.vergence			= 0 # Horizontal separation
		self.vsep				= 0 # Vertical separation
		self.left 	= self.right = ''
		self.height = self.width = 0
		
		self.conf	= functions.getConfig(self, 'interlaced')
		if self.conf == 0: # default configuration
			self.conf = {}
			self.conf['hardware'] = 'Zalman'
			self.conf['type'] = 'h1' # adaptable
		
		self.SpecialHardware("on")

	def __del__(self):
		functions.saveConfig(self, 'interlaced', self.conf)
		self.SpecialHardware("off")

	def open(self, path, anaglyph=False): # TODO Open Anaglyph doesn't work anymore
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
			
	def make(self, parent, fullscreen):

		
		if self.conf['type'][0] == 'h':
			width 		= self.width + math.fabs(self.vergence)
			height 		= self.height + math.fabs(self.vsep)*2
			self.stereo = Image.new('RGB', (width,height)) # Final image
			self.make_horizontal()
		else:
			width 		= self.width + math.fabs(self.vergence)*2
			height 		= self.height + math.fabs(self.vsep)
			self.stereo = Image.new('RGB', (width,height)) # Final image
			self.make_vertical()
		
		pixbuf = functions.image_to_pixbuf(self, self.stereo)
		if fullscreen == 0:
			parent.stereo.set_from_pixbuf(pixbuf) # Display in normal window
		else:
			parent.fs_image.set_from_pixbuf(pixbuf) # Display in fullscreen window
	
	def make_horizontal(self):
		j = int(self.conf['type'][1]) # Height (in px) of the row
		
		i = 0 # Left or right
		y = 0 # Coordinate
		while i < self.height:
			if i%2 == 0:
				src = (0, y, self.width, y+j)
				region = self.left.crop(src)
				
				if self.vergence < 0:
					CorrectedX = math.fabs(self.vergence)
				else:
					CorrectedX = 0
				
				if self.vsep < 0:
					CorrectedY = math.fabs(self.vsep)*2
				else:
					CorrectedY = 0
				
				dst = (CorrectedX, CorrectedY+y, CorrectedX+self.width, CorrectedY+y+j)
			
			else:
				src = (0, y, self.width, y+j)
				region = self.right.crop(src)
				
				if self.vergence > 0:
					CorrectedX = self.vergence
				else:
					CorrectedX = 0
				
				if self.vsep > 0:
					CorrectedY = math.fabs(self.vsep)*2
				else:
					CorrectedY = 0
				
				dst = (CorrectedX, CorrectedY+y, CorrectedX+self.width, CorrectedY+y+j)
			
			self.stereo.paste(region, dst)
			
			# Incrementation
			i = i + 1
			y = y + j
	
	def make_vertical(self):
		j = int(self.conf['type'][1]) # Width (in px) of the column
		
		i = 0 # Left or right
		x = 0 # Coordinate
		while i < self.width:
			if i%2 == 0:
				src = (x, 0, x+j, self.height)
				region = self.left.crop(src)
				
				if self.vergence < 0:
					CorrectedX = math.fabs(self.vergence)*2
				else:
					CorrectedX = 0
				
				if self.vsep < 0:
					CorrectedY = math.fabs(self.vsep)
				else:
					CorrectedY = 0
				
				dst = (CorrectedX+x, CorrectedY, CorrectedX+x+j, CorrectedY+self.height)
			else:
				src = (x, 0, x+j, self.height)
				region = self.right.crop(src)
				
				if self.vergence > 0:
					CorrectedX = math.fabs(self.vergence)*2
				else:
					CorrectedX = 0
				
				if self.vsep > 0:
					CorrectedY = math.fabs(self.vsep)
				else:
					CorrectedY = 0

				dst = (CorrectedX+x, CorrectedY, CorrectedX+x+j, CorrectedY+self.height)
			
			self.stereo.paste(region, dst)
			i = i + 1
			x = x + j
	
	def swap_eyes(self):
		self.left, self.right = self.right, self.left
	
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
				
	def SpecialHardware(self, go='on'): # Special Hardware actvation
		if go == 'on':
			if self.conf['hardware'] == 'eDimensionnal':
				exec('edimActivator --INTERLACED') # activate eDimensionnal in Interlaced Mode
		else:
			if self.conf['hardware'] == 'eDimensionnal':
				exec('edimActivator --OFF')
