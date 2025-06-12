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
#    file: text_dialog
#    desc: Text Dialog Class
#
#          This is the main class for the text dialog.
#          It will control the text dialog, but it will not directly update
#          the screen.
#
#  author: Peter Antoine
#    date: 08/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog import BaseDialog

#---------------------------------------------------------------------------------
# Class Definition.
#---------------------------------------------------------------------------------
class TextDialog(BaseDialog):
	""" Text Dialog """
	#---------------------------------------------------------------------------------
	# Input Modes
	#---------------------------------------------------------------------------------
	DIALOG_INPUT_MODE_INSERT	= 0
	DIALOG_INPUT_MODE_REPLACE	= 1

	#---------------------------------------------------------------------------------
	# Special Keys
	#---------------------------------------------------------------------------------
	DIALOG_SPECIAL_KEYS_UP				= 0
	DIALOG_SPECIAL_KEYS_DOWN			= 1
	DIALOG_SPECIAL_KEYS_LEFT			= 2
	DIALOG_SPECIAL_KEYS_RIGHT			= 3
	DIALOG_SPECIAL_KEYS_RETURN			= 4
	DIALOG_SPECIAL_KEYS_DELETE			= 5
	DIALOG_SPECIAL_KEYS_BACKSPACE		= 6
	DIALOG_SPECIAL_KEYS_TAB				= 7
	DIALOG_SPECIAL_KEYS_ESCAPE			= 8

	SPECIAL_KEYS = [	DIALOG_SPECIAL_KEYS_UP				,
						DIALOG_SPECIAL_KEYS_DOWN			,
						DIALOG_SPECIAL_KEYS_LEFT			,
						DIALOG_SPECIAL_KEYS_RIGHT			,
						DIALOG_SPECIAL_KEYS_RETURN			,
						DIALOG_SPECIAL_KEYS_DELETE			,
						DIALOG_SPECIAL_KEYS_BACKSPACE		,
						DIALOG_SPECIAL_KEYS_TAB				,
						DIALOG_SPECIAL_KEYS_ESCAPE 			]

	@classmethod
	def isSpecialKey(cls, keypress):
		""" Is Special Key

			Checks to see if the key value passed into the function is one of the
			special keys that are non-character key-presses.
		"""
		if keypress in cls.SPECIAL_KEYS:
			return True
		else:
			return False

	def __init__(self):
		""" Initialise

			This function will initialise the TextDialog.
		"""
		# need to init the superclass
		super(TextDialog, self).__init__()

		self.screen_width = 0
		self.screen_height = 0
		self.lines = []
		self.current_element = None

		# state information
		self.input_mode = TextDialog.DIALOG_INPUT_MODE_INSERT

		from beorn_lib.dialog.text_dialog.text_box_element import TextBoxElement
		from beorn_lib.dialog.text_dialog.text_field_element import TextFieldElement
		from beorn_lib.dialog.text_dialog.text_button_element import TextButtonElement
		from beorn_lib.dialog.text_dialog.text_drop_down_element import TextDropDownElement
		from beorn_lib.dialog.text_dialog.text_button_list_element import TextButtonListElement

		# set the element types
		self.element_types['Button'] = TextButtonElement
		self.element_types['TextBox'] = TextBoxElement
		self.element_types['DropDown'] = TextDropDownElement
		self.element_types['TextField'] = TextFieldElement
		self.element_types['ButtonList'] = TextButtonListElement

	def resetDialog(self, defaults = False):
		""" Reset Dialog

			This function will throw away the current dialog buffer and rebuild
			it from the elements in the element list. It will fill the fields
			with the defaults (if present) in the elements. If this dialog has
			been filled before, unless the 'clean' flag is set then the previous
			values will be used where available.
		"""
		self.lines = []

		# first calculate the screen hight.
		# Only need to do this once.
		if self.screen_height == 0:
			for element in self.elements:
				(x, y) = element.bottomRight()

				if self.screen_width < x:
					self.screen_width = x

				if self.screen_height < y:
					self.screen_height = y

		self.screen_height += 1
		self.screen_width  += 1

		# create a square array of chars
		self.lines = [[' '] * self.screen_width for x in range(self.screen_height)]

		# Ok, we can now draw the elements onto the screen
		for element in self.elements:
			if defaults:
				element.loadDefaults()

			element.renderElement(self.lines)

		if self.current_element is None:
			self.current_element = self.elements[0]

	def setInputMode(self, mode = None):
		""" Set Input Mode

			This function will set the input mode for dialog. It excepts either insert
			or overwrite.

			If mode is left empty then the mode will be toggled.
		"""
		if mode is None:
			if self.input_mode == TextDialog.DIALOG_INPUT_MODE_INSERT:
				self.input_mode = TextDialog.DIALOG_INPUT_MODE_REPLACE
			else:
				self.input_mode = TextDialog.DIALOG_INPUT_MODE_INSERT

		else:
			self.input_mode = mode

	def getInputMode(self):
		""" Get Input Mode

			returns either text_dialog.DIALOG_INPUT_MODE_INSERT or text_dialog.DIALOG_INPUT_MODE_REPLACE
		"""
		return self.input_mode

	def handleSpecialKeys(self, keypress):
		""" Handle Special Keys

			This function will handle the special keys.
		"""
		refresh = False
		used = False
		exit_dialog = False

		if keypress == TextDialog.DIALOG_SPECIAL_KEYS_TAB:
			# Ok, need to change Element
			index = self.elements.index(self.current_element)

			start = index
			index = (index + 1) % len(self.elements)

			# don't select any elements that are read only.
			while index != start and self.elements[index].read_only:
				index = (index + 1) % len(self.elements)

			# only update if it has changed
			if index != start:
				self.current_element.setFocus(False)
				self.current_element = self.elements[index]
				self.current_element.setFocus(True)

				refresh = True

			used = True

		elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_ESCAPE:
			# Ok, exit the dialog
			exit_dialog = True
			used = True

		return (exit_dialog, refresh, used)

	def handleKeyboardInput(self, keypress):
		""" Handle Keyboard Input

			This function will handle the keyboard input.
			It first checks to see if the keyboard is one of the magic keys
			that need a specific action, else pass the key to the current selected
			element.
		"""
		(exit_dialog, refresh, used) = self.handleSpecialKeys(keypress)

		if not used:
			if self.current_element is not None:
				(exit_dialog, refresh) = self.current_element.handleKeyboardInput(keypress, self.lines)

		if refresh:
			self.repaint()

		return (exit_dialog, refresh)

	def focusElement(self, name):
		""" Focus Element

			This function will select the named element and make it the current
			focused element. If the element can't be found the function will
			return False, else True.
		"""
		result = False

		for element in self.elements:
			if element.name == name and not element.read_only:
				self.current_element.setFocus(False)
				self.current_element = element
				self.current_element.setFocus(True)
				result = True

		return result

	def repaint(self):
		""" Repaint Screen

			This function will cause all the elements that have changed to be
			repainted.
		"""
		for element in self.elements:
			if element.isDirty():
				element.renderElement(self.lines)

	def getScreen(self, read_only = False):
		""" Refresh screen

			This function will create the list of strings that can be used to
			update the screen. It will also call the "system" update function
			so that it can then update the system screen.
		"""
		output = []

		for line in self.lines:
			output.append(''.join(line))

		return output

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the current cursor position.
		"""
		return self.current_element.getCursorPos()

	def getResult(self):
		""" Exit Dialog

			This function will get the values from the dialog and return them back to the caller.
		"""
		result = {}

		for element in self.elements:
			(index, value) = element.getValue()
			result[index] = value

		return result
# vim: ts=4 sw=4 noexpandtab nocin ai
