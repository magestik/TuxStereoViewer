#!/usr/bin/python
# -*- coding:utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk # For pixbuff conversion

import Image, os
import StringIO, string, binascii

#
# BASIC "OPEN" FUNCTIONS
# 
def set_sources_from_stereo(self, src, ana=False): 
	#if is_anaglyph(src):
	#	return open_anaglyph(src)
	
	if is_mpo(src):
		return open_mpo(src)
		
	else: # Open side-by-side image
		return  open_jps(src)

def set_sources_from_images(self, right, left): # Open 2 images
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

#
# BASIC "SAVE" FUNCTIONS
# 
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
	
#
# BASIC "CONFIG" FUNCTIONS
# 
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
		return 0 
	else:
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


#
# DETECTING AND OPENING ANAGLYPH IMAGES
#
def is_anaglyph(src):
	anaglyphe 	= Image.open(src).convert("RGBA")
	taille 		= anaglyphe.size

	#alpha		= Image.new('L', (taille[0], taille[1])) # needed
	#r, g, b, a 	= anaglyphe.split()
	
	orpix = [pix for pix in list(anaglyphe.getdata())]
	
	i = 0
	matching = 0
	for index, pixel in enumerate(orpix):
		if pixel[1] >= pixel[2]-5 and pixel[1] <= pixel[2]+5:
			matching += 1
		i += 1
		
	print 'Pixels mathing (anaglyph): ', (matching/(i+0.0))*100

def open_anaglyph(src):
	pass

#
# DETECTING AND OPENING MPO IMAGES
#
def is_mpo(src):
	splitsrc = src.split('.')
	extension = splitsrc[len(splitsrc) - 1].upper()
	if extension == "MPO": 
		return True
	else:
		return False

def open_mpo(src):
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
	
	return left, right

#
# DETECTING TYPE AND OPENING STEREO IMAGE
#
def calculate_matches(left, right):
	matching = 0 # number of pixel matching

	if left.size[1] > 200 and left.size[0] > 200: # To speed up the comparaison
		left = left.resize((200,200))
		right = right.resize((200,200))
	
	leftpix = [pix for pix in list(left.getdata())]
	rightpix = [pix for pix in list(right.getdata())]
	
	i = 0
	for index, pixel in enumerate(leftpix):
		score = 0
		
		if pixel[0]-2 <= rightpix[index][0] and pixel[0]+2 >= rightpix[index][0]: # RED
			score += 1
			
		if pixel[1]-2 <= rightpix[index][1] and pixel[1]+2 >= rightpix[index][1]: # GREEN
			score += 1
		
		if pixel[2]-2 <= rightpix[index][2] and pixel[2]+2 >= rightpix[index][2]: # BLUE
			score += 1
		
		if score == 3:
			matching += 1
		
		i += 1
		
	print 'Pixels mathing (jps): ', (matching/(i+0.0))*100
	return (matching/(i+0.0))*100

def open_jps(src):
	jps 	= Image.open(src)
	taille 	= jps.size		
		
	right1 	= Image.new('RGB', (taille[0]/2, taille[1]))
	left1 	= Image.new('RGB', (taille[0]/2, taille[1]))
		
	src = (0, 0, taille[0]/2, taille[1])
	region = jps.crop(src)
	dst = (0, 0, taille[0]/2, taille[1])
	right1.paste(region, dst)
		
	src = (taille[0]/2, 0, taille[0], taille[1])
	region = jps.crop(src)
	dst = (0, 0, taille[0]/2, taille[1])		
	left1.paste(region, dst)
	
	pK1 = calculate_matches(right1, left1)
		
	right2 	= Image.new('RGB', (taille[0], taille[1]/2))
	left2 	= Image.new('RGB', (taille[0], taille[1]/2))
		
	src = (0, 0, taille[0], taille[1]/2)
	region = jps.crop(src)
	dst = (0, 0, taille[0], taille[1]/2)
	right2.paste(region, dst)
		
	src = (0, taille[1]/2, taille[0], taille[1])
	region = jps.crop(src)
	dst = (0, 0, taille[0], taille[1]/2)		
	left2.paste(region, dst)		
		
	pK2 = calculate_matches(right2, left2)
		
	pKmax = max(pK1, pK2)
	if pKmax == pK1:
		return left1, right1
	else:
		return left2, right2
