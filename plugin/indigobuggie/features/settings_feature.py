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
#    file: project_feature
#    desc: This class implements the Project Feature.
#
#    This feature controls settings for the underlying project.
#
#  author: peter
#    date: 17/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
import getpass
import platform
import beorn_lib
from feature import Feature, KeyDefinition
from settings_node import SettingsNode


class SettingsFeature(Feature):
	SETTINGS_SELECT				= 1
	SETTINGS_MOVE_TO_USER		= 2
	SETTINGS_MOVE_TO_PROJECT	= 3

	def __init__(self):
		super(SettingsFeature, self).__init__()

		self.selectable = True

		self.keylist = [KeyDefinition('<cr>', 	SettingsFeature.SETTINGS_SELECT,			False, self.handleSelectItem,	"Select an Item."),
						KeyDefinition('u', 		SettingsFeature.SETTINGS_MOVE_TO_USER,		False, self.handleMoveToUser,	"Move config item to user config."),
						KeyDefinition('p', 		SettingsFeature.SETTINGS_MOVE_TO_PROJECT,	False, self.handleMoveToProject,"Move config item to project config.")]

		self.title = "Settings"
		self.user_config = None
		self.project_config = None
		self.use_project_config = None

		self.settings = SettingsNode('general', 'SettingsFeature')

		self.menu_created = False
		self.is_new = False

	def setupConfig(self, config_object):
		for feature in self.tab_window.getFeatures():
			config = feature.getDefaultConfiguration()

			if config is not None:
				config_object.addDictionary(feature.__class__.__name__, config)

			config_object.save()

	def createSettingsMenu(self):
		for feature in self.tab_window.getFeatures():
			settings = feature.getSettingsMenu()

			if settings is not None:
				self.settings.addChildNode(settings)

		self.menu_created = True

	def initialise(self, tab_window):
		result = super(SettingsFeature, self).initialise(tab_window)

		if result:
			self.auto_create = int(tab_window.getSetting('auto_create')) == 1
			self.project_file = tab_window.getSetting('specific_file')
			self.use_project_config = int(tab_window.getSetting('use_project_config')) == 1

			# open project config.
			if self.use_project_config:
				if self.project_file is None or self.project_file == '':
					self.project_file = os.path.join(tab_window.getWorkingRoot(), "project.ipf")

				self.project_config = beorn_lib.Config(self.project_file)

				if not os.path.isfile(self.project_file) and self.auto_create:
					self.setupConfig(self.project_config)
				else:
					self.project_config.load()

			# open user config - non optional
			ib_config_dir = self.tab_window.getResourceDir()
			self.makeResourceDir('project')
			user_file = os.path.join(ib_config_dir, 'project', getpass.getuser() + '@' + platform.node())

			self.user_config = beorn_lib.Config(user_file)
			if not os.path.isfile(user_file):
				if not self.use_project_config:
					self.setupConfig(self.user_config)
				else:
					self.user_config.save()
			else:
				self.user_config.load()

		self.user_config.export()
		self.project_config.export()

		return True

	def getConfigItem(self, feature, item):
		result = None

		if self.use_project_config:
			result = self.project_config.find(feature, item)

		if result is None:
			result = self.user_config.find(feature, item)

		return result

	def setConfigItem(self, feature, item, value):
		if self.use_project_config:
			result = self.project_config.setValue(feature, item, value)

		if result is None:
			result = self.user_config.setValue(feature, item, value)

	def renderFunction(self, last_visited_node, node, value, level, direction):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		skip_children = True
		add_default = False

		if node.hasChild():
			if node.isOpen():
				marker = 'v '
				skip_children = False
				add_default = True
			else:
				marker = '> '
		else:
			marker = '  '

		if self.project_config.find(*node.getKey()) is not None:
			proj_marker = ' [p]'
		else:
			proj_marker = ' [u]'

		if add_default:
			value.append(level*'  ' + marker + node.getName())
			value.append((level+1)*'  ' + '  settings' + proj_marker)
		else:
			value.append(level*'  ' + marker + node.getName() + proj_marker)

		node.colour = len(value)

		return (node, value, skip_children)

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			if not self.menu_created:
				self.createSettingsMenu()

			contents = self.getHelp(self.keylist)
			contents += self.settings.walkTree(self.renderFunction)

			self.tab_window.setBufferContents(self.buffer_id, contents)

	def handleSelectItem(self, line_no, action):
		redraw = False
		item = self.settings.findItemWithColour(line_no)

		if item is not None:
			if item.hasChild() and (self.settings.findItemWithColour(line_no-1) is not None or line_no == 1):
				item.toggleOpen()
				redraw = True

			elif item.hasDialog():
				self.tab_window.showDialog(item)
				redraw = True
		else:
			item_next = self.settings.findItemWithColour(line_no+1)
			if item_next is not None and item_next.hasChild() and item_next.isOpen():
				item_next.toggleOpen()
				redraw = True

		return (redraw, line_no)

	def handleMoveToUser(self, line_no, action):
		redraw = False
		item = self.settings.findItemWithColour(line_no)

		if item is not None:
			if self.user_config.find(*item.getKey()) is None:
				config_item = self.project_config.find(*item.getKey())

				if config_item is not None:
					self.project_config.move(*item.getKey(), to=self.user_config)
					redraw = True

		return (redraw, line_no)

	def handleMoveToProject(self, line_no, action):
		redraw = False
		item = self.settings.findItemWithColour(line_no)

		if item is not None:
			if self.project_config.find(*item.getKey()) is None:
				config_item = self.user_config.find(*item.getKey())

				if config_item is not None:
					self.user_config.move(*item.getKey(), to=self.project_config)
					redraw = True

		return (redraw, line_no)

	def select(self):
		super(SettingsFeature, self).select()
		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_settings__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_settings')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)

	def unselect(self):
		super(SettingsFeature, self).unselect()
		self.tab_window.closeWindowByName("__ib_settings__")

	def close(self):
		self.project_config.save()
		self.user_config.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
