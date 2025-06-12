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
#    file: html_dialog
#    desc: The is the dialog class for the HTML dialogs (forms).
#
#  author: Peter Antoine
#    date: 26/08/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib.dialog import BaseDialog
from beorn_lib.dialog.html_dialog.html_box_element import HTMLBoxElement
from beorn_lib.dialog.html_dialog.html_field_element import HTMLFieldElement
from beorn_lib.dialog.html_dialog.html_button_element import HTMLButtonElement
from beorn_lib.dialog.html_dialog.html_drop_down_element import HTMLDropDownElement
from beorn_lib.dialog.html_dialog.html_button_list_element import HTMLButtonListElement

class HTMLDialog(BaseDialog):
	""" Text Dialog """

	def __init__(self):
		""" Initialise

			This function will initialise the HTMLDialog.
		"""
		# need to init the superclass
		super(HTMLDialog, self).__init__()

		# set the element types
		self.element_types['Button'] = HTMLButtonElement
		self.element_types['TextBox'] = HTMLBoxElement
		self.element_types['DropDown'] = HTMLDropDownElement
		self.element_types['TextField'] = HTMLFieldElement
		self.element_types['ButtonList'] = HTMLButtonListElement

	def resetDialog(self, defaults = False):
		""" Reset Dialog

			This function will throw away the current dialog buffer and rebuild
			it from the elements in the element list. It will fill the fields
			with the defaults (if present) in the elements. If this dialog has
			been filled before, unless the 'clean' flag is set then the previous
			values will be used where available.
		"""
		# Simply for the HTML reset the elements to the defaults if required.
		if defaults:
			for element in self.elements:
				element.loadDefaults()

	def getScreen(self, read_only = False):
		""" Refresh screen

			This function will create the list of strings that can be used to
			update the screen. It will also call the "system" update function
			so that it can then update the system screen.
		"""

		# TODO: use the position to order the elements - also add blank space
		#       for lines that are apart - prob only a copy to allow for grouping.
		screen = []

		for item in self.elements:
			item.renderElement(screen)

		return screen

# vim: ts=4 sw=4 noexpandtab nocin ai
