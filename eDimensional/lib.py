###
#
# File for using eDimensional Dongle !
#
###

class rendering:
	# Obligatoires
	def make(self):
		print "Make Rendering"

	def import(self,left,right):
		print "Make Rendering"
	
	def swap_eyes(self):
		print "Swap Eyes"
		
	# Specifiques
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