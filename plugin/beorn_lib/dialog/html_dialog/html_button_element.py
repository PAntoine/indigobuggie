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
#    file: html_button_element
#    desc: The class defines the HTML button.
#
#  author: Peter Antoine
#    date: 03/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base import ButtonElement

class HTMLButtonElement(ButtonElement):
	""" HTML Button Element """

	def __init__(self, parameters):
		""" Init """

		# defaults for a BoxElement
		self.link = None

		# now bring in the parameters - may override the defaults
		super(HTMLButtonElement, self).__init__(parameters)

	def renderElement(self, screen):
		""" Render Element

			This function will render the html button.
		"""
		if self.link is None:
			screen.append("<a href='/%s' class='button'>%s</a>" % (self.title, self.title))
		else:
			screen.append("<a href='%s' class='button'>%s</a>" % (self.link, self.title))

# vim: ts=4 sw=4 noexpandtab nocin ai
