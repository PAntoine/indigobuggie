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
#    desc: The button list base class.
#
#  author: Peter Antoine
#    date: 06/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import beorn_lib.dialog
from beorn_lib.dialog.base.element import ElementItem

class ButtonListElement(ElementItem):
	def __init__(self, parameters):
		""" Init """

		# defaults for a ButtonListElement
		self.width = 32
		self.current_line = 0
		self.type_single = True
		self.items = []

		# now bring in the parameters - may override the defaults
		super(ButtonListElement, self).__init__(parameters)

	@classmethod
	def create(cls, parameters):
		""" create

			This function will create a ButtonListElement.
		"""
		result = None

		if 'items' in parameters and type(parameters['items']) == list:
			# Ok, all the required parameters exist.
			result = cls(parameters)

			if result is not None:
				# type defaults to single selection
				result.type_single = True

				# has user offered a preference
				if 'type' in parameters:
					if parameters['type'] == 'multiple':
						result.type_single = False

				# now load the itemss
				result.current_line = 0
				result.items = parameters['items']

				# Local Element values
				result.loadDefault()
				result.initialise()

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
