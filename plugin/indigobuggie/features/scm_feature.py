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
#	 file: scm_feature
#	 desc: The feature manages SCM integration.
#
#  author: peter
#	 date: 24/10/2018
#---------------------------------------------------------------------------------
#					  Copyright (c) 2018 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import beorn_lib
from feature import Feature
from threading import Thread, Lock, Event

class SCMItem(object):
	__slots__ = ('scm_type', 'path', 'scm', 'submodule', 'change_list')

	def __init__(self, scm_type, path, scm, submodule, change_list):
		self.scm_type = scm_type
		self.path = path
		self.scm = scm
		self.submodule = submodule
		self.change_list = change_list

class SCMFeature(Feature):
	def __init__(self, configuration):
		result = super(SCMFeature, self).__init__(configuration)
		self.source_tree = None
		self.tab_window = None
		self.closedown = None
		self.polling_thread = None
		self.poll_period = 36.0
		self.scm_list = []
		if 'number_history_items' in configuration:
			self.number_history_items = configuration['number_history_items']
		else:
			self.number_history_items = 10

		if 'active_scm' in configuration:
			self.active_scm = configuration['active_scm']
		else:
			self.active_scm = ''

	def initialise(self, tab_window):
		result = super(SCMFeature, self).initialise(tab_window)

		# find all the supported scms
		self.find_scms()

		# start the server
		self.closedown = Event()
		self.source_tree_lock = Lock()
		self.polling_thread = Thread(target=self.polling_scm_function)
		self.polling_thread.start()

	def find_scms(self):
		found_scms = beorn_lib.scm.findRepositories(None)
		source_tree = self.tab_window.getTree('SourceTreeFeature')

		root_path = source_tree.getPath()

		for fscm in found_scms:
			for submodule in fscm.sub:
				new_scm = beorn_lib.scm.create(fscm.type, working_dir=submodule)

				if new_scm is not None:
					self.scm_list.append(SCMItem(fscm.type, submodule, new_scm, True, []))
					new_path = os.path.relpath(submodule, root_path)

					if new_path is not None and new_path[0] != '.':
						entry = source_tree.addTreeNodeByPath(new_path)
						entry.setSCM(new_scm, True)

			for primary in fscm.primary:
				new_scm = beorn_lib.scm.create(fscm.type, working_dir=primary)

				if new_scm is not None:
					self.scm_list.append(SCMItem(fscm.type, primary, new_scm, False, []))
					new_path = os.path.relpath(primary, root_path)

					if new_path is not None and new_path[0] != '.':
						entry = source_tree.addTreeNodeByPath(new_path)
						entry.setSCM(new_scm, False)

	def getItemHistoryFile(self, item, version):
		result = []

		if self.active_scm != '':
			scm_item = item.getState(self.active_scm)

			if scm_item is None or scm_item.status != 'A':
				result = scm_item.scm.getFile(item.getPath(True), version)
		else:
			for scm in self.scm_list:
				scm_item = item.getState(scm.scm_type)

				if scm_item is None or scm_item != 'A':
					result = scm.scm.getFile(item.getPath(True), version)

		return result

	def getItemHistory(self, item):
		result = (None, [])

		if self.active_scm != '':
			scm_item = item.getState(self.active_scm)

			if scm_item is None or scm_item.status != 'A':
				result = (scm_item.scm, scm_item.scm.getHistory(item.getPath(True), max_entries=self.number_history_items))
		else:
			for scm in self.scm_list:
				scm_item = item.getState(scm.scm_type)

				if scm_item is None or scm_item != 'A':
					result = (scm.scm, scm.scm.getHistory(item.getPath(True), max_entries=self.number_history_items))

		return result

	def getCurrentSCM(self):
		""" Return the active scm, if that is not set then return the
			first SCM found. Meh - not the best solution but a solution.
		"""
		result = None

		if len(self.scm_list) > 0:
			if self.active_scm in self.scm_list:
				result = self.scm_list[self.active_scm]
			else:
				result = self.scm_list[0]

		return result

	def getPatch(self, item, version):
		result = []

		if self.active_scm != '':
			scm_item = item.getState(self.active_scm)

			if scm_item is None or scm_item.status != 'A':
				result = scm_item.scm.getPatch(version)
		else:
			for scm in self.scm_list:
				scm_item = item.getState(scm.scm_type)

				if scm_item is None or scm_item != 'A':
					result = scm.scm.getPatch(version)

					if result is not None:
						break

		return result

	def polling_scm_function(self):
		for scm in self.scm_list:
			self.update_source_tree(scm)

		while not self.closedown.wait(self.poll_period):
			needs_pruning = False

			for scm in self.scm_list:
				needs_pruning = needs_pruning or self.update_source_tree(scm)

			if needs_pruning:
				# TODO: this should call the pruning function
				print "needs pruning"

	def update_source_tree(self, scm):
		result = False

		changes = scm.scm.getTreeChanges()

		source_tree = self.tab_window.getTree('SourceTreeFeature')

		diffs = set(scm.change_list) ^ set(changes)

		# check to see if the item is still on the filesystem
		for item in diffs:
			if item.status != 'M':
				entry = source_tree.findItemNode(item.path)
				if entry is not None:
					entry.checkOnFileSystem()
					result = True

		if scm.change_list == [] or len(diffs) > 0:
			self.tab_window.lockTree()

			for item in scm.change_list:
				entry = source_tree.findItemNode(item.path)
				if entry is not None:
					entry.removeItemState(scm.scm_type)
					entry.clearFlag()

			for item in changes:
				entry = source_tree.addTreeNodeByPath(item.path)
				entry.updateItemState(scm.scm_type, item.status)
				entry.setFlag('M')

			scm.change_list = changes

			self.tab_window.releaseTree()
			self.tab_window.renderTree()

		return result

	def close(self):
		self.closedown.set()
		self.polling_thread.join(5.0)

		result = super(SCMFeature, self).close()

# vim: ts=4 sw=4 noexpandtab nocin ai
