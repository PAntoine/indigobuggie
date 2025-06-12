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
#    file: text_box
#    desc: Text Box Element
#
#          This is the Basic Text Box for the Dialog system. This defines a text
#          box that will look like the following on screen:
#
#          Title Text [                                        ]
#                     [                                        ]
#                     [                                        ]
#
#          Extra Parameters:
#          	height = number of lines.
#
#
#  author: Peter Antoine
#    date: 08/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import beorn_lib.dialog
from beorn_lib.dialog.base import BoxElement
from beorn_lib.dialog.text_dialog import TextDialog

class TextBoxElement(BoxElement):
	""" Text Box Element

		This defines the following element:

		    Title Text [                                        ]
		               [                                        ]
		               [                                        ]

		This box will allow for linear text to be entered in the defined space.
		The text will returned as a single string.

		The box will allow for basic navigation with the up,down,left and right
		keys. Delete and Backspace will both be supported. Tabs cannot be input
		directly as these are dialog special keys, so standard c-style escape
		chars can be input if the text box will allow.

		Navigation keys cannot take the text past the last character entered.

		Extra Parameters:
		 name       type       description
		 --------   ---------- -----------------------------------------------------
		 height     <number>   The number of lines in the text box.
		 word-wrap  <Bool>	   If the text box should word-wrap at the end of line
		                       this being set to true, implies 'list = True'.[False]
		 list       <Bool>     This field will cause the result to be returned as
		                       a list of strings. [False]
	"""
	def loadDefault(self):
		""" Load Default

			This resets the value of the item back to the default.
		"""
		if self.default is not None:
			for char in self.default:
				self.input_text.append(char)

		if len(self.input_text) > 0:
			self.text_pos = len(self.input_text) - 1
		else:
			self.text_pos = 0


	def bottomRight(self):
		""" Bottom Right

			This function will return the bottom right corner of the dialog.
		"""
		right = self.x + len(self.title) + 3 + self.width

		return (right, self.y + self.height)

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the cursor position relative to the start of
			the screen.
		"""
		y_pos = self.y + int( self.text_pos / self.width)
		x_pos = self.x + len(self.title) + (self.text_pos % self.width) + 3
		return (x_pos, y_pos)

	def handleKeyboardInput(self, keypress, screen):
		""" Handle Keyboard Input

			This function will handle the keyboard input to the element.

			What it will do is add the keypress to the output, if the output
			is at length then throw the keypress away. If the keypress is
			allowed then the screen will be updated.
		"""
		redraw = False

		if TextDialog.isSpecialKey(keypress):
			old_pos = self.text_pos

			if keypress == TextDialog.DIALOG_SPECIAL_KEYS_DELETE:
				del self.input_text[self.text_pos]
				redraw = True

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_BACKSPACE:
				if self.text_pos > 0:
					self.text_pos -= 1
					del self.input_text[self.text_pos]

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_LEFT:
				if self.text_pos > 0:
					self.text_pos -= 1

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_RIGHT:
				if self.text_pos < len(self.input_text):
					self.text_pos += 1

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_UP:
				if (self.text_pos - self.width) > 0:
					self.text_pos -= self.width
				else:
					self.text_pos = self.text_pos % self.width

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_DOWN:
				if (self.text_pos + self.width) < len(self.input_text):
					self.text_pos += self.width
				else:
					self.text_pos = len(self.input_text)

			# do we need to update the screen
			redraw = redraw or (old_pos != self.text_pos)

		else:
			if self.dialog.getInputMode() == TextDialog.DIALOG_INPUT_MODE_REPLACE:
				if self.text_pos < len(self.input_text):
					# overwrite if a character
					self.input_text[self.text_pos] = keypress
					self.text_pos += 1
				else:
					# append if at end of text
					self.input_text.insert(self.text_pos, keypress)
					self.text_pos += 1

				redraw = True

			else:
				# Ok, in insert mode
				self.input_text.insert(self.text_pos, keypress)
				self.text_pos += 1
				redraw = True

		self.is_dirty = redraw

		return (False, redraw)

	def renderElement(self, screen):
		""" Render Element

			This function will render the text box and fill in the typed in
			text to the screen.
		"""
		text_start = 0
		self.is_dirty = False

		for index, char in enumerate(self.title):
			screen[self.y][self.x + index] = char

		if self.word_wrap:
			# draw the word wrapped version
			line_offsets = self.wordWrapText()
			box_start = self.x + len(self.title) + 2

			for h_line in range(0, self.height):
				y_line = self.y + h_line

				# draw markers
				screen[y_line][box_start - 1] = '['
				screen[y_line][box_start + self.width] = ']'

				if h_line < len(line_offsets):
					# write text
					line = line_offsets[h_line]

					for index in range(self.width):
						if index < (line[1] - line[0]):
							screen[y_line][box_start + index] = self.input_text[line[0] + index]
						else:
							screen[y_line][box_start + index] = ' '

		else:
			# non-word wrapped text
			for line in range(self.y, self.y + self.height):
				box_start = self.x + len(self.title) + 1

				# draw markers
				screen[line][box_start] = '['
				screen[line][box_start + 1 + self.width] = ']'

				# adjust box start to skip border
				box_start += 1

				# write the text to the screen buffer
				for index in range(self.width):
					if (index + text_start) < len(self.input_text):
						screen[line][box_start + index] = self.input_text[text_start + index]
					else:
						screen[line][box_start + index] = ' '

				# increment the text by a line
				text_start += self.width

# vim: ts=4 sw=4 noexpandtab nocin ai
