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
#    desc: This is the base class for the drop down element.
#
#  author: Peter Antoine
#    date: 12/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base import DropDownElement

class HTMLDropDownElement(DropDownElement):
	""" HTML DropDown Element """

	def renderElement(self, screen):
		""" Render Element

			This function will render the html button.
		"""
		screen.append('<div class="DropDown">%s</div>' % self.title)
		screen.append('<select size=%d>' % self.height)

		for index, item in enumerate(self.contents):
			if index == self.current_line:
				screen.append('<option selected="selected" value="%d">%s</option>' % (index, item))
			else:
				screen.append('<option value="%d">%s</option>' % (index, item))

		screen.append('</select>')
		screen.append('</div>')

# vim: ts=4 sw=4 noexpandtab nocin ai
