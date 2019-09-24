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
#    file: settings_node
#    desc: This is the settings node for use in the settings menu.
#
#  author: peter
#    date: 15/04/2019
#---------------------------------------------------------------------------------
#                     Copyright (c) 2019 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from beorn_lib import NestedTreeNode


class SettingsNode(NestedTreeNode):
	def __init__(self, name, feature_name, config_key=None, dialog_function=None, results_function=None):
		super(SettingsNode, self).__init__()
		self.feature_name = feature_name
		self.name = name
		self.config_key = config_key
		self.dialog_function = dialog_function
		self.results_function = results_function

	def getKey(self):
		return (self.feature_name, self.config_key)

	def getName(self):
			return self.name

	def getDialog(self, item):
		if self.dialog_function is None:
			return None
		else:
			return self.dialog_function(item)

	def handleResults(self, results):
		if self.results_function is None:
			return None
		else:
			return self.results_function(self, results)

	def hasDialog(self):
		return (self.dialog_function is not None and self.results_function is not None)

# vim: ts=4 sw=4 noexpandtab nocin ai
