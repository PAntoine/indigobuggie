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
#    file: text_button_element
#    desc: Text Button Element
#
#          This is the button element of the dialog.
#
#          The button will always exit the dialog when selected with the value
#          set to True.
#
#          <"title_text">
#
#  author: Peter Antoine
#    date: 11/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base import ButtonElement
from .text_dialog import TextDialog


class TextButtonElement(ButtonElement):
	""" Text Button Element

		This defines the following element:

		    <  Text Button  >

		and:

		    <# Text Button #>

		when selected. This is a simple button element.
	"""
	def bottomRight(self):
		""" Bottom Left

			This function will return the bottom right corner of the dialog.
		"""
		return (self.x + len(self.title) + 6, self.y)

	def handleKeyboardInput(self, keypress, screen):
		""" Handle Keyboard Input

			This function will handle the keyboard input to the element.

			As the default implementation this does nothing.

			The tuple returned is: exit_dialog and refresh_screen.
		"""
		exit_dialog = False

		if keypress == TextDialog.DIALOG_SPECIAL_KEYS_RETURN:
			self.selected = True
			exit_dialog = True

		return (exit_dialog, False)

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the cursor position relative to the start of
			the screen.
		"""
		return (int(self.x + (len(self.title) + 6) / 2), int(self.y))

	def setFocus(self, focus):
		""" Set Focus

			This function lets the element know that it has focus.
			When the focus changes then the button needs to be redrawn.
		"""
		self.is_dirty = True
		self.has_focus = focus

	def renderElement(self, screen):
		""" Render Element

			This function will render the text box and fill in the typed in
			text to the screen.
		"""
		self.is_dirty = False

		screen[self.y][self.x    ] = '<'
		if self.has_focus:
			screen[self.y][self.x + 1] = '#'
		else:
			screen[self.y][self.x + 1] = ' '

		screen[self.y][self.x + 2] = ' '

		for index, char in enumerate(self.title):
			screen[self.y][self.x + 3 + index] = char

		pos = self.x + 3 + len(self.title)

		screen[self.y][pos    ] = ' '
		if self.has_focus:
			screen[self.y][pos + 1] = '#'
		else:
			screen[self.y][pos + 1] = ' '

		screen[self.y][pos + 2] = '>'

# vim: ts=4 sw=4 noexpandtab nocin ai
