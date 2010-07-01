#!/usr/bin/python
# -*- coding:utf-8 -*-

try:
	import psyco
	psyco.full();
	print "Psyco is installed."
except:
	print "Psyco isn't installed."

# == Utilisation de GTK pour la GUI
import pygtk
pygtk.require('2.0')
import gtk

# == Module a importer
import stereoIMG 		# Import du module de transformation en S-3D
import StringIO		# Conversion PIL -> Pixbuf
import sys, os, glob, getopt, time

#sys.path.append('/ufs/guido/lib/python')

# == Interface
class GUI:	
	def main(self): # Boucle principale
		gtk.main()
		return 0
	
	def __init__(self, fopen):
		self.interface = gtk.Builder()
		self.interface.add_from_file(sys.path[0] + '/interface-v0.3.glade')

		self.window = self.interface.get_object("main")
		self.window.set_title("Tux stereo Viewer")					# Nom de la fenetre
		self.window.set_icon( gtk.gdk.pixbuf_new_from_file('/usr/share/pixmaps/TuxStereoViewer-icon.png') ) # Thx H4X0R666 for the icon
		self.window.maximize()												# Maximiser la fenetre
		
		self.flag 				= False # Used for swithes (right<->left; interlaced<->anaglyph) --> Thx MickeyJaw !
		self.window_mode 		= 0 # Variable used for define fullscreen or maximized window
		self.src_info			= os.path.split(fopen) # All about file to open (fopen)
		self.zoom_percent		= 0 # Zoom
		self.getConfig()
		#self.stereo_mode 		= "INTERLACED"
		self.vergence 			= 0 # Puissance de l'effet 3D -> decallage horizontale
		
		# Connexions : Events -> Callback
		self.window.connect("destroy", self.destroy) 			# Fermeture propre
		self.window.connect("delete_event", self.delete_event) 	# Femeture par la croix
		
		# - Shortcut
		#	# Zoom
		self.increase_bouton	= self.interface.get_object("zoom")
		self.reset_x_bouton		= self.interface.get_object("echelle")
		self.decrease_bouton	= self.interface.get_object("unzoom")
		#	# Images
		self.fscreen_bouton 	= self.interface.get_object("full_screen")
		self.forward_bouton		= self.interface.get_object("forward")
		self.back_bouton		= self.interface.get_object("back")
		#	# 3D Effects
		self.increase_bouton	= self.interface.get_object("increase")
		self.reset_x_bouton		= self.interface.get_object("reset_x")
		self.decrease_bouton	= self.interface.get_object("decrease")
		
		# - Menus
		self.menubar 			= self.interface.get_object("menubar")
		self.about_dialog 		= self.interface.get_object("about")
		self.options_dialog 	= self.interface.get_object("options")
		
		# - Windows for eDimensional activations
		self.interlaced_on_window 	= self.interface.get_object("InterlacedOnWindow") 		# Set Interlaced Active
		self.int_reverse_window 	= self.interface.get_object("InterlacedReverseWindow")  # Set Interlaced (revesed) Active
		self.sync_doubling_window 	= self.interface.get_object("SyncDoublingWindow") 		# Set SyncDoubling (top/bottom) Active
		self.page_flip_window 		= self.interface.get_object("PageFlipWindow")			# Set Page Flipping (Shutter) Active
		self.off_window 				= self.interface.get_object("OffWindow")			# Set Glasses Off
		
		# - Dual Output
		self.doright 					= self.interface.get_object("do-right")
		self.doleft 					= self.interface.get_object("do-left")
		self.dualoutput_window 		= self.interface.get_object("dualoutputWindow")			# Window for displaying two images
		
		# - Switching menus
		# # Eyes
		self.re_menu 	= self.interface.get_object("right_eye_menu")
		self.le_menu 	= self.interface.get_object("left_eye_menu")
		if self.conf['eye'] == "LEFT":
			self.le_menu.set_active(True)
		else:
			self.re_menu.set_active(True)
		
		# # Stereo Mode
		self.imode_menu		= self.interface.get_object("inter_mode_menu")
		self.domode_menu		= self.interface.get_object("dualout_mode_menu")
		self.amode_menu		= self.interface.get_object("ana_mode_menu")
		self.tbmode_menu	= self.interface.get_object("top_bottom_menu")
		self.lrmode_menu	= self.interface.get_object("left_right_menu")
		self.checkerboard_menu 	= self.interface.get_object("checkerboard_menu")
		if self.conf['mode'] == "INTERLACED":
			self.imode_menu.set_active(True)
		else:
			self.amode_menu.set_active(True)

		# # eDimensional
		self.dongle_menu 		= self.interface.get_object("dongle_menu")
		if self.conf['type'] == "eDimensional":
			self.dongle_menu.set_active(True)
			if self.conf['mode'] == "INTERLACED":
				self.interlace_flash() 
			elif self.conf['mode'] == "VSYNC":
				self.vsync_flash()
		else:
			self.dongle_menu.set_active(False)
		
		self.interface.connect_signals(self)
		
		# display = gtk.gdk.display_get_default()
		# print display.get_name() -> :0:0

		print self.window.set_screen(gtk.gdk.screen_get_default())
		
		self.stereoIMG = stereoIMG.stereoIMG()
		self.stereoIMG.vsep = 0
		# - Displaying
		self.stereo = self.interface.get_object("stereo")
		self.window.show()
		self.max_img_height, self.max_img_width = self.stereo.allocation.height, self.stereo.allocation.width
		self.display_image(fopen)
	
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

	# #
	# Call-Back functions for events	
	def delete_event(self, widget, event=None, data=None): # Clean Closing
		print "Delete event"
		self.off_flash()
		gtk.timeout_add(1000, gtk.main_quit)
		return True # Do not allow OS to destroy we will kill ourselves in due time

	def destroy(self, widget, data=None): # Closing
		print "Destroy"
		self.off_flash()
		gtk.timeout_add(1000, gtk.main_quit)

	def swap_eyes_button(self, button):
		if self.re_menu.get_active() == True:
			self.le_menu.set_active(True)
		else:
			self.re_menu.set_active(True)

	def zoom(self, button):
		self.zoom_percent += 0.1
		self.modify_image() # "1" is to force redimesionning
	
	def taille_normale(self, button):
		self.zoom_percent = 0
		self.modify_image(0,1)
				
	def echelle(self, button):
		self.zoom_percent = 0
		self.modify_image()
		
	def unzoom(self, button):
		self.zoom_percent -= 0.1
		self.modify_image()
		
	def increase(self, button):
		self.vergence += 1
		self.modify_image()
		
	def reset_x(self, button):
		self.vergence = 0
		self.modify_image()
		
	def decrease(self, button):
		self.vergence -= 1
		self.modify_image()

	def increaseVsep(self, button):
		self.stereoIMG.vsep += 1
		self.modify_image()

	def decreaseVsep(self, button):
		self.stereoIMG.vsep -= 1
		self.modify_image()
		
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
			self.display_image(fopen)
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
			self.display_image(fopen, True)
		elif response == gtk.RESPONSE_CANCEL:
			print 'File selection aborted'
		
		dialog.destroy()

	def full_screen(self, button): # Passage en plein ecran
		# TODO :: Ouverture d'une pop-up sur fond noir en plein ecran
		if self.window_mode == 0:	
			print "full screen"
			self.window_mode = 1
			self.window.fullscreen()
			screen = self.window.get_screen()
			self.max_img_height, self.max_img_width = screen.get_width(), screen.get_height()
			self.modify_image()
		else:
			print "unfull screen"
			self.window_mode = 0
			self.window.unfullscreen()
			self.max_img_height, self.max_img_width = self.stereo.allocation.height, self.stereo.allocation.width
			self.modify_image()
			
	def forward(self, button):
		self.change_image(1)
	
	def back(self, button):
		self.change_image(-1)		
	
	def switch2ana(self, button):
		if self.flag == False: # Not already running
			print "Clicked anglyph"
			self.flag = True # Set flag so code for interlace button knows we are running
			if self.amode_menu.get_active() == True:	
				print "Just selected anaglyph, so deselecting others"			
				self.imode_menu.set_active(False)
				self.lrmode_menu.set_active(False)
				self.tbmode_menu.set_active(False)
				self.checkerboard_menu.set_active(False)		
				self.flag = False # No risk of changing interlace button now
				print "Now changing mode"								
				self.change_mode(1)
				print "Calling dongle code"
				self.off_flash()
			else:
				print "Just tried to deselect anaglyph, so set it again because we don't want nothing selected"
				self.amode_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to anaglyph value ignored because flag set"
			
				
	def switch2inter(self, button):
		if self.flag == False:
			print "Clicked interlaced"
			self.flag = True
			if self.imode_menu.get_active() == True:		
				print "Just selected interlace, so deselecting others"						
				self.amode_menu.set_active(False)
				self.lrmode_menu.set_active(False)
				self.tbmode_menu.set_active(False)
				self.checkerboard_menu.set_active(False)
				self.flag = False
				print "Calling dongle code"
				self.interlace_flash() # active before changing mode
				print "Now changing mode"				
				self.change_mode(0)
			else:
				print "Just tried to deselect interlace, so set it again because we don't want nothing selected"
				self.imode_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to interlace value ignored because flag set"
			
	def switch2topbottom(self, button):
		if self.flag == False:
			print "Clicked top/bottom"
			self.flag = True
			if self.tbmode_menu.get_active() == True:		
				print "Just selected top/bottom, so deselecting others"						
				self.amode_menu.set_active(False)
				self.imode_menu.set_active(False)
				self.lrmode_menu.set_active(False)
				self.checkerboard_menu.set_active(False)
				self.flag = False
				print "Calling dongle code"
				self.vsync_flash() # active before changing mode
				print "Now changing mode"				
				self.change_mode(3)
			else:
				print "Just tried to deselect top/bottom, so set it again because we don't want nothing selected"
				self.imode_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to top/bottom value ignored because flag set"
	
	def switch2leftright(self, button):
		if self.flag == False:
			print "Clicked left/right"
			self.flag = True
			if self.lrmode_menu.get_active() == True:		
				print "Just selected left/right, so deselecting others"						
				self.amode_menu.set_active(False)
				self.imode_menu.set_active(False)
				self.tbmode_menu.set_active(False)
				self.checkerboard_menu.set_active(False)
				self.flag = False
				print "Now changing mode"				
				self.change_mode(4)
				print "Calling dongle code"
				self.off_flash() # active before changing mode

			else:
				print "Just tried to deselect left/right, so set it again because we don't want nothing selected"
				self.imode_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to left/right value ignored because flag set"	
	
	def switch2dualoutput(self, button):
		if self.flag == False:
			print "Clicked dual-output"
			self.flag = True
			if self.domode_menu.get_active() == True:		
				print "Just selected dual-output, so deselecting others"						
				self.amode_menu.set_active(False)
				self.lrmode_menu.set_active(False)
				self.tbmode_menu.set_active(False)
				self.imode_menu.set_active(False)
				self.checkerboard_menu.set_active(False)
				self.flag = False
				self.change_mode(6)
			else:
				print "Just tried to deselect dual-output, so set it again because we don't want nothing selected"
				self.domode_menu.set_active(True)
				self.flag = False
		else:
			print "Change to dual-output value ignored because flag set"	

	def switch2checkerboard(self, button):
		if self.flag == False:
			print "Clicked left/right"
			self.flag = True
			if self.checkerboard_menu.get_active() == True:		
				print "Just selected left/right, so deselecting others"						
				self.amode_menu.set_active(False)
				self.imode_menu.set_active(False)
				self.tbmode_menu.set_active(False)
				self.lrmode_menu.set_active(False)
				self.flag = False
				print "Now changing mode"				
				self.change_mode(5)
				print "Calling dongle code"
				self.off_flash() # active before changing mode
			else:
				print "Just tried to deselect left/right, so set it again because we don't want nothing selected"
				self.checkerboard_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to left/right value ignored because flag set"	
		
	def switch2right(self, button):
		if self.flag == False:
			print "Clicked right eye"
			self.flag = True
			if self.re_menu.get_active() == True:		
				print "Just selected right, so deselecting left"						
				self.le_menu.set_active(False) # desactiver gauche
				self.flag = False
				print "Switching to right eye"
				self.stereoIMG.swap_eyes()
				self.modify_image()
			else:
				print "Just tried to deselect right, so set it again because we don't want nothing selected"
				self.re_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to right eye value ignored because flag set"
	
	def switch2left(self, button):
		if self.flag == False:
			print "Clicked left eye"
			self.flag = True
			if self.le_menu.get_active() == True:		
				print "Just selected left, so deselecting right"						
				self.re_menu.set_active(False) # desactiver droit
				self.flag = False
				print "Switching to left eye"
				self.stereoIMG.swap_eyes()
				self.modify_image()
			else:
				print "Just tried to deselect left, so set it again because we don't want nothing selected"
				self.le_menu.set_active(True)
				self.flag = False		
		else:
			print "Change to left eye value ignored because flag set"


	# #
	# Fonctions diverses
	def change_mode(self, mode):
		if mode == 0:
			self.conf['mode'] = "INTERLACED" # Polarized Monitors (Zalman,IZ3D) / eDimensional
		elif mode == 1:
			self.conf['mode'] = "ANAGLYPH"
		elif mode == 2:
			self.conf['mode'] = "SHUTTERS" # Nvidia 3D Vision / eDimensional
		elif mode == 3:
			self.conf['mode'] = "VSYNC" # Dual Projector / eDimensional
		elif mode == 4:
			self.conf['mode'] = "HSYNC" # Dual Projector / Planar
		elif mode == 5:
			self.conf['mode'] = "CHECKERBOARD" # Checkerboard for DLP
		elif mode == 6:
			self.conf['mode'] = "DUALOUTPUT" # Checkerboard for DLP
		try:
			self.modify_image()
		except:
			print "Mode changed, but image can not be modified"

	def change_image(self,mode=1):
		extension 	= "jps" # Extension autorise
		path 			= self.src_info[0] # dossier ou chercher

		fichiers 	= glob.glob(path +"/*."+ extension) # Recupere seulement les .jps
		fichiers.sort() #Classement alphabetique

		max 				= len(fichiers)-1 # nombre de fichiers
		index 			= fichiers.index(path +"/"+ self.src_info[1]) + int(mode)
		
		if index < 0:
			index = max
		elif index > max:
			index = 0
		# reinitalisation des variables
		self.zoom_percent = 0
		self.vergence = 0
		self.src_info	= os.path.split(fichiers[index]) # Mise a jour
		self.display_image(fichiers[index])
				
	def display_image(self, fopen="None", anaglyph=False): # Afichage d'une image (ouverture)
		if fopen != "None":
			#print image.get_mode()
			print "Opening " + fopen + " : " + self.conf['mode']
			#try:
			self.stereoIMG.set_sources_from_stereo(fopen,anaglyph)	# (fopen, True) -> si anaglyphe			
			if self.re_menu.get_active() == True:
				print "Swapping eyes"
				self.stereoIMG.swap_eyes()
			else:
				print "Not Swapping eyes"
			self.stereoIMG.make_stereo(self.max_img_height, self.max_img_width, self.vergence, self.conf['mode'])
			if self.conf['mode'] != "DUALOUTPUT":
				pixbuf = self.image_to_pixbuf( self.stereoIMG.get_image() )
				self.stereo.set_from_pixbuf(pixbuf) # Affichage
			else:
				images = self.stereoIMG.get_images()
				left = self.image_to_pixbuf( images[0] )
				right = self.image_to_pixbuf( images[1] )
				self.doleft.set_from_pixbuf(left) # displaying
				self.doright.set_from_pixbuf(right) # displaying
				location = self.window.get_position()
				self.dualoutput_window.move(location[0],location[1])
				self.dualoutput_window.fullscreen()
				self.dualoutput_window.show()
			#except:
			#	print "Image doesn't exist !"
	
	def modify_image(self, force=0, normale=0): # Affichage d'une image (modification)
		maxh, maxw = self.max_img_height*(1 + self.zoom_percent), self.max_img_width*(1 + self.zoom_percent)
		self.stereoIMG.make_stereo(maxh, maxw, self.vergence, self.conf['mode'], force, normale)
		print "Modification: Vergence=",self.vergence ," Mode=",self.conf['mode'], "Zoom=", self.zoom_percent
		if self.conf['mode'] != "DUALOUTPUT":
			pixbuf = self.image_to_pixbuf( self.stereoIMG.get_image() )
			self.stereo.set_from_pixbuf(pixbuf) # Affichage
		else:
			images = self.stereoIMG.get_images()
			left = self.image_to_pixbuf( images[0] )
			right = self.image_to_pixbuf( images[1] )
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

	def interlace_flash(self):
		if self.dongle_menu.get_active() == True:
			location = self.window.get_position()
			self.interlaced_on_window.move(location[0],location[1])
			self.interlaced_on_window.fullscreen()
			self.interlaced_on_window.show()
			gtk.timeout_add(1000, self.interlaced_on_window.hide)

	def reverse_flash(self):
		if self.dongle_menu.get_active() == True:
			location = self.window.get_position()
			self.int_reverse_window.move(location[0],location[1])
			self.int_reverse_window.fullscreen()
			self.int_reverse_window.show()
			gtk.timeout_add(1000, self.int_reverse_window.hide)
						
	def vsync_flash(self):
		if self.dongle_menu.get_active() == True:
			location = self.window.get_position()
			self.sync_doubling_window.move(location[0],location[1])
			self.sync_doubling_window.fullscreen()
			self.sync_doubling_window.show()
			gtk.timeout_add(1000, self.sync_doubling_window.hide)

	def pageflip_flash(self):
		if self.dongle_menu.get_active() == True:
			location = self.window.get_position()
			self.page_flip_window.move(location[0],location[1])
			self.page_flip_window.fullscreen()
			self.page_flip_window.show()
			gtk.timeout_add(1000, self.page_flip_window.hide)
	
	def off_flash(self):
		if self.dongle_menu.get_active() == True:
			location = self.window.get_position()
			self.off_window.move(location[0],location[1])
			self.off_window.fullscreen()
			self.off_window.show()
			gtk.timeout_add(1000, self.off_window.hide)

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