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
from .feature import Feature, KeyDefinition
from .settings_node import SettingsNode
from collections import namedtuple, OrderedDict


class SettingsFeature(Feature):
	SETTINGS_SELECT				= 1
	SETTINGS_MOVE_TO_USER		= 2
	SETTINGS_MOVE_TO_PROJECT	= 3

	def __init__(self, root_directory=None, project_name=None):
		super(SettingsFeature, self).__init__()

		self.selectable = True

		self.keylist = [KeyDefinition('<cr>', 	SettingsFeature.SETTINGS_SELECT,			False, self.handleSelectItem,	"Select an Item."),
						KeyDefinition('u', 		SettingsFeature.SETTINGS_MOVE_TO_USER,		False, self.handleMoveToUser,	"Move config item to user config."),
						KeyDefinition('p', 		SettingsFeature.SETTINGS_MOVE_TO_PROJECT,	False, self.handleMoveToProject,"Move config item to project config.")]

		self.title = "Settings"
		self.project_name = project_name
		self.user_config = None
		self.project_config = None
		self.use_project_config = None

		self.using_default_user_config = True
		self.using_default_project_config = True

		if root_directory is None:
			self.root_directory = None
		elif root_directory[0] == '~':
			self.root_directory = os.expanduser(root_directory)
		else:
			self.root_directory = os.path.abspath(root_directory)

		self.settings = SettingsNode('general', 'SettingsFeature')

		self.menu_created = False
		self.is_new = False

	def DefaultSettingsConfigration(self):
		enabled_features = []

		for feature in self.tab_window.getFeatures():
			enabled_features.append(feature.__class__.__name__)

		# create the feature select keys - choose the first letter
		# in the feature names that has not been used, lower then
		# upper case. These can be changed by the user when they
		# want to.
		select_keys = OrderedDict()

		used_letters = ['h']
		select_keys['help'] = "<leader>h"

		for feature in self.tab_window.getFeatures():
			if feature.isSelectable():
				name = feature.__class__.__name__
				selected_letter = ''

				for letter in name:
					if letter.lower() not in used_letters:
						selected_letter = letter.lower()
						used_letters.append(letter.lower())
						break

					elif letter.upper() not in used_letters:
						selected_letter = letter.upper()
						used_letters.append(letter.upper())
						break

				select_keys[feature.__class__.__name__] = "<leader>" + selected_letter

		return {'root_directory': self.root_directory,
				'do_not_move_cwd':	False,
				'auto_create':		True,
				'enabled_features':	enabled_features,
				'select_keys': select_keys};

	def setupConfig(self, config_object):
		config_object.addDictionary("SettingsFeature", self.DefaultSettingsConfigration())

		for feature in self.tab_window.getFeatures():
			config = feature.getDefaultConfiguration()

			if config is not None:
				config_object.addDictionary(feature.__class__.__name__, config)

	def getDialog(self, settings):
		system_settings = [	(self.tab_window.getConfiguration('SettingsFeature', 'do_not_move_cwd'),	"Hide Dot files."),
							(self.tab_window.getConfiguration('SettingsFeature', 'auto_create'),		"Show hidden files.") ]

		enabled_features = []

		enabled = self.tab_window.getConfiguration('SettingsFeature', 'enabled_features')

		if len(enabled) == 0:
			for feature in self.tab_window.getFeatures():
				# if it is not enabled then just turn it on.
				enabled_features.append((True, feature.__class__.__name__))
		else:
			for feature in self.tab_window.getFeatures():
				if feature.__class__.__name__ in enabled:
					enable = True
				else:
					enable = False

				enabled_features.append((enable, feature.__class__.__name__))

		dialog_layout = [
			beorn_lib.dialog.Element('TextField', {'name': 'root_directory',	'title': 'Root Directory  ',	'x': 10, 'y': 1, 'width':80, 'default': self.root_directory}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'settings',			'title': 'Settings',			'x': 15, 'y': 3, 'width':64, 'items': system_settings,  'type': 'multiple'}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'enabled_features',	'title': 'Enabled Features',	'x': 15, 'y': 5+len(system_settings), 'width':64, 'items': enabled_features, 'type': 'multiple'})]

		# add the selection key for the features.
		select_keys = self.tab_window.getConfiguration('SettingsFeature', 'select_keys')

		if select_keys is None:
			# need to get the default configuration here
			default = self.DefaultSettingsConfigration()
			select_keys = default['select_keys']

		if 'help' in select_keys:
			del select_keys['help']

		index = 7+len(system_settings) + len(enabled_features)
		for feature in select_keys:
			feat = self.tab_window.getFeature(feature)

			if feat is not None and feat.isSelectable():
				name = '  Feature Select ' + feature

				dialog_layout.append(beorn_lib.dialog.Element('TextField', {'name': 'key_' + feature, 'title': name.ljust(35),	'x': 10, 'y': index, 'width':50, 'default': select_keys[feature]}))
				index += 1

		dialog_layout += [
			beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': 5 + len(dialog_layout) + len(system_settings) + len(enabled_features)}),
			beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 36, 'y': 5 + len(dialog_layout) + len(system_settings) + len(enabled_features)})
		]

		return beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

	def resultsFunction(self, settings, results):
		if self.root_directory != results['root_directory']:
			self.root_directory = results['root_directory']
			self.tab_window.setConfiguration('SettingsFeature', 'root_directory', self.root_directory)

		enabled_features = []
		for index, feature in enumerate(self.tab_window.getFeatures()):
			if results['enabled_features'][index]:
				enabled_features.append(feature.__class__.__name__)

		self.tab_window.setConfiguration('SettingsFeature', 'enabled_features', enabled_features)

		self.tab_window.setConfiguration('SettingsFeature', 'do_not_move_cwd',	results['settings'][0])
		self.tab_window.setConfiguration('SettingsFeature', 'auto_create',		results['settings'][1])

		select_keys = OrderedDict()

		select_keys['help'] = "<leader>h"

		for feature in results:
			if feature[0:4] == 'key_':
				select_keys[feature[4:]] = results[feature]

		self.tab_window.setConfiguration('SettingsFeature', 'select_keys', select_keys)

	def createSettingsMenu(self):
		self.settings.addChildNode(SettingsNode('Settngs', 'SettingsFeature', None, self.getDialog, self.resultsFunction))

		for feature in self.tab_window.getFeatures():
			settings = feature.getSettingsMenu()

			if settings is not None:
				self.settings.addChildNode(settings)

		self.menu_created = True

	def initialise(self, tab_window):
		result = super(SettingsFeature, self).initialise(tab_window)

		if result:
			self.project_file = os.path.join(self.tab_window.getResourceDir(self.project_name), 'project.ipf')
			self.use_project_config = int(tab_window.getSetting('use_project_config')) == 1

			# open project config - if we are using it.
			if self.use_project_config:
				if os.path.isfile(self.project_file):
					self.project_config = beorn_lib.Config(self.project_file)
					self.project_config.load()
					self.using_default_project_config = True

				else:
					self.project_config = beorn_lib.Config(self.project_file)
					self.setupConfig(self.project_config)

			# open user config - non optional
			ib_config_dir = self.tab_window.getResourceDir(self.project_name)
			self.makeResourceDir('project')
			user_file = os.path.join(ib_config_dir, 'project', getpass.getuser() + '@' + platform.node())

			self.user_config = beorn_lib.Config(user_file)
			if os.path.isfile(user_file) and not self.use_project_config:
				self.user_config.load()
			else:
				self.setupConfig(self.user_config)
				self.using_default_user_config = True

			# set the root directory from the configuration.
			rd = os.path.abspath(self.getConfigItem("SettingsFeature", "root_directory"))

			if rd is not None:
				self.root_directory = rd
				tab_window.setCWD(self.root_directory)

		return True

	def getConfigItem(self, feature, item):
		result = None

		if self.use_project_config:
			result = self.project_config.find(feature, item)

		if result is None and self.user_config is not None:
			result = self.user_config.find(feature, item)

		return result

	def setConfigItem(self, feature, item, value):
		if self.use_project_config:
			result = self.project_config.setValue(feature, item, value)

		if result is None:
			result = self.user_config.setValue(feature, item, value)

	def renderFunction(self, last_visited_node, node, value, level, direction, parameter):
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
		auto_create = self.tab_window.getConfiguration('SettingsFeature','auto_create')

		if self.use_project_config and (not self.using_default_project_config or auto_create):
			self.project_config.save()

		if not self.use_project_config and (not self.using_default_user_config or auto_create):
			self.user_config.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
