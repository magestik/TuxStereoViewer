#!/usr/bin/python
# -*- coding:utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk # For pixbuff conversion

import Image, os
import StringIO, string, binascii

def getConfig(self, mode):
	path 	=  os.path.expanduser("~") + '/.stereo3D/' + mode + '.conf'
	config = {}
	try:
		file = open(path)
		for line in file.readlines():
			if line.find('=') > 0:
				key, value = line[0:].split(" = ",2)
				config[key] = value.replace('\n', '')
		file.close()
	except:
		config['mode'] = "ANAGLYPH"
		config['type'] = "red/cyan"
		config['eye'] = "LEFT"
		config['hardware'] = "UNKNOW"
		return 0 
	return config

def saveConfig(self, mode, conf):
	dir 	= os.path.expanduser("~") + '/.stereo3D/'
	path 	= dir + mode + '.conf'
	
	toWrite = ''
	for key in conf:
		toWrite = toWrite + key + ' = ' + conf[key] + '\n'

	try:
		if not os.path.exists(dir):
			os.mkdir(home + dir)
			print "Creating configuration files directory"
			
		file = open(path, 'w')
		file.write(toWrite)
		file.close()
	except:
		print "Error while saving config file !"

def set_sources_from_stereo(self, src, ana=False): # Open
	splitsrc = src.split('.')
	extension = splitsrc[len(splitsrc) - 1].upper()
	
	if ana == True: # Open from an Anaglyph image
		anaglyphe 	= Image.open(src)
		taille 		= anaglyphe.size
			
		alpha		= Image.new('L', (taille[0], taille[1])) # needed
		r, v, b 	= anaglyphe.split()

		source	= [alpha, v, b]		
		right 	= Image.merge("RGB", source)
		
		source	= [r, alpha, alpha]
		left		= Image.merge("RGB", source)
	
	elif extension == "MPO": # Open from an MPO file
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
		right 	= Image.open(buff)
		
		# Image 2
		data 	= wanted + files[2]
		buff 	= StringIO.StringIO()
		buff.write(data)
		buff.seek(0)
		left 	= Image.open(buff)
		
	else: # Open side-by-side image			
		jps 	= Image.open(src)
		
		taille 		= jps.size		
		right = Image.new('RGB', (taille[0]/2, taille[1]))
		left = Image.new('RGB', (taille[0]/2, taille[1]))
		
		src = (0, 0, taille[0]/2, taille[1])
		region = jps.crop(src)
		dst = (0, 0, taille[0]/2, taille[1])
		right.paste(region, dst)
		
		src = (taille[0]/2, 0, taille[0], taille[1])
		region = jps.crop(src)
		dst = (0, 0, taille[0]/2, taille[1])		
		left.paste(region, dst)

	return [right, left]

def set_sources_from_images(self, right, left): # Open
	right, left 		= Image.open(right), Image.open(left)
	taille, taille2	= right.size, left.size
	
	if (taille[0] == taille2[0]) and (taille[1] == taille2[1]): # Check images size
		self.height, self.width = taille[1], taille[0]
		return [right, left]
	else:
		return False

def image_to_pixbuf(self, image):
	fd = StringIO.StringIO()
	image.save(fd, "ppm")
	contents = fd.getvalue()
	fd.close()
	loader = gtk.gdk.PixbufLoader("pnm")
	loader.write(contents, len(contents))
	pixbuf = loader.get_pixbuf()
	loader.close()
	return pixbuf

def make_leftright(self, decallage): # Save
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

def make_topbottom(self, decallage): # Save
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