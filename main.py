#!/usr/bin/python
# -*- coding:utf-8 -*-

try:
	import psyco
	psyco.full();
except:
	print "You can install Psyco to improove the rendering speed"

import pygtk
pygtk.require('2.0')
import gtk

#from gettext import gettext as _
#print display.get_name() #-> :0:0
#print self.window.set_screen(gtk.gdk.screen_get_default())
#print gdk.screen_width(), gdk.screen_height()

import sys, os, glob, getopt, string, webbrowser
import functions
import gconf

class GUI:	
	def main(self): # Main loop
		gtk.main()
		return 0
	
	def __init__(self):
		self.interface = gtk.Builder()
		self.interface.add_from_file(sys.path[0] + '/interface-v0.4.glade')

		self.window = self.interface.get_object("MainWin")
		self.window.set_title("Tux Stereo Viewer")
		self.window.set_icon( gtk.gdk.pixbuf_new_from_file('/usr/share/pixmaps/TuxStereoViewer-icon.png') )
		self.window.maximize()
		
		self.window.connect("destroy", self.destroy)
		self.window.connect("delete_event", self.delete_event)
		
		self.gconf = gconf.client_get_default()
		self.gconf.add_dir("/apps/tsv/general", gconf.CLIENT_PRELOAD_NONE)
		
		#self.src_info		= os.path.split(fopen)
		self.zoom_percent	= 0 # Zoom (in %)
		self.vergence 		= 0 # Vergence (in px)
		self.flag 			= False
		self.stereo			= self.interface.get_object("stereo") # Where we want to display the stereo image
		
		self.about_dialog 	= self.interface.get_object("AboutWin")
		self.options_dialog = self.interface.get_object("OptionsWin")
		
		# Fullscreen
		self.fs_image 		= self.interface.get_object("fullscreenImage") # Where we want to display the fullscreen image
		self.fs_window 		= self.interface.get_object("fullscreenWin")
		self.fs_mode		= 0 # 1 = Fullscren ; 0 = Windowed
		black 				= gtk.gdk.color_parse('#000000')
		self.fs_window.modify_bg(gtk.STATE_NORMAL, black)
		self.fs_window.fullscreen()
		
		# Dual Output Horizontal
		self.doright		= self.interface.get_object("do-right") # Right image for h dual output format
		self.doleft 		= self.interface.get_object("do-left") # Left image for h dual output format
		self.horizontal_window 	= self.interface.get_object("H-DualOutWin")
		
		# Dual Output Vertical
		self.dotop 			= self.interface.get_object("do-top") # Top image for v dual output format
		self.dobottom 		= self.interface.get_object("do-bottom") # Bottom image for v dual output format
		self.vertical_window	= self.interface.get_object("V-DualOutWin")
		
		# Quick configurations menus
		
		self.re_menu 		= self.interface.get_object("right_eye_menu")
		self.le_menu 		= self.interface.get_object("left_eye_menu")

		self.imode_menu		= self.interface.get_object("inter_mode_menu")
		self.domode_menu	= self.interface.get_object("dualout_mode_menu")
		self.amode_menu		= self.interface.get_object("ana_mode_menu")
		self.smode_menu		= self.interface.get_object("shutter_mode_menu")
		self.cbmode_menu	= self.interface.get_object("checkerboard_menu")
		
		# Toolbar
		self.toolbar 		= self.interface.get_object("QuickChangeToolbar")
		self.toolbar_check 	= self.interface.get_object("toolbar_check")
		if self.gconf.get_bool("/apps/tsv/general/toolbar") == False:
			self.toolbar_check.set_active(False)
			self.toolbar.hide()
		
		# Statusbar
		self.statusbar 	 = self.interface.get_object("statusBar")
		self.statusbar_check = self.interface.get_object("statusbar_check")
		if self.gconf.get_bool("/apps/tsv/general/statusbar") == False:
			self.statusbar_check.set_active(False)
			self.statusbar.hide()

		self.set_mode( self.gconf.get_string("/apps/tsv/general/mode") )
		self.set_eye( self.gconf.get_string("/apps/tsv/general/eye") )

		self.interface.connect_signals(self)
		self.window.show()

		
	def onSizeAllocate(self, win, alloc):
		self.max_height = alloc[3] - alloc[1]
		self.max_width 	= alloc[2] - alloc[0]
	
	def onScroll(self, widget, event):
		if event.direction == gtk.gdk.SCROLL_UP:
			print "UP"
		elif event.direction == gtk.gdk.SCROLL_DOWN:
			print "DOWN"
	
	def onKeyPressed(self, widget, event):
		if event.keyval == 65307 or event.keyval == 65480: # Escap / F11
			if self.fs_mode == 1: # Fullscreen is active
				self.full_screen(0)
	
	def onStatusbarCheck(self, button):
		if self.statusbar_check.get_active():
			self.statusbar.show()
			self.gconf.set_bool("/apps/tsv/general/statusbar", True)
		else:
			self.statusbar.hide()
			self.gconf.set_bool("/apps/tsv/general/statusbar", False)
				
	def onToolbarCheck(self, button):
		if self.toolbar_check.get_active():
			self.toolbar.show()
			self.gconf.set_bool("/apps/tsv/general/toolbar", True)
		else:
			self.toolbar.hide()
			self.gconf.set_bool("/apps/tsv/general/toolbar", False)

	#
	# # Shut down functions
	#
	def delete_event(self, widget, event=None, data=None): # Clean Closing
		print "Delete event"
		self.img.__del__()
		gtk.timeout_add(100, gtk.main_quit)
		return True # Do not allow OS to destroy we will kill ourselves in due time

	def destroy(self, widget, data=None): # Closing
		print "Destroy"
		self.img.__del__()
		gtk.timeout_add(100, gtk.main_quit)
	
	#
	# # Functions for controlling dialog windows
	#	
	def about(self, button): # About Window
		self.about_dialog.run()
		self.about_dialog.hide()

	def run_pref(self, button): # Preferences Window
		resp = self.options_dialog.run()
		if resp == 1:
			self.options_dialog.hide()
			# Sauvegarde
		else:
			self.options_dialog.hide()
	
	def offline_help(self, button):
		print 'Not yet'
					
	def online_help(self, button):
		url = 'https://answers.launchpad.net/tsv'
		# Open URL in new window, raising the window if possible.
		webbrowser.open_new(url)
	
	def translate(self, button):
		url = 'https://translations.launchpad.net/tsv'
		# Open URL in new window, raising the window if possible.
		webbrowser.open_new(url)
	
	#
	# # Open functions
	#		
	def openStereo(self, button):
		dialog = gtk.FileChooserDialog("Open Stereoscopic Image", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		dialog.set_default_response(gtk.RESPONSE_OK)
		
		filter = gtk.FileFilter()
		filter.set_name("Images Stéréo") # S3D Formats
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
			self.display_image(fopen, False)
		elif response == gtk.RESPONSE_CANCEL:
			print 'File selection aborted'
		dialog.destroy()
	
	def openAnaglyph(self, button):
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
			self.display_image(fopen, True)
		elif response == gtk.RESPONSE_CANCEL:
			print 'File selection aborted'
		dialog.destroy()
	
	#
	# # Callback functions for the toolbox
	#
	def full_screen(self, button):	
		if self.fs_mode == 0:
			self.fs_mode = 1
			self.fs_window.show()
			self.modify_image()
		else:
			self.fs_mode = 0
			self.fs_window.destroy()
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
		if button.get_stock_id() == 'gtk-go-forward':
			mode = 1
		elif button.get_stock_id() == 'gtk-go-back':
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

		self.zoom_percent 	= 0
		self.vergence 		= 0
		self.src_info		= os.path.split(fichiers[index]) # Mise a jour
		self.display_image(fichiers[index])
	
	def onSeperationClick(self, button):
		print button
		
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
	# # Functions about Eyes
	#
	def set_eye(self, side):
		if side == "LEFT":
			print "Swapping to left eye"
			self.onEyeChange(True, False)
			self.gconf.set_string("/apps/tsv/general/eye", "LEFT")
		else:
			print "Swapping to right eye"
			self.onEyeChange(False, True)
			self.gconf.set_string("/apps/tsv/general/eye", "RIGHT")
		
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
		#else:
		#	print "New eye value ignored because flag set"

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
			self.gconf.set_string("/apps/tsv/general/mode", "INTERLACED") # Polarized Monitors (Zalman) / eDimensional
			self.onModeChange(False, True, False, False, False)
		elif mode == "ANAGLYPH":
			import lib_anaglyph
			self.img = lib_anaglyph.Anaglyph()
			self.gconf.set_string("/apps/tsv/general/mode", "ANAGLYPH") # red/cyan
			self.onModeChange(True, False, False, False, False)
		elif mode == "SHUTTERS":
			import lib_shutter
			self.img = lib_shutter.Shutter()
			self.gconf.set_string("/apps/tsv/general/mode", "SHUTTERS") # Nvidia 3D Vision / eDimensional
			self.onModeChange(False, False, True, False, False)
		elif mode == "DUAL OUTPUT":
			import lib_dualoutput
			self.img = lib_dualoutput.DualOutput()
			self.gconf.set_string("/apps/tsv/general/mode", "DUAL OUTPUT")
			self.onModeChange(False, False, False, True, False)
		elif mode == "CHECKERBOARD":
			import lib_checkerboard
			self.img = lib_checkerboard.CheckerBoard()
			self.gconf.set_string("/apps/tsv/general/mode", "CHECKERBOARD")
			self.onModeChange(False, False, False, False, True)	
		else:
			import lib_interlaced # TODO => MONOSCOPIC
			self.img = lib_interlaced.Interlaced()
			self.gconf.set_string("/apps/tsv/general/mode", "INTERLACED")
			self.onModeChange(False, True, False, False, False)

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
		#else:
		#	print "New mode value ignored because flag set"
	
	#
	# # Functions for controlling the image display
	#				
	def display_image(self, fopen="None", anaglyph=False): # Opening an image
		context_id = self.statusbar.get_context_id("Open")
		self.statusbar.push(context_id, "Opening '"+fopen+"'")
			
		self.vergence 	= 0 # reset decallage
		self.src_info 	= os.path.split(fopen)	

		self.img.open(fopen, anaglyph) # anaglyph = True if the image is an anaglyph
		self.modify_image()
		
		self.statusbar.pop(context_id)
	
	def modify_image(self, force=0, normale=0): # Displaying the image (includes changes like size, vergence ...)
		self.img.resize(self.max_width*(1 + self.zoom_percent), self.max_height*(1 + self.zoom_percent), force, normale)
		#thread.start_new_thread(self.img.make, (self, self.fs_mode))
		self.img.make(self, self.fs_mode)
	
if __name__ == "__main__":
	TSV = GUI()

	if len(sys.argv)>1:
		if sys.argv[1][0] == "/":
			fopen = ' '.join(sys.argv[1])
			TSV.display_image(fopen, False)
			
	TSV.main()
