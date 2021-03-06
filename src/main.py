#!/usr/bin/python
# -*- coding:utf-8 -*-

try:
	import psyco
	psyco.full();
except:
	print "You can install Python-Psyco to improve the rendering speed"

import pygtk
pygtk.require('2.0')
import gtk

#from gettext import gettext as _

import sys, os, glob, getopt, string, gconf, time

class GUI:	
	def main(self): # Main loop
		gtk.main()
		return 0
	
	def __init__(self):
		self.interface = gtk.Builder()
		self.interface.add_from_file(sys.path[0] + '/interface-v0.4.glade')

		self.window = self.interface.get_object("MainWin")
		self.window.set_title("Tux Stereo Viewer")
		self.window.set_icon( gtk.gdk.pixbuf_new_from_file('/usr/share/pixmaps/tuxstereoviewer.png') )
		self.window.maximize()
		
		self.window.connect("destroy", self.destroy)
		self.window.connect("delete_event", self.delete_event)
		
		self.gconf = gconf.client_get_default()
		self.gconf.add_dir("/apps/tsv/general", gconf.CLIENT_PRELOAD_NONE)

		self.zoom_percent	= 0 # Zoom (in %)
		self.vergence 		= 0 # Vergence (in px)
		self.fs_mode		= 0 # 1 = Fullscren ; 0 = Windowed
		self.flag 			= False
		self.stereo			= self.interface.get_object("stereo") # Where we want to draw the stereo image
		
		self.about_dialog 	= self.interface.get_object("AboutWin")
		self.options_dialog = self.interface.get_object("OptionsWin")
		
		# Dual Output Horizontal
		self.doright		= self.interface.get_object("do-right") # Right image for h dual output format
		self.doleft 		= self.interface.get_object("do-left") # Left image for h dual output format
		self.horizontal_window 	= self.interface.get_object("H-DualOutWin")
		
		# Dual Output Vertical
		self.dotop 			= self.interface.get_object("do-top") # Top image for v dual output format
		self.dobottom 		= self.interface.get_object("do-bottom") # Bottom image for v dual output format
		self.vertical_window	= self.interface.get_object("V-DualOutWin")
		
		# Quick configurations menus
		self.re_menu = self.interface.get_object("right_eye_menu")
		self.le_menu = self.interface.get_object("left_eye_menu")
		
		# Toolbar
		self.toolbar = self.interface.get_object("QuickChangeToolbar")
		self.toolbar_check = self.interface.get_object("toolbar_check")
		if self.gconf.get_bool("/apps/tsv/general/toolbar") == False:
			self.toolbar_check.set_active(False)
			self.toolbar.hide()
		
		# Statusbar
		self.statusbar = self.interface.get_object("statusBar")
		self.statusbar_check = self.interface.get_object("statusbar_check")
		if self.gconf.get_bool("/apps/tsv/general/statusbar") == False:
			self.statusbar_check.set_active(False)
			self.statusbar.hide()
		
		self.menubar = self.interface.get_object("MenuBar")	
		self.set_mode( self.gconf.get_string("/apps/tsv/general/mode") )
		self.set_eye( self.gconf.get_string("/apps/tsv/general/eye") )

		self.interface.connect_signals(self)
		self.window.show()
		
		style = self.stereo.get_style()
		self.gc = style.fg_gc[gtk.STATE_NORMAL]
		
	def onSizeAllocate(self, win, alloc):
		self.max_height = alloc[3] - alloc[1]
		self.max_width 	= alloc[2] - alloc[0]		
		return True
		
	def onScroll(self, widget, event):
		if event.direction == gtk.gdk.SCROLL_UP:
			print "UP"
		elif event.direction == gtk.gdk.SCROLL_DOWN:
			print "DOWN"
					
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
			
	def onCursorStop(self):
		pix_data = """/* XPM */
		static char * invisible_xpm[] = {
		"1 1 1 1",
		"       c None",
		" "};"""
		color = gtk.gdk.Color()
		pix = gtk.gdk.pixmap_create_from_data(None, pix_data, 1, 1, 1, color, color)
		invisible = gtk.gdk.Cursor(pix, pix, color, color, 0, 0)
		
		b.window.set_cursor(invisible)

	#
	# # Fullscreen functions
	#	
	def onKeyPressed(self, widget, event):
		print "press", gtk.gdk.keyval_name(event.keyval)
		if event.keyval == 65307 or event.keyval == 65480: # Escap / F11
			if self.fs_mode == 1:
				self.fs_mode = 0
				self.full_screen(0)
				return True

	def onFullScreenCheck(self, button):
		if self.fs_mode == 0 and button.get_active():
			self.fs_mode = 1
			self.full_screen(1)
		return True
	
	def onExpose(self, widget, event):
		print event
		self.modify_image()
		return True
	
	def full_screen(self, mode):
		if mode == 1 and mode == self.fs_mode:
			#self.statusbar.hide()
			#self.toolbar.hide()
			#self.menubar.hide()
			self.stereo.fullscreen()
		elif mode == 0 and mode == self.fs_mode:
			#self.statusbar.show()
			#self.toolbar.show()
			#self.menubar.show()
			self.window.unfullscreen()
	
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
		print "Not yet"
	
	#
	# # Open functions
	#		
	def openStereo(self, button):
		dialog = gtk.FileChooserDialog("Open Stereoscopic Image", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		dialog.set_default_response(gtk.RESPONSE_OK)
		
		filter = gtk.FileFilter()
		filter.set_name("Stereo Images") # S3D Formats
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
	def onSizeClick(self, button):	
		# UGLY
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
		path		= self.src_info[0]

		fichiers 	= glob.glob(path +"/*."+ extension)
		fichiers.sort() # Alphabetical order

		max 		= len(fichiers)-1 # file count
		index 		= fichiers.index(path +"/"+ self.src_info[1]) + int(mode)
		
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
		# UGLY !
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
		self.modify_image() # refresh image
	
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
		
		if mode == "ANAGLYPH": #Red/Cyan and others
			import lib_anaglyph
			self.img = lib_anaglyph.Anaglyph(self)
			self.gconf.set_string("/apps/tsv/general/mode", "ANAGLYPH")
			self.onModeChange(False, True, False, False, False, False)
		elif mode == "INTERLACED": # Polarized Monitors (i.e. Zalman)
			import lib_interlaced
			self.img = lib_interlaced.Interlaced()
			self.gconf.set_string("/apps/tsv/general/mode", "INTERLACED")
			self.onModeChange(False, False, True, False, False, False)
		elif mode == "SHUTTERS": # Nvidia 3D Vision / eDimensional
			import lib_shutter
			self.img = lib_shutter.Shutter(self)
			self.gconf.set_string("/apps/tsv/general/mode", "SHUTTERS") 
			self.onModeChange(False, False, False, True, False, False)
		elif mode == "DUAL OUTPUT": # Two Projector
			import lib_dualoutput
			self.img = lib_dualoutput.DualOutput()
			self.gconf.set_string("/apps/tsv/general/mode", "DUAL OUTPUT")
			self.onModeChange(False, False, False, False, True, False)
		elif mode == "CHECKERBOARD": # SOME OLD (USA) 3D TV
			import lib_checkerboard
			self.img = lib_checkerboard.CheckerBoard()
			self.gconf.set_string("/apps/tsv/general/mode", "CHECKERBOARD")
			self.onModeChange(False, False, False, False, False, True)	
		else: # MONOSCOPIC
			import lib_freeview
			self.img = lib_freeview.Simple()
			self.gconf.set_string("/apps/tsv/general/mode", "MONOSCOPIC")
			self.onModeChange(True, False, False, False, False, False)
		
		self.img.open2('None', [temp_left, temp_right])
		self.modify_image() # refresh image	
		temp_left, temp_right = '', ''

	def onModeChange(self, mono, ana, int, shu, dout, che):
		self.interface.get_object("mono_mode_menu").set_active(mono) # Monoscopic
		self.interface.get_object("inter_mode_menu").set_active(int) # Interlaced
		self.interface.get_object("dualout_mode_menu").set_active(dout) # Dual Out
		self.interface.get_object("ana_mode_menu").set_active(ana) # Anaglyph
		self.interface.get_object("shutter_mode_menu").set_active(shu) # Shutters
		self.interface.get_object("checkerboard_menu").set_active(che) # Checkerboard

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
		try:
			if self.fs_mode == 1:
				self.img.resize(self.max_width, self.max_height, 1, 0)
			else:
				self.img.resize(self.max_width*(1 + self.zoom_percent), self.max_height*(1 + self.zoom_percent), force, normale)
			
			self.stereo.window.clear()	
			self.img.make(self, self.fs_mode)
		except Exception,e:
			print "Error while rendering the image:", e
	
if __name__ == "__main__":
	TSV = GUI()

	if len(sys.argv)>1:
		if sys.argv[1][0] == "/":
			#fopen = ' '.join(sys.argv[1])
			if os.path.exists(sys.argv[1]):
				TSV.display_image(sys.argv[1], False)
			else:
				print "Image doesn't exist"
	
	TSV.main()
