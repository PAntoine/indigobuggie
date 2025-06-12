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
#    file: html_box_element
#    desc: This is a basic text box for the dialog.
#
#  author: Peter Antoine
#    date: 03/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base.element import ElementItem
from beorn_lib.dialog.base import BoxElement

class HTMLBoxElement(BoxElement):
	""" HTML Text Box Element

		This box generates a basic text box element.

		Extra Parameters:
		 name       type       description
		 --------   ---------- -----------------------------------------------------
		 height     <number>   The number of lines in the text box.
		 word-wrap  <Bool>	   If the text box should word-wrap at the end of line
		                       this being set to true, implies 'list = True'.[False]
		 list       <Bool>     This field will cause the result to be returned as
		                       a list of strings. [False]
	"""
	def renderElement(self, screen):
		""" Render Element

			This function will render the text box and fill in the typed in
			text to the screen.
		"""
		text_start = 0
		self.is_dirty = False

		screen.append("<div class='title'> %s </div>" % self.title)

		if self.word_wrap:
			screen.append("<textarea name='%s' wrap='hard' class='textbox' cols=%d rows=%d>" % (self.title, self.width, self.height))

			# draw the word wrapped version
			for item in self.wordWrapText():
				screen.append(''.join(self.input_text[item[0]:item[1]]))

			screen.append("</textarea>")

		else:
			screen.append("<textarea name='%s' wrap='soft' class='textbox' cols=%d rows=%d>" % (self.title, self.width, self.height))
			screen.append(''.join(self.input_text[0:self.width]))
			screen.append("</textarea>")

	def setValue(self, value):
		""" Set Value

			This function sets the value of the element.
		"""
		if type(value) == str or type(value) == int:
			self.input_text = []
			for char in str(value):
				self.input_text.append(char)

		elif type(value) == list and type(value[0]) == str:
			self.input_text = value

# vim: ts=4 sw=4 noexpandtab nocin ai
