import os
import logging
import sublime, sublime_plugin

class TSCompletionCommand(sublime_plugin.TextCommand):

	def createTree(self):
		return os.listdir(os.curdir + "./../../../../Users/SoiZen/Documents/work/office/ebzLoader/src/")

	def run(self, edit):
		#self.view.insert(edit, 0, "Hello, World!")
		#sublime.message_dialog(str(self.view.sel()))
		#sublime_plugin.EventListener
		sublime.active_window().show_quick_panel(self.createTree(), self.on_choice)

	def on_change(self, value):
		logging.warning(value)
		self.enteredKey.append(value)


	def on_choice(self, value):
		logging.warning("Finish")
