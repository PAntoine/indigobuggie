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
#    desc: This is the drop down element.
#
#  author: Peter Antoine
#    date: 11/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import beorn_lib.dialog
from beorn_lib.dialog.base.element import ElementItem

REQUIRED_PARAMETERS = [ 'height', 'items' ]

class DropDownElement(ElementItem):
	def __init__(self, parameters):
		""" Init """

		# defaults for a DropDownElement
		self.width = 32
		self.height = 1
		self.contents = []
		self.current_line = 0

		# now bring in the parameters - may override the defaults
		super(DropDownElement, self).__init__(parameters)

	@classmethod
	def create(cls, parameters):
		""" create

			This function will create a DropDown. As the parameters
			are validated before the element is created then
		"""
		result = None

		# check that the parameters that are required are passed in
		if all([ parameter in parameters for parameter in REQUIRED_PARAMETERS]):

			if type(parameters['items']) == list:

				# Ok, all the required parameters exist.
				result = cls(parameters)

				if result:
					# must have a width to operate
					if 'width' not in parameters:
						result.width = 32
					else:
						result.width = parameters['width']

					# must have a width to operate
					if 'default' in parameters:
						result.current_line = parameters['default']

					# Ok, all looks good, do the setup for the TextDropDownElement
					result.height  = parameters['height']
					result.contents = parameters['items']

					# Local Element values
					result.loadDefault()

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
