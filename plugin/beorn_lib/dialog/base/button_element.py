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
#    file: button_element
#    desc: This is the base class for the button element.
#
#  author: Peter Antoine
#    date: 03/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base.element import ElementItem

class ButtonElement(ElementItem):
	""" Button Element """
	def __init__(self, parameters):
		""" Init """

		# defaults for a BoxElement
		self.width = 32
		self.selected = False

		# now bring in the parameters - may override the defaults
		super(ButtonElement, self).__init__(parameters)

	@classmethod
	def create(cls, parameters):
		""" create

			This function will create a TextButtonElement.
		"""
		result = None

		# Ok, all the required parameters exist.
		result = cls(parameters)

		return result

	def getValue(self):
		""" Get Value

			This function returns value from the Element.
		"""
		return (self.name, self.selected)

# vim: ts=4 sw=4 noexpandtab nocin ai
