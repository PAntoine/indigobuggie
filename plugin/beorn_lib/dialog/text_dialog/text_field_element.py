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
#    file: text_field_element
#    desc: Text Field Element
#
#          This is the Basic Text Field for the Dialog system. This defines a text
#          box that will look like the following on screen:
#
#          Title Text [                                        ]
#
#  author: Peter Antoine
#    date: 08/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.text_dialog.text_dialog import TextDialog
from beorn_lib.dialog.base import FieldElement

class TextFieldElement(FieldElement):
	""" Text Box Element

		This defines the following element:

		    Title Text [                                        ]

		This box will allow for linear text to be entered in the defined space.
		The text will returned as a single string.

		Navigation keys cannot take the text past the last character entered.

		Optional Parameters:
		 name        type       description
		 ----------- ---------- -------------------------------------------------
		 input_type  <string>   For special input fields this specifies the type.
		                        Allowed types:
								'text'    The default basic text field.
								'numeric' The field is numeric.
								'secret'  The field is secret and the contents
								          are not shown.
								'error'   The field is an error field.
	"""
	def __init__(self, parameters):
		""" Init """
		# Local Element values
		self.line_no = 0
		self.text_pos = 0
		self.input_text = []

		# now bring in the parameters - may override the defaults
		super(TextFieldElement, self).__init__(parameters)

	def loadDefault(self):
		""" Load Default

			This resets the value of the item back to the default.
		"""
		self.input_text = []

		if self.default is not None:
			for char in self.default:
				if self.input_type == 'numeric':
					if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
						self.input_text.append(char)
				else:
					self.input_text.append(char)

		self.text_pos = len(self.input_text)

	def bottomRight(self):
		""" Bottom Right

			This function will return the bottom right corner of the dialog.
		"""
		right = self.x + len(self.title) + 3 + self.width

		return (right, self.y)

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the cursor position relative to the start of
			the screen.
		"""
		x_pos = self.x + len(self.title) + self.text_pos + 3
		return (x_pos, self.y)

	def handleKeyboardInput(self, keypress, screen):
		""" Handle Keyboard Input

			This function will handle the keyboard input to the element.

			What it will do is add the keypress to the output, if the output
			is at length then throw the keypress away. If the keypress is
			allowed then the screen will be updated.
		"""
		redraw = False

		if TextDialog.isSpecialKey(keypress):
			if keypress == TextDialog.DIALOG_SPECIAL_KEYS_DELETE:
				del self.input_text[self.text_pos]
				redraw = True

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_BACKSPACE:
				if self.text_pos > 0:
					self.text_pos -= 1
					del self.input_text[self.text_pos]
					redraw = True

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_LEFT:
				if self.text_pos > 0:
					self.text_pos -= 1
					redraw = True

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_RIGHT:
				if self.text_pos + 1 < len(self.input_text):
					self.text_pos += 1
					redraw = True

		else:
			if self.dialog.getInputMode() == TextDialog.DIALOG_INPUT_MODE_REPLACE:
				self.input_text[self.text_pos] = keypress
				self.text_pos += 1
				redraw = True

			else:
				# Ok, in insert mode
				if (self.text_pos + 1) < self.width:
					if self.input_type == 'numeric' and keypress in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
						self.input_text.insert(self.text_pos, keypress)
						self.text_pos += 1
						redraw = True

					elif self.input_type != 'numeric':
						self.input_text.insert(self.text_pos, keypress)
						self.text_pos += 1
						redraw = True

		self.is_dirty = redraw

		return (False, redraw)

	def renderElement(self, screen):
		""" Render Element

			This function will render the text field and fill in the typed in
			text to the screen.
		"""
		self.is_dirty = False

		if self.input_type == 'error' and len(self.input_text) == 0:
			# remove any old error that exists.
			x_pos = self.x

			while x_pos < (self.x + len(self.title) + 1 + 1 + self.width):
				screen[self.y][x_pos] = ' '

		else:
			for index, char in enumerate(self.title):
				screen[self.y][self.x + index] = char

			box_start = self.x + len(self.title) + 1

			# draw markers
			screen[self.y][box_start] = '['
			screen[self.y][box_start + 1 + self.width] = ']'

			# adjust box start to skip border
			box_start += 1

			# write the text to the screen buffer
			if len(self.input_text) >= self.width:
				text = self.input_text[len(self.input_text) - self.width:]
			else:
				text = self.input_text

			for index, _ in enumerate(text):
				if self.input_type in ['text', 'numeric']:
					screen[self.y][box_start + index] = text[index]
				else:
					screen[self.y][box_start + index] = '*'

		# clear the rest of the screen buffer
		for index in range(len(self.input_text), self.width):
			screen[self.y][box_start + index] = ' '

	def getValue(self):
		""" Get Value

			This function returns value from the Element.
		"""
		if self.input_type == 'numeric':
			if len(self.input_text) == 0:
				result = 0
			else:
				result = int(''.join(self.input_text))
		else:
			result = ''.join(self.input_text)

		return (self.name, result)

# vim: ts=4 sw=4 noexpandtab nocin ai
