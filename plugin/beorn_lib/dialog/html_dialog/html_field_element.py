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
#    file: html_field_element
#    desc: The is the HTML text field element.
#
#  author: Peter Antoine
#    date: 12/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------
from beorn_lib.dialog.base import FieldElement

class HTMLFieldElement(FieldElement):
	""" HTML Field Element """

	def renderElement(self, screen):
		""" Render Element

			This function will render the html button.
		"""
		screen.append('<div class="Field">%s</div>' % self.title)

		if self.default is not None:
			content = self.default
		else:
			content = ''

		if self.input_type == 'text':
			screen.append('<input type="text">%s</input>' % content)

		elif self.input_type == 'numeric':
			screen.append('<input type="number">%s</input>' % content)

		elif self.input_type == 'secret':
			screen.append('<input type="password">%s</input>' % content)

		elif self.input_type == 'error':
			screen.append('<input type="text" disabled class="text_error">%s</input>' % content)

		screen.append('</div>')

# vim: ts=4 sw=4 noexpandtab nocin ai
