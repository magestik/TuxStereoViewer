#!/usr/bin/python
# -*- coding:utf-8 -*-

import Image
import string, binascii, StringIO, math

class stereoIMG:
	def image_to_pixbuf(self,image):
		fd = StringIO.StringIO()
		image.save(fd, "ppm")
		contents = fd.getvalue()
		fd.close()
		loader = gtk.gdk.PixbufLoader("pnm")
		loader.write(contents, len(contents))
		pixbuf = loader.get_pixbuf()
		loader.close()
		return pixbuf
	
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
			
			anaglyphe 	= Image.open(src)
			self.ana 	= True
			taille 		= anaglyphe.size
			self.height, self.width = taille[1], taille[0]
			
			alpha 		= Image.new('L', (self.width,self.height)) # needed
			r, v, b 		= anaglyphe.split()
			
			# Gauche
			source 		= [alpha, v, b]		
			self.right 	= Image.merge("RGB", source) # cyan
			
			# Droite
			source 		= [r, alpha, alpha]
			self.left	= Image.merge("RGB", source) # rouge
		
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
			self.jps = None
		return [self.right, self.left]
		
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
		
		# Reglage des effets 3D (decallage verticale)
		width = self.width + math.fabs(decallage)
		
		self.stereo = Image.new('RGB', (width,self.height)) # Image Finale
		
		#if (self.width > maxwidth) or (self.height > maxheight):
		#	self.resize_image(maxwidth,maxheight)
		
		#rendering = self.get_mode()

		if mode == "HSYNC":
			rep = self.make_leftright(decallage)
			return rep
		elif mode == "VSYNC":
			rep = self.make_topbottom(decallage)
			return rep
		else:
			print "Aucun mode de rendu"
			return False

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
	# Fonction de redimensionnement
	#
	def resize_sources(self, width, height):
		self.right, self.left = self.oright, self.oleft  # Backup
		self.right, self.left = self.right.resize((width, height), Image.ANTIALIAS), self.left.resize((width, height), Image.ANTIALIAS)
		self.width, self.height = width, height