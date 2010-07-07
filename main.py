#!/usr/bin/python
# -*- coding:utf-8 -*-

try:
	import psyco
	psyco.full();
	print "Psyco is installed."
except:
	print "Psyco isn't installed."

import pygtk
pygtk.require('2.0')
import gtk

import StringIO, sys, os, glob, getopt, time, string

class GUI:	
	def main(self): # Main loop
		gtk.main()
		return 0
	
	def __init__(self, fopen):
		self.interface = gtk.Builder()
		self.interface.add_from_file(sys.path[0] + '/interface-v0.3.glade')

		self.window = self.interface.get_object("main")
		self.window.set_title("Tux stereo Viewer")
		self.window.set_icon( gtk.gdk.pixbuf_new_from_file('/usr/share/pixmaps/TuxStereoViewer-icon.png') )
		self.window.maximize()
		
		self.window.connect("destroy", self.destroy)
		self.window.connect("delete_event", self.delete_event)
		
		self.max_height = self.max_width = 0
		self.src_info			= os.path.split(fopen)
		self.window_mode 		= 0 # 1 = Fullscren ; 0 = Windowed
		self.zoom_percent		= 0 # Zoom (in %)
		self.vergence 			= 0 # Vergence (in px)
		self.flag 				= False
		self.lib 				= False
		self.getConfig()
		
		self.stereo = self.interface.get_object("stereo") # Where goes the image
		
		# - Menus
		self.about_dialog 	= self.interface.get_object("about")
		self.options_dialog 	= self.interface.get_object("options")
		
		# - Dual Output
		self.doright 					= self.interface.get_object("do-right")
		self.doleft 					= self.interface.get_object("do-left")
		self.dualoutput_window 		= self.interface.get_object("dualoutputWindow")
		
		# - Switching menus
		self.re_menu 		= self.interface.get_object("right_eye_menu")
		self.le_menu 		= self.interface.get_object("left_eye_menu")

		self.imode_menu	= self.interface.get_object("inter_mode_menu")
		self.domode_menu	= self.interface.get_object("dualout_mode_menu")
		self.amode_menu	= self.interface.get_object("ana_mode_menu")
		self.smode_menu	= self.interface.get_object("shutter_mode_menu")
		self.cbmode_menu	= self.interface.get_object("checkerboard_menu")
		# self.tbmode_menu	= self.interface.get_object("top_bottom_menu")
		# self.lrmode_menu	= self.interface.get_object("left_right_menu")
		
		self.set_mode( self.conf['mode'] )
		self.set_eye( self.conf['eye'] )

		self.interface.connect_signals(self)
		self.window.show()
		
		if fopen != "None":
			self.img.open(fopen)
			self.modify_image()
		
	def onSizeAllocate(self, win, alloc):
		self.max_height 	= alloc[3] - alloc[1]
		self.max_width 	= alloc[2] - alloc[0]
		
	#
	# # Configurations functions
	#	
	def saveConfig(self):
		home 	= os.path.expanduser("~")
		dir   = '/.stereo3D/'
		name 	= 'general.conf'
		path =  home + dir + name
		file = ''
		for key in self.conf:
			file = file + key + ' = ' + self.conf[key] + '\n'

		try:
			if not os.path.exists(home + dir):
				os.mkdir(home + dir)
				print "creating configuration files directory"
			
			conf = open(path, 'w')
			conf.write(file)
			conf.close()
		except:
			print "Error while saving config file !"

	def getConfig(self):
		home 	= os.path.expanduser("~")
		dir   = '/.stereo3D/'
		name 	= 'general.conf'
		path =  home + dir + name
		self.conf = {}
		try:
			conf = open(path)
			for line in conf.readlines():
				if line.find('=') > 0:
					key, value = line[0:].split(" = ",2)
					self.conf[key] = value.replace('\n', '')
			conf.close()
		except:
			self.conf['mode'] = "ANAGLYPH"
			self.conf['type'] = "red/cyan"
			self.conf['eye'] = "LEFT"
			print "Error while parsing config file !"
		print self.conf

	#
	# # Close functions
	#
	def delete_event(self, widget, event=None, data=None): # Clean Closing
		print "Delete event"
		self.img.__del__()
		self.saveConfig()
		gtk.timeout_add(100, gtk.main_quit)
		return True # Do not allow OS to destroy we will kill ourselves in due time

	def destroy(self, widget, data=None): # Closing
		print "Destroy"
		self.img.__del__()
		self.saveConfig()
		gtk.timeout_add(100, gtk.main_quit)
	
	#
	# # Functions for controlling dialog windows
	#	
	def about(self, button): # Pop-up about
		self.about_dialog.run()
		self.about_dialog.hide()
			
	def run_pref(self, button): # Pop up preferences
		resp = self.options_dialog.run()
		if resp == 1:
			self.options_dialog.hide()
			# Sauvegarde
		else:
			self.options_dialog.hide()
	
	#
	# # Open functions
	#		
	def file_open(self, button):
		dialog = gtk.FileChooserDialog("Open Stereoscopic Image", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		dialog.set_default_response(gtk.RESPONSE_OK)
		
		filter = gtk.FileFilter()
		filter.set_name("Images Stéréo")
		# S3D Formats (si non present = inconnu = insupporte ???)
		filter.add_pattern("*.jps")
		filter.add_pattern("*.JPS")
		filter.add_pattern("*.pns")
		filter.add_pattern("*.PNS")
		filter.add_pattern("*.mpo")
		filter.add_pattern("*.MPO")
		dialog.add_filter(filter)
		
		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_mime_type("image/bmp")
		dialog.add_filter(filter)
				
		filter = gtk.FileFilter()
		filter.set_name("All Files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			fopen 			= dialog.get_filename()
			self.vergence 	= 0 # reset decallage
			self.src_info 	= os.path.split(fopen)
			
			self.img.open(fopen)
			self.modify_image()
		elif response == gtk.RESPONSE_CANCEL:
			print 'File selection aborted'
		dialog.destroy()
	
	def open_ana(self, button):
		dialog = gtk.FileChooserDialog("Open Anaglyph Image", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		dialog.set_default_response(gtk.RESPONSE_OK)
		
		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_mime_type("image/bmp")
		dialog.add_filter(filter)
				
		filter = gtk.FileFilter()
		filter.set_name("All Files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			fopen 			= dialog.get_filename()
			self.vergence 	= 0 # reset decallage
			self.src_info 	= os.path.split(fopen)
			
			self.img.open(fopen, True)
			self.modify_image()
		elif response == gtk.RESPONSE_CANCEL:
			print 'File selection aborted'
		dialog.destroy()

	#
	# # Callback functions for the toolbox
	#
	def full_screen(self, button):
		if self.window_mode == 0:	
			self.window_mode = 1
			self.window.fullscreen()
			screen = self.window.get_screen()
			# self.max_img_height, self.max_img_width = screen.get_width(), screen.get_height()
			self.modify_image()
		else:
			self.window_mode = 0
			self.window.unfullscreen()
			# self.max_img_height, self.max_img_width = self.stereo.allocation.height, self.stereo.allocation.width
			self.modify_image()

	def onSizeClick(self, button):	
		if button.get_label() == 'unzoom':
			self.zoom_percent -= 0.1
			self.modify_image()
		elif button.get_label() == 'zoom':
			self.zoom_percent += 0.1
			self.modify_image(1)
		elif button.get_label() == 'scale':
			self.zoom_percent = 0
			self.modify_image(1)
		elif button.get_label() == 'normale':
			self.zoom_percent = 0
			self.modify_image(1,1)

	def onImageMove(self, button): # Next/Previous image in the directory
		if button.get_label() == '>>':
			mode = 1
		elif button.get_label() == '<<':
			mode = -1
			
		extension 	= "jps" # Only jps
		path 			= self.src_info[0]

		fichiers 	= glob.glob(path +"/*."+ extension)
		fichiers.sort() # Alphabetical order

		max 				= len(fichiers)-1 # file count
		index 			= fichiers.index(path +"/"+ self.src_info[1]) + int(mode)
		
		if index < 0:
			index = max
		elif index > max:
			index = 0

		self.zoom_percent = 0
		self.vergence 		= 0
		self.src_info		= os.path.split(fichiers[index]) # Mise a jour
		self.display_image(fichiers[index])
	
	def onSeperationClick(self, button):	
		if button.get_label() == 'h+':
			self.img.vergence -= 1
		elif button.get_label() == 'h0':
			self.img.vergence = 0
		elif button.get_label() == 'h-':
			self.img.vergence += 1
		elif button.get_label() == 'v-':
			self.img.vsep -= 1
		elif button.get_label() == 'v+':
			self.img.vsep += 1
		
		self.modify_image()
	
	#
	# # Functions about first Eye
	#
	def set_eye(self, side):
		if side == "LEFT":
			print "Swapping to left eye"
			self.onEyeChange(True, False)
			self.conf['eye'] = "LEFT"
		elif side == "RIGHT":
			print "Swapping to right eye"
			self.onEyeChange(False, True)
			self.conf['eye'] = "RIGHT"
				
		self.img.swap_eyes()

		try:
			self.modify_image() # refresh image
		except:
			print "Eye changed, but image can not be modified"
	
	def onEyeChange(self, left, right):
		self.le_menu.set_active(left)
		self.re_menu.set_active(right)
		
	def onEyeClick(self, button):
		if self.flag == False:
			self.flag = True
			if button.get_name() == "GtkToolButton": # Swap button in the toolbox
				if self.le_menu.get_active() == True:
					self.set_eye("RIGHT")
				else:
					self.set_eye("LEFT")
				self.flag = False	
			else: # Menu
				if button.get_active() == True:	
					self.set_eye( string.upper( button.get_label() ) )
					self.flag = False
				else:
					button.set_active(True)
					self.flag = False	
		else:
			print "New eye value ignored because flag set"

	#
	# # Functions about Rendering Mode
	#
	def set_mode(self, mode):
		try:
			temp_left, temp_right = self.img.left, self.img.right
		except: # lib is not imported yet
			temp_left, temp_right = '', ''
		
		if mode == "INTERLACED":
			import lib_interlaced
			self.img = lib_interlaced.Interlaced()
			self.conf['mode'] = "INTERLACED" # Polarized Monitors (Zalman,IZ3D) / eDimensional
			self.onModeChange(False, True, False, False, False)
		elif mode == "ANAGLYPH":
			import lib_anaglyph
			self.img = lib_anaglyph.Anaglyph()
			self.conf['mode'] = "ANAGLYPH" # red/cyan
			self.onModeChange(True, False, False, False, False)
		elif mode == "SHUTTERS":
			import lib_shutter
			self.img = lib_shutter.Shutter()
			self.conf['mode'] = "SHUTTERS" # Nvidia 3D Vision / eDimensional
			self.onModeChange(False, False, True, False, False)
		elif mode == "DUAL OUTPUT":
			import lib_dualoutput
			self.img = lib_dualoutput.DualOutput()
			self.conf['mode'] = "DUAL OUTPUT"
			self.onModeChange(False, False, False, True, False)
		elif mode == "CHECKERBOARD":
			import lib_checkerboard
			self.img = lib_checkerboard.CheckerBoard()
			self.conf['mode'] = "CHECKERBOARD"
			self.onModeChange(False, False, False, False, True)	
		
		try:
			self.img.open2('None', [temp_left, temp_right])
			self.modify_image() # refresh image
		except:
			print "Mode changed, but image can not be modified"
		
		temp_left, temp_right = '', ''

	def onModeChange(self, ana, int, shu, dout, che):
		self.amode_menu.set_active(ana) # Anaglyph
		self.imode_menu.set_active(int) # Interlaced
		self.smode_menu.set_active(shu) # Shutters
		self.domode_menu.set_active(dout) # Dual Out
		self.cbmode_menu.set_active(che) # Checkerboard

	def onModeClick(self, button):
		if self.flag == False:
			self.flag = True
			if button.get_active() == True:	
				self.set_mode( string.upper( button.get_label() ) )
				self.flag = False
			else:
				button.set_active(True)
				self.flag = False		
		else:
			print "New mode value ignored because flag set"
	
	#
	# # Functions for controlling the image display
	#				
	def display_image(self, fopen="None", anaglyph=False): # Opening an image
		if fopen != "None":
			self.img.open(fopen, anaglyph) # anaglyph = True if the image is an anaglyph
			self.modify_image()
			
	# display = gtk.gdk.display_get_default()
	# print display.get_name() -> :0:0
	# print self.window.set_screen(gtk.gdk.screen_get_default())
	# gdk.screen_width(), gdk.screen_height()
	
	def modify_image(self, force=0, normale=0): # Redisplaying the image including changes (size, vergence ...) 
		self.img.resize(self.max_width*(1 + self.zoom_percent), self.max_height*(1 + self.zoom_percent), force, normale)
		
		get 	= self.img.make()
		
		if self.conf['mode'] != "DUAL OUTPUT" and self.conf['mode'] != "SHUTTERS":
			pixbuf = self.image_to_pixbuf( get )
			self.stereo.set_from_pixbuf(pixbuf) # Affichage
		else:
			left = self.image_to_pixbuf( get[0] )
			right = self.image_to_pixbuf( get[1] )
			self.doleft.set_from_pixbuf(left) # displaying
			self.doright.set_from_pixbuf(right) # displaying
			location = self.window.get_position()
			self.dualoutput_window.move(location[0],location[1])
			self.dualoutput_window.fullscreen()
			self.dualoutput_window.show()
		
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

# == On lance le programme
if __name__ == "__main__":
	def main(argv):
		fopen = "None"
		
		if len(argv) >= 1: # Il y a (au moins) un argument
			
			if argv[0][0] == "/": # Cas du lancement auto
				fopen = ' '.join(argv[0:])
			else:
				try:
					opts, args = getopt.getopt(argv, "hf:", ["help", "file="])
					print "Test arg"	
				
					for opt, arg in opts: # Traitement des parametres
						if opt in ("-h", "--help"):
							usage()
							sys.exit()
						elif opt in ("-f", "--file"):
							fopen = arg
				except getopt.GetoptError, err:
					print str(err)
					usage()
					sys.exit(2)
			
		return fopen		
	
	def usage():
		print "Tux Stereo Viewer"
		print "Usage:"
		print "    -h, --help : affiche ce message d'aide."
		print "    -f, --file : ouvre le fichier specifie."

	# Lancement du prog
	#	-> verification des param
	#	-> creation de la GUI
	fopen = "None"
	fopen = main(sys.argv[1:])
	GUI(fopen).main()