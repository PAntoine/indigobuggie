#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#
#                    ,--.
#                    |  |-.  ,---.  ,---. ,--.--.,--,--,
#                    | .-. '| .-. :| .-. ||  .--'|      \
#                    | `-' |\   --.' '-' '|  |   |  ||  |
#                     `---'  `----' `---' `--'   `--''--'
#
#    file: element
#    desc: Base Dialog Element
#
#          This class is the base class for the Dialog Elements.
#          This function provides all the default functions that are required
#          for the elements.
#
#  author: Peter Antoine
#    date: 08/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

MANDATORY_PARAMETERS = [ 'name', 'x', 'y', 'title' ]
OPTIONAL_PARAMETERS = [ 'width', 'default', 'read-only' ]

class ElementItem(object):
	""" Base Dialog Element """

	def __new__(cls, parameters):
		""" New """
		result = None

		# check the the parameters that are required a passed in
		if all([ parameter in parameters for parameter in MANDATORY_PARAMETERS]):

			# Ok, all the required parameters exist.
			result = super(ElementItem, cls).__new__(cls)
			result.__init__(parameters)

		return result

	def __init__(self, parameters):
		""" init function for the base Element class """
		# load the mandatory parameters
		self.x = parameters['x']
		self.y = parameters['y']
		self.name = parameters['name']
		self.title = parameters['title']

		# load the option parameters
		if 'width' in parameters:
			self.width = parameters['width']

		elif not hasattr(self, 'width'):
			self.width = 0

		if 'default' in parameters:
			self.default = parameters['default']

		elif not hasattr(self, 'default'):
			self.default = None

		if 'read-only' in parameters:
			self.read_only = parameters['read-only']

		elif not hasattr(self, 'read_only'):
			self.read_only = False

		# non-parameter defaults (can be overridden)
		self.height = 1

		# working values
		self.is_dirty = True
		self.has_focus = False

		# the dialog that this element belongs too.
		self.dialog = None

	def initialise(self):
		""" Initialise """
		pass

	def isDirty(self):
		""" is Dirty

			Does the element need a redraw.
		"""
		return self.is_dirty

	def clearDirty(self):
		""" Clear Dirty

			This function clears the dirty flag.
		"""
		self.is_dirty = False

	def setFocus(self, focus):
		""" Set Focus

			This function lets the element know that it has focus.
		"""
		self.has_focus = focus

	def setParentDialog(self, dialog):
		""" Set Parent

			This simply sets the parent of the element.
		"""
		self.dialog = dialog

	def topLeft(self):
		""" Top Left

			This function will return the coordinates of the top-left corner of
			the object.
		"""
		return (self.x, self.y)

	def bottomRight(self):
		""" Bottom Left

			This function will return the bottom right corner of the dialog.
		"""
		return (self.x + self.width, self.y + self.height)

	def loadDefault(self):
		""" Load Default

			This resets the value of the item back to the default.
		"""
		# this does nothing
		pass

	def handleKeyboardInput(self, keypress, screen):
		""" Handle Keyboard Input

			This function will handle the keyboard input to the element.

			As the default implementation this does nothing.

			The tuple returned is: exit_dialog and refresh_screen.
		"""
		return (False, False)

	def getValue(self):
		""" Get Value

			This function returns value from the Element.
		"""
		return (self.name, None)

	def setValue(self, value):
		""" Set Value

			This function sets the value of the element.
		"""
		pass

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the cursor position relative to the start of
			the screen.
		"""
		return (self.x, self.y)

# vim: ts=4 sw=4 noexpandtab nocin ai
