#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#     _____           _ _                ______                    _
#    (_____)         | (_)              (____  \                  (_)
#       _   ____   _ | |_  ____  ___     ____)  )_   _  ____  ____ _  ____
#      | | |  _ \ / || | |/ _  |/ _ \   |  __  (| | | |/ _  |/ _  | |/ _  )
#     _| |_| | | ( (_| | ( ( | | |_| |  | |__)  ) |_| ( ( | ( ( | | ( (/ /
#    (_____)_| |_|\____|_|\_|| |\___/   |______/ \____|\_|| |\_|| |_|\____)
#                        (_____|                      (_____(_____|
#
#    file: feature
#    desc: This is the base class that all the features use.
#
#  author: peter
#    date: 30/10/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from collections import namedtuple

KeyDefinition = namedtuple('KeyDefinition',["key_value", "action", "command", "handler", "help_text"])

class Feature(object):
	def __init__(self, configuration):
		self.title = 'Default'
		self.selectable = False
		self.position = [0, 0]
		self.is_selected = False
		self.help_length = 0

	def getHelp(self, key_list):
		result = []

		if self.tab_window.isHelpEnabled():
			result = self.tab_window.getHelp()
			result += ['Feature Commands:']

			for item in key_list:
				result.append("  {:10s} {}".format(item.key_value, item.help_text))
			result.append("")

		result.append('[ ' + self.title + ' ]')
		self.help_length = len(result)

		return result

	def getPosition(self):
		return self.position

	def initialise(self, tab_window):
		self.tab_window = tab_window
		return True

	def close(self):
		self.tab_window = None

	def isSelectable(self):
		return self.selectable

	def select(self):
		self.is_selected = True

	def keyPressed(self, value, cursor_pos):
		""" cursor_pos is a list of the following:
			bufnum, lnum, col, off, curswant

			off      - is virtual offset for the cursor
			curswant - is the preferred column when move the cursor.
		"""
		redraw = False

		line = int(cursor_pos[1]) - self.help_length

		for item in self.keylist:
			if item.action == value:
				(redraw, line_no) = item.handler(line, item.action)
				break

		if redraw:
			self.renderTree()
			self.tab_window.setPosition(self.current_window, (line_no + self.help_length, int(cursor_pos[2])))

	def makeResourceDir(self, name):
		ib_config_dir = self.tab_window.getSetting('Config_directory')
		resource_dir = os.path.join(ib_config_dir, name)

		if not os.path.isdir(resource_dir):
			os.makedirs(resource_dir)

	def renderTree(self):
		pass

	def onBufferWrite(self, window_number):
		pass

	def onCommand(self, command_id, parameter, window_number):
		pass

	def onEvent(self, event_id, window_obj):
		pass

	def getTitle(self):
		return self.title

	def onMouseClick(self, line, col):
		pass

	def unselect(self):
		self.is_selected = False
		if self.tab_window is not None:
			self.position = self.tab_window.getCurrentPos()

	def error_message(self, message):
		pass

	def logging_message(self, message):
		pass

# vim: ts=4 sw=4 noexpandtab nocin ai
