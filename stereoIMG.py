#!/usr/bin/python
# -*- coding:utf-8 -*-

#
# Module de transformation 3D
# JPS -> Interlaced
# JPS -> Anaglyph
#

import Image
import string, binascii, StringIO, math

class stereoIMG:
	#
	# Fonction d'aquisition d'une source stereo (2 vues en une image)
	#
	def set_sources_from_stereo(self,src,ana=False): 
		splitsrc = src.split('.')
		extension = splitsrc[len(splitsrc) - 1].upper()
		self.ana = False
		
		if ana == True: # utilisation d'une image anaglyphe
			# *** Methode:
			# On va séparer les couleurs de l'image anaglyphe.
			# La composante rouge formera la vue droite, alors que le cyan (vert+bleu) formera la gauche.
			
			anaglype 	= Image.open(src)
			self.ana 	= True
			taille 		= anaglype.size
			self.height, self.width = taille[1], taille[0]
			
			alpha 		= Image.new('L', (self.width,self.height)) # needed
			r, v, b 		= anaglype.split()
			
			# Gauche
			source 		= [alpha, v, b]		
			self.right 	= Image.merge("RGB", source) # cyan
			
			# Droite
			source 		= [r, alpha, alpha]
			self.left	= Image.merge("RGB", source) # rouge
			
			self.oright, self.oleft = self.right, self.left # servira pour le zoom/dezoom
						

			return True
		
		elif extension == "MPO": # utilisation d'une image stereo MPO
			# *** Methode:
			# On split l'hexadecimal à la limite entre les deux images.
			# Chacun des deux cotés de cette limite est l'hexa d'un image.
						
			binaryFile 	= open(src, mode='rb')
			string 		= binaryFile.read()
			binaryFile.close()
			
			wanted 	= binascii.unhexlify('FFD8FFE1')
			files 	= string.split(wanted)
			
			# Image 1
			data 	= wanted + files[1]
			buff 	= StringIO.StringIO()
			buff.write(data)
			buff.seek(0)
			self.right 	= Image.open(buff)
			
			# Image 2
			data 	= wanted + files[2]
			buff 	= StringIO.StringIO()
			buff.write(data)
			buff.seek(0)
			self.left 	= Image.open(buff)

			self.oright, self.oleft = self.right, self.left  # servira pour le zoom/dezoom
			
			taille 		= self.right.size
			self.height, self.width = taille[1], taille[0]
			
		else: # utilisation d'une image stereo normale (JPS ...)
			# *** Methode:
			# L'image est une grande image constitué de deux images.
			# La vue droite se trouve sur la première moitié ...
			
			self.jps 	= Image.open(src)
			#self.ojps 	= self.jps # servira pour le zoom/dezoom
			taille 		= self.jps.size
			self.height, self.width = taille[1], taille[0]/2
			
			self.right = Image.new('RGB', (taille[0]/2, taille[1]))
			self.left = Image.new('RGB', (taille[0]/2, taille[1]))
			
			src = (0, 0, taille[0]/2, taille[1])
			region = self.jps.crop(src)
			dst = (0, 0, taille[0]/2, taille[1])
			self.right.paste(region, dst)
			
			src = (taille[0]/2, 0, taille[0], taille[1])
			region = self.jps.crop(src)
			dst = (0, 0, taille[0]/2, taille[1])		
			self.left.paste(region, dst)
			
			self.oright, self.oleft = self.right, self.left  # servira pour le zoom/dezoom
			self.jps = None
			return True
		
	#
	# Fonction d'aquisition de deux sources (une vue par image)
	#
	def set_sources_from_images(self, right, left): # utilisation de deux images
		self.ana 	= False
		self.right, self.left 	= Image.open(right), Image.open(left)
		self.oright, self.oleft = self.right, self.left  # servira pour le zoom/dezoom
		taille, taille2 			= self.right.size, self.left.size
		# On verifie que les images ont la meme taille
		if (taille[0] == taille2[0]) and (taille[1] == taille2[1]):
			self.height, self.width = taille[1], taille[0]
			return True
		else:
			return False

	def swap_eyes(self):
		self.tempimg 	= self.left
		self.left 		= self.right
		self.right 		= self.tempimg
		self.tempimg 	= ''

	#
	# Fonction de lancement de la creation d'une image stereoscopique
	#
	def make_stereo(self, maxwidth, maxheight, decallage, mode=None, force=0, normale=0):
		if normale == 1: # Taille normale
			self.right, self.left = self.oright, self.oleft # back-up
			taille 		= self.right.size
			self.height, self.width = taille[1], taille[0]				
		else: # Redimensionnement
			if force == 1:
				taille = self.right.size
				self.height, self.width = taille[1], taille[0]

			#Reglage de la taille de l'image (zoom/dezoom)
			if maxwidth < self.width or maxheight < self.height:
				if maxwidth < self.width:
					prop1 = self.width / (maxwidth + 0.00000)
				else:
					prop1 = 0
			
				if maxheight < self.height:
					prop2 = self.height / maxheight 
				else:
					prop2 = 0
		
				prop = max(prop1, prop2)
		
				if prop > 0:
					newh = int( math.floor( self.width/prop ) )
					neww = int( math.floor( self.height/prop ) )
					print "Resize: ", neww, newh
					self.resize_sources(newh, neww)
		
		# Reglage des effets 3D (dacallage verticale)
		width = self.width + math.fabs(decallage)
		
		self.stereo = Image.new('RGB', (width,self.height)) # Image Finale
		
		#if (self.width > maxwidth) or (self.height > maxheight):
		#	self.resize_image(maxwidth,maxheight)
		
		#rendering = self.get_mode()
		
		if mode == "INTERLACED":
			rep = self.make_interlaced(decallage)
			return rep # True or False
		elif mode == "ANAGLYPH":
			rep = self.make_anaglyph(decallage)
			return rep # True or False
		elif mode == "HSYNC":
			rep = self.make_leftright(decallage)
			return rep
		elif mode == "VSYNC":
			rep = self.make_topbottom(decallage)
			return rep
		elif mode == "CHECKERBOARD":
			rep = self.make_checkerboard(decallage)
			return rep
		elif mode == "DUALOUTPUT":
			return True
		else:
			print "Aucun mode de rendu"
			return False
	
	#
	# Fonction de creation d'une image S-3D, mode entrelacee
	# (Doit etre appellee depuis make_stereo)
	#
	def make_interlaced(self, decallage):
		if self.ana == True:
			self.right, self.left 	= self.right.convert("L"), self.left.convert("L")

			
		i = 0 # on commence a zero
		while i < self.height:
			self.copyPaste(i, decallage)
			i = i + 1
		return True

	def make_checkerboard(self, decallage):
		if self.ana == True:
			self.right, self.left 	= self.right.convert("L"), self.left.convert("L")
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
		return True

	

	def make_leftright(self, decallage):
		if self.ana == True:
			self.right, self.left 	= self.right.convert("L"), self.left.convert("L")
		self.stereo = Image.new('RGB', ((self.width * 2) + decallage,self.height))
		print "Destination image size = ", self.width * 2, "x", self.height
		src = (0, 0, self.width, self.height)
		region = self.left.crop(src)
		dst = (0, 0, self.width, self.height)
		print "Cropping left, source region = ", src
		print "Dest region = ",dst
		self.stereo.paste(region, dst)
		print "Pasted left"
		src = (0, 0, self.width, self.height)	
		region = self.right.crop(src)
		dst = (self.width+decallage, 0, (self.width * 2)+decallage, self.height)
		print "Cropping right, source region = ", src
		print "Dest region = ",dst
		self.stereo.paste(region, dst)
		print "Pasted right"
		return True


	def make_topbottom(self, decallage):
		if self.ana == True:
			self.right, self.left 	= self.right.convert("L"), self.left.convert("L")
		self.stereo = Image.new('RGB', (self.width + decallage, (self.height * 2)+self.vsep))
		print "Destination image size = ", self.width, "x", self.height * 2
		src = (0, 0, self.width, self.height)
		region = self.left.crop(src)
		dst = (0, 0, self.width, self.height)
		print "Cropping left, source region = ", src
		print "Dest region = ",dst
		self.stereo.paste(region, dst)
		print "Pasted left"
		src = (0, 0, self.width, self.height)	
		region = self.right.crop(src)
		dst = (decallage, self.height+self.vsep, self.width+decallage, (self.height * 2)+self.vsep)
		print "Cropping right, source region = ", src
		print "Dest region = ",dst
		self.stereo.paste(region, dst)
		print "Pasted right"
		return True
	#
	# Fonction de creation d'une image S-3D, mode anaglyphe
	# (Doit etre appellee depuis make_stereo)
	#
	def make_anaglyph(self, decallage):
		if self.ana == True:
			self.right, self.left 	= self.oright, self.oleft
		
		# better with an array [0], [1], [2]
		rg, vg, bg 	= self.left.split() # Left = Red
		rd, vd, bd 	= self.right.split() # Right = Cyan

		# rouge/cyan, vert/violet, bleu/orange; rouge/vert, vert/bleu, bleu/rouge
		modes = ["R-VB", "V-BR", "B-RV", "R-V", "V-B", "B-R",
					"VB-R", "BR-V", "RV-B", "V-R", "B-V", "R-B"]

		source 		= [rg, vd, bd]
		self.stereo = Image.merge("RGB", source)
	
	#
	# Fonction servant a prendre une ligne sur la source, pour le coller sur le rendu final
	# (Doit etre appellee depuis make_interlaced)
	#
	def copyPaste(self, row, decallage):
		### Copiage
		
		# --- Lignes Paires
		if row%2 == 0:
			src = (0, row, self.width, row+1)
			region = self.left.crop(src)
			dst = (0, row, self.width, row+1)
			
		# --- Lignes Impaires
		else:
			src = (0, row, self.width, row+1)
			region = self.right.crop(src)
			dst = (math.fabs(decallage), row, self.width+math.fabs(decallage), row+1)
		
		### Collage
		self.stereo.paste(region, dst)

		
	#
	# Fonction de renvoie de l'image
	#	
	def get_image(self):
		return self.stereo
		
	def get_images(self):
		images = [self.left, self.right]
		return images
	
	#
	# Fonction de redimensionnement
	#
	def resize_sources(self, width, height):
		self.right, self.left = self.oright, self.oleft  # Backup
		self.right, self.left = self.right.resize((width, height), Image.ANTIALIAS), self.left.resize((width, height), Image.ANTIALIAS)
		self.width, self.height = width, height