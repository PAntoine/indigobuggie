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
#    file: field_element
#    desc: Base class for the field element.
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

class FieldElement(ElementItem):
	def __init__(self, parameters):
		""" Init """

		# defaults for a FieldElement
		self.width = 32
		self.read_only = False
		self.input_type = 'text'

		# now bring in the parameters - may override the defaults
		super(FieldElement, self).__init__(parameters)

	@classmethod
	def create(cls, parameters):
		""" create

			This function will create a TextFieldElement. As the parameters
			are validated before the element is created.
		"""
		result = None

		# Ok, all the required parameters exist.
		result = cls(parameters)

		# option parameters
		if 'input_type' in parameters:
			if parameters['input_type'] in ['text', 'numeric', 'secret', 'error']:
				result.input_type = parameters['input_type']

		if result:
			# error fields are always read-only
			if result.input_type == 'error':
				result.read_only = True

			result.loadDefault()

		return result


# vim: ts=4 sw=4 noexpandtab nocin ai
