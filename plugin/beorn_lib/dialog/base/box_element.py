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
#    file: box_element
#    desc: This is the base class for the basic text box element.
#
#  author: Peter Antoine
#    date: 03/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base.element import ElementItem

REQUIRED_PARAMETERS = [ 'height' ]

class BoxElement(ElementItem):
	""" Box Element

		This is a basic text box element and it will have following definitions.

		Extra Parameters:
		 name       type       description
		 --------   ---------- -----------------------------------------------------
		 height     <number>   The number of lines in the text box.
		 word-wrap  <Bool>	   If the text box should word-wrap at the end of line
		                       this being set to true, implies 'list = True'.[False]
		 list       <Bool>     This field will cause the result to be returned as
		                       a list of strings. [False]
	"""

	def __init__(self, parameters):
		""" Init """

		# defaults for a BoxElement
		self.width = 32
		self.input_text = ""
		self.text_length = 0
		self.word_wrap = False
		self.output_list = False

		# now bring in the parameters - may override the defaults
		super(BoxElement, self).__init__(parameters)

	@classmethod
	def create(cls, parameters):
		""" create

			This function will create a BoxElement. As the parameters
			are validated before the element is created.
		"""
		result = None

		# check that the parameters that are required are passed in
		if all([ parameter in parameters for parameter in REQUIRED_PARAMETERS]):

			if 'word-wrap' in parameters and type(parameters['word-wrap']) != bool:
				pass

			elif 'list' in parameters and type(parameters['list']) != bool:
				pass

			else:
				# Ok, all the required parameters exist.
				result = cls(parameters)

				if result:
					if 'list' in parameters:
						result.output_list = parameters['list']

					if 'word-wrap' in parameters:
						result.word_wrap = parameters['word-wrap']
						result.output_list = True

					# Ok, all looks good, do the setup for the BoxElement
					result.height = parameters['height']

					# text length
					result.input_text = []
					result.text_length = 0

					# Local Element values
					result.loadDefault()

		return result

	def loadDefault(self):
		""" Load Default

			This resets the value of the item back to the default.
		"""
		if self.default is not None:
			for char in self.default:
				self.input_text.append(char)

	def getValue(self):
		""" Get Value

			This function returns value from the Element.
		"""
		if self.output_list:
			result = []

			if self.word_wrap:
				line_offsets = self.wordWrapText()

				for item in line_offsets:
					result.append(''.join(self.input_text[item[0]:item[1]]))

			else:
				pos = 0

				for _ in range(self.height):
					result.append( ''.join(self.input_text[pos:pos + self.width]))
					pos += self.width

			return (self.name, result)
		else:
			return (self.name, ''.join(self.input_text))

	def wordWrapText(self):
		""" Word Wrap Text

			This function will take the current text and generate a list of start and length
			tuples. It will simply check at line_length intervals for non-spaces, and then
			search backwards for the next space. If the search finds the beginning of the
			line then it will hard-wrap the line be setting a marker at the line offset.
		"""
		result = []

		start = 0
		offset = 0
		search = offset + self.width

		while offset < len(self.input_text) and search < len(self.input_text):
			if self.input_text[search] == ' ':
				# we have we found a space, wrap here
				result.append((start, search))

				start  = search + 1
				offset = start + self.width
				search = offset
			else:
				# decrement the search
				search = search - 1

				# have we reached the start of the search, if so clip. (means the word is
				# wider then the window).
				if search <= start:
					result.append((start, start + self.width))
					start  = start + self.width
					offset = start + self.width
					search = offset

		if start < len(self.input_text):
			result.append((start, len(self.input_text)))

		return result


# vim: ts=4 sw=4 noexpandtab nocin ai
