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
#    file: drop_down_element
#    desc: Drop Down Element
#
#          This is the Drop Down Element for the Dialog system. This defines a
#          drop down that will look like the following on screen:
#
#          Drop Down [ line x of drop down                    ]
#                   >[ line y of drop down                    ]
#                    [ line z of drop down                    ]
#
#          Extra Parameters:
#          	height = number of lines to display.
#
#
#  author: Peter Antoine
#    date: 08/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.text_dialog import TextDialog
from beorn_lib.dialog.base import DropDownElement

class TextDropDownElement(DropDownElement):
	""" Drop Down Element

		This defines the following element:

            Drop Down [ line x of drop down                    ]
                     >[ line y of drop down                    ]
                      [ line z of drop down                    ]

		This box will allow for a list of elements to be selected from.

		The list is navigated by the up and down keys. The list will rotate
		around the mid-point in the list.


		Extra Parameters:
		 name     type       description
		 -------- ---------- -------------------------------------------------
		 height   <number>   The number of lines displayed in the drop box, it
		                     not the number of elements in the drop down list.

		 items    <list>	 NOT OPTIONAL. The list of elements for the list.

		 default  <number>   The element that has been selected.
	"""

	ELEMENT_TYPE = 'DropDown'

	def bottomRight(self):
		""" Bottom Right

			This function will return the bottom right corner of the dialog.
		"""
		right = self.x + len(self.title) + 3 + self.width
		bottom = self.y + self.height

		return (right, bottom)

	def getCursorPos(self):
		""" Get Cursor Position

			This function returns the cursor position relative to the start of
			the screen.
		"""
		return (0, 0)

	def handleKeyboardInput(self, keypress, screen):
		""" Handle Keyboard Input

			This function will handle the keyboard input to the element.

			What it will do is add the keypress to the output, if the output
			is at length then throw the keypress away. If the keypress is
			allowed then the screen will be updated.
		"""
		redraw = False

		if TextDialog.isSpecialKey(keypress):
			if keypress == TextDialog.DIALOG_SPECIAL_KEYS_UP:
				if self.current_line > 0:
					self.current_line -= 1
					redraw = True

			elif keypress == TextDialog.DIALOG_SPECIAL_KEYS_DOWN:
				if self.current_line < (len(self.contents) - 1):
					self.current_line += 1
					redraw = True

		self.is_dirty = redraw

		return (False, redraw)

	def renderElement(self, screen):
		""" Render Element

			This function will render the drop down list.
		"""
		self.is_dirty = False
		start_item = 0

		if len(self.contents) < self.height:
			# we dont need to scroll
			selected_line = self.current_line

		elif self.current_line > (len(self.contents) - self.height + 1):
			# remains of the list are in the list
			start_item    = len(self.contents) - self.height
			selected_line = self.current_line - start_item

		elif self.current_line > (self.height / 2):
			start_item    = self.current_line - int (self.height / 2)
			selected_line = self.current_line - start_item

		else:
			selected_line = self.current_line

		# write title
		for index, char in enumerate(self.title):
			screen[self.y][self.x + index] = char

		# write the lines in the drop down
		for line in range(0, self.height):
			box_start = self.x + len(self.title) + 1

			# draw markers
			screen[self.y + line][box_start] = '['

			if line == selected_line:
				screen[self.y + line][box_start - 1] = '>'
			else:
				screen[self.y + line][box_start - 1] = ' '

			screen[self.y + line][box_start + 1 + self.width] = ']'

			# adjust box start to skip border
			box_start += 1

			if (line + start_item) < len(self.contents):
				# write the text to the screen buffer
				for index in range(self.width):
					if index < len(self.contents[line + start_item]):
						screen[self.y + line][box_start + index] = self.contents[line + start_item][index]
					else:
						screen[self.y + line][box_start + index] = ' '
			else:
				for index in range(self.width):
					screen[self.y + line][box_start + index] = ' '

	def getValue(self):
		""" Get Value

			This function returns value from the Element.
		"""
		return (self.name, self.current_line)

# vim: ts=4 sw=4 noexpandtab nocin ai
