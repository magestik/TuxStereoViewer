#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG
import Image
import math

class Anaglyph:
	"Anaglyph support class"
	
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0 # Horizontal separation
		self.vsep				= 0 # Vertical separation
		self.hardware 			= '' # Who cares ? :p
		self.mode 				= 'green/purple'
		self.left = self.right = '' # Right and left Images
		self.height = self.width = 0 # Height and Width
	
	def __del__(self):
		print "del ana"
	
	def open(self, path, anaglyph):
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
	
	def make(self, decallage):
		width 		= self.width + math.fabs(self.vergence)
		height 		= self.height + math.fabs(self.vsep)
		self.stereo = Image.new('RGB', (width,height)) # Final image
		
		rg, vg, bg	= self.left.split()
		rd, vd, bd 	= self.right.split()

		if self.mode == "red/cyan":
			source = [rg, vd, bd]
		elif self.mode == "green/purple":
			source = [vg, bd, rd]
		elif self.mode == "blue/yellow":
			source = [bg, rd, vd]
		elif self.mode == "cyan/red":
			source = [vg, bg, rd]
		elif self.mode == "purple/green":
			source = [bg, rg, vd]
		elif self.mode == "yellow/blue":
			source = [rg, vg, bd]
		
		# "R-V", "V-B", "B-R", "V-R", "B-V", "R-B"]

		self.stereo = Image.merge("RGB", source)
		return self.stereo
	
	def resize(self, maxw, maxh):
		try:
			self.right, self.left 	= self.oright, self.oleft  # Backup
			self.right, self.left 	= self.right.resize((maxw, maxh), Image.ANTIALIAS), self.left.resize((maxw, maxh), Image.ANTIALIAS)
			self.height, self.width = maxh, maxw
		except:
			"bug"
			
	def swap_eyes(self):
		self.tempimg 	= self.left
		self.left 		= self.right
		self.right 		= self.tempimg
		self.tempimg 	= ''