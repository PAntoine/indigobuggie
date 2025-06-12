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
#    file: button_list_element
#    desc: This element controls the button list.
#          It supports two kinds of button list, single select (radio) and
#          multiple select.
#
#  author: Peter Antoine
#    date: 03/02/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base import ButtonListElement
from .text_dialog import TextDialog

class TextButtonListElement(ButtonListElement):
	""" Button List Element

		This defines the following element:

		    Title:
			  [x] some text
			  [ ] some text more
			  [ ] some more text

		This allows for a button list to be drawn in text mode. It also supports
		two kinds of button list the single select (radio) and the multiple selection.

		The box is navigated by either the up and down keys, and an entry is
		toggled by either the space or the return key.

		Extra Parameters:
		 name     type       description
		 -------- ---------- -------------------------------------------------
		 items    <list>     The elements in the button list. This list should
		                     be in the following format:

							  (True/False, 'string text')

							 If the first element is True the item is selected
							 else it is not. The string text is what is going
							 to be displayed.

		 type     <string>   'single'   - Only allow one item to be selected.
		                     'multiple' - Allow multiple selections.

		Result:

		This element returns a list of the items that has been selected. So the
		result is a simple numeric list.
	"""
	def __init__(self, parameters):
		""" Init """

		# defaults for a TextButtonListElement
		self.current_line = 0
		self.bottom = 0
		self.lines = []

		# now bring in the parameters - may override the defaults
		super(TextButtonListElement, self).__init__(parameters)

	def initialise(self, defaults = False):
		""" Initialise

			This function will initialise the button list.
		"""
		self.lines = []

		""" Build Text Screen

			This only needs to be done once as the same layout can be used.
		"""
		longest_string = 0
		have_selection = False

		self.height = len(self.items) + 1

		for index, entry in enumerate(self.items):
			# only one allowed for the single selection, first come first served.
			if self.type_single:
				if have_selection:
					self.lines.append([False, entry[1]])
				else:
					self.lines.append([entry[0], entry[1]])
			else:
				self.lines.append([entry[0], entry[1]])

			# set current line to the first selection
			if not have_selection and entry[0]:
				self.current_line = index
				have_selection = True

			# calculate the width of the window
			if len(entry[1]) > longest_string:
				longest_string = len(entry[1])

		# calculate the width
		if self.width is None:
			if (longest_string + 5) < (len(self.title) + 2):
				self.right = len(self.title) + 2 + self.x
			else:
				self.right = longest_string + 5 + self.x

			self.width = 6 + longest_string
		else:
			self.right = self.x + self.width

		self.bottom = len(self.lines) + 1 + self.y
		self.last_selected = self.current_line

	def handleKeyboardInput(self, keypress, screen):
		""" Handle Keyboard Input

			This function will handle the keyboard input to the element.

			As the default implementation this does nothing.

			The tuple returned is: exit_dialog and refresh_screen.
		"""
		exit_dialog = False
		refresh = False

		if keypress == TextDialog.DIALOG_SPECIAL_KEYS_UP:
			if self.current_line > 0:
				self.current_line -= 1
				refresh = True

		elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_DOWN:
			if self.current_line < (len(self.lines) - 1):
				self.current_line += 1
				refresh = True

		elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_RETURN:
			if self.type_single:
				if not self.lines[self.current_line][0]:
					self.lines[self.last_selected][0] = False
					self.lines[self.current_line][0] = True

					self.last_selected = self.current_line
					refresh = True
			else:
				# toggle the current value
				self.lines[self.current_line][0] ^= True
				refresh = True

		self.is_dirty = refresh
		return (exit_dialog, refresh)

	def getValue(self):
		""" Get Value

			This function returns value from the Element.
		"""
		result = []

		for index, line in enumerate(self.lines):
			result.append(line[0])

		return (self.name, result)

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the cursor position relative to the start of
			the screen.
		"""
		return (self.x + 3, self.y + 1 + self.current_line)

	def renderElement(self, screen):
		""" Render Element

			This function will render the text box and fill in the typed in
			text to the screen.
		"""
		self.is_dirty = False

		for index, char in enumerate(self.title):
			screen[self.y][self.x + index] = char

		screen[self.y][self.x + len(self.title)] = ':'

		y_line = self.y

		for line in range(0, len(self.lines)):
			y_line += 1

			# draw markers
			screen[y_line][self.x + 2] = '['

			if self.lines[line][0]:
				screen[y_line][self.x + 3] = 'x'
			else:
				screen[y_line][self.x + 3] = ' '

			screen[y_line][self.x + 4] = ']'
			screen[y_line][self.x + 5] = ' '

			for index, char in enumerate(self.lines[line][1]):
				if (index + 6) < self.width:
					screen[y_line][self.x + 6 + index] = char
				else:
					break

# vim: ts=4 sw=4 noexpandtab nocin ai

