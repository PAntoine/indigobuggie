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
#    file: html_button_list_element
#    desc: This is the base class for a button list element.
#
#  author: Peter Antoine
#    date: 05/09/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog.base import ButtonListElement

class HTMLButtonListElement(ButtonListElement):
	""" HTML Button List Element """

	def renderElement(self, screen):
		""" Render Element

			This function will render the html button.
		"""
		screen.append('<div class="ButtonList">%s</div>' % self.title)
		screen.append('<div class="button-holder">')

		for index, item in enumerate(self.items):
			button_id = "%s-%d" % (self.name, index)
			button_set = "%s-set" % (self.name)

			if item[0]:
				screen.append('<input type="radio" id="%s" name="%s" class="regular-radio big-radio" checked /><label for="%s">%s</label><br />' % (button_id, button_set, button_id, self.title))
			else:
				screen.append('<input type="radio" id="%s" name="%s" class="regular-radio big-radio"/><label for="%s">%s</label><br />' % (button_id, button_set, button_id, self.title))

		screen.append('</div>')
		screen.append('</div>')

# vim: ts=4 sw=4 noexpandtab nocin ai
