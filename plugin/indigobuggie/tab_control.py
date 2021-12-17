#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#	  _____			  _ _				 ______					   _
#	 (_____)		 | (_)				(____  \				  (_)
#		_	____   _ | |_  ____  ___	 ____)	)_	 _	____  ____ _  ____
#	   | | |  _ \ / || | |/ _  |/ _ \	|  __  (| | | |/ _	|/ _  | |/ _  )
#	  _| |_| | | ( (_| | ( ( | | |_| |	| |__)	) |_| ( ( | ( ( | | ( (/ /
#	 (_____)_| |_|\____|_|\_|| |\___/	|______/ \____|\_|| |\_|| |_|\____)
#						 (_____|					  (_____(_____|
#
#	 file: tab_control
#	 desc: Tab Control Class
#
#	 This class controls the vim tab. It handles the setup of the windows
#	 within the tab and handles a data set that the plugin will use to enable
#	 multiple views.
#
#  author: peter
#	 date: 01/10/2018
#---------------------------------------------------------------------------------
#					  Copyright (c) 2018 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import vim
from . import features
from .tab_window import TabWindow


class TabControl(object):
	def __init__(self):
		self.tab_list = {}
		self.tab_id = 1
		self.current_tab = vim.current.tabpage

		# testing changer 1.

	def getTabID(self):
		result = self.tab_id
		self.tab_id += 1
		return result

	def getTab(self, tab_id):
		return self.tab_list[tab_id]

	def addTab(self, directory=None, project=None, feature_list=[]):
		result = False

		if directory is not None:
			dir_item = os.path.realpath(directory)
			name = os.path.basename(dir_item)
		else:
			name = project

		try:
			# create the tab
			vim.command("tabnew")

			# create the TabWindow
			tab_id = self.getTabID()

			self.tab_list[tab_id] = TabWindow(name, tab_id, vim.current.tabpage.number)

			# create the settings feature - always attached first.
			self.tab_list[tab_id].attachFeature(features.SettingsFeature(directory, name))

			# now create the features for the tabwindow
			for feature in feature_list:
				if hasattr(features, feature):
					new_feature = getattr(features, feature)()

					if new_feature is not None:
						self.tab_list[tab_id].attachFeature(new_feature)

			self.tab_list[tab_id].initialiseFeatures()

			# set the tab variables
			vim.current.tabpage.vars['__tab_id__'] = tab_id
			vim.current.tabpage.vars['__tab_name__'] = name

			self.tab_list[tab_id].selectFeature(feature_list[1])

			result = True

		except vim.error:
			pass

		return result

	def switchTab(self, index):
		result = False

		index = int(index)

		if index in self.tab_index:
			tab = self.tab_list[self.tab_index[index]]

			try:
				vim.command("tabnext " + str(tab.tab_number))
				vim.command("cd " + tab.root)

				result = True

			except vim.error:
				pass

		return result

	def getTimerHandler(self, timer_id):
		for tab in self.tab_list:
			if self.tab_list[tab].onTimerCallbackHandler(int(timer_id)):
				break

	def getCurrentTab(self):
		result = None

		if "__tab_id__" in vim.current.tabpage.vars:
			curr_id = vim.current.tabpage.vars['__tab_id__']

			result = self.tab_list[curr_id]

		return result

	def closeTab(self, tab_nr):
		""" This function is called when any tab is closed. We will
			check to see if it is one of ours, if so then remove all
			the features and stop any background tasks.
		"""
		for tab in self.tab_list:
			if tab_nr == self.tab_list[tab].getTabNumber():
				# Ok, we have the tab - it has been closed by vim and
				# no longer exists.
				self.tab_list[tab].close()

	def toggleHelp(self):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.toggleHelp()

	def keyPressed(self, value, cursor_pos):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.keyPressed(value, cursor_pos)

	def selectFeature(self, feature):
		if feature == 'help':
			self.toggleHelp()
		else:
			tab = self.getCurrentTab()

			if tab is not None:
				tab.selectFeature(feature)

	def unselectCurrentFeature(self):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.unselectCurrentFeature()

	def selectCurrentFeature(self):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.selectCurrentFeature()

	def getFeature(self, feature_name):
		result = None

		tab = self.getCurrentTab()

		if tab is not None:
			result = tab.getFeature(feature_name)

		return result

	def closeAllTabs(self):
		for tab in self.tab_list:
			self.tab_list[tab].close()

	def onTabEntered(self, tab_nr):
		# This gets called when a window is entered.
		if tab_nr in vim.tabpages:
			if "__tab_id__" in vim.tabpages[tab_nr].vars:
				tab_id = vim.tabpages[tab_nr].vars["__tab_id__"]
				self.tab_list[tab_id].entered()

	def onTabLeave(self, tab_nr):
		# This gets called when a tab is left.
		if tab_nr in vim.tabpages:
			if "__tab_id__" in vim.tabpages[tab_nr].vars:
				tab_id = vim.tabpages[tab_nr].vars["__tab_id__"]
				self.tab_list[tab_id].left()

	def onBufferWrite(self, window_number):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.onBufferWrite(window_number)

	def onCommand(self, feature_name, command_id, parameter, window_number):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.onCommand(feature_name, command_id, parameter, window_number)

	def onEventHandler(self, feature_name, event_id, window_obj):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.onEventHandler(feature_name, event_id, window_obj)

	def onMouseClickHandler(self):
		tab = self.getCurrentTab()

		if tab is not None:
			tab.onMouseClickHandler()

	def onServerCallback(self, tab_id, server_id, message):
		tab_id_int = int(tab_id)

		if tab_id_int in self.tab_list:
			self.tab_list[tab_id_int].onServerCallback(server_id, message)

# vim: ts=4 sw=4 noexpandtab nocin ai
