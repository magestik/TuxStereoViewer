#!/usr/bin/python
# -*- coding:utf-8 -*-

import stereoIMG
import Image

class Anaglyph:
	"Anaglyph support class"
	
	def __init__(self):
		self.image 				= stereoIMG.stereoIMG()
		self.vergence			= 0
		self.hardware 			= '' # Who cares ? :p
		self.mode 				= 'green/purple'
	
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
	
	def make(self, decallage):
		self.stereo = Image.new('RGB', (self.width,self.height)) # Image Finale
		
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