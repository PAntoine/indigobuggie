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
from settings_node import SettingsNode
from threading import Thread, Lock, Event
from collections import namedtuple, OrderedDict

MenuItem = namedtuple('MenuItem', ["getMenu", "updateConfig"])


class SCMItem(object):
	__slots__ = ('scm_type', 'path', 'scm', 'submodule', 'change_list')

	def __init__(self, scm_type, path, scm, submodule, change_list):
		self.scm_type = scm_type
		self.path = path
		self.scm = scm
		self.submodule = submodule
		self.change_list = change_list

class SCMFeature(Feature):

	def __init__(self):
		super(SCMFeature, self).__init__()
		self.source_tree = None
		self.tab_window = None
		self.closedown = None
		self.polling_thread = None
		self.poll_period = 36.0
		self.enabled_scms = []
		self.scm_list = []
		self.number_history_items = 10

		self.cheap_lock = False

	def initialise(self, tab_window):
		super(SCMFeature, self).initialise(tab_window)

		self.number_history_items = self.tab_window.getConfiguration('CodeReviewFeature', 'number_history_items')
		if self.number_history_items is None:
			self.number_history_items = 10

		self.preferred_scm = self.tab_window.getConfiguration('CodeReviewFeature', 'preferred_scm')
		if self.preferred_scm is None:
			self.preferred_scm = ''

		self.enabled_scms = self.tab_window.getConfiguration('SCMFeature', 'enabled_scms')
		if self.enabled_scms is None:
			self.enabled_scms = []

		# start the server
		self.closedown = Event()
		self.source_tree_lock = Lock()
		self.polling_thread = Thread(target=self.polling_scm_function)
		self.polling_thread.start()

	def getSCMByName(self, name):
		result = None

		for scm in self.scm_list:
			if scm.scm_type == name:
				result = scm.scm
				break

		return result

	def buildDialog(self, settings):
		result = None

		config_item = self.tab_window.getConfiguration(*settings.getKey())
		supported = beorn_lib.scm.getSupportedSCMs()

		for item in supported:
			if item.type == settings.name:
				dialog_items = item.cls.getDialogLayout()

				if dialog_items is not None:
					dialog_layout = []
					line = 1

					for item in dialog_items:
						if item[0] == 'ButtonList':

							button_list = []

							for entry in item[4]:
								if type(config_item[entry[0]]) == str:
									value = 'True' == config_item[entry[0]]
								else:
									value = config_item[entry[0]]

								button_list.append((value, entry[1]))

							parameters = {	'name':			item[2],
											'title':		item[3],
											'x':			4,
											'y':			line,
											'width':		64,
											'items':		button_list,
											'type':			item[1]}

							line += len(item[4]) + 1
						else:
							parameters = {	'name':			item[2],
											'title':		item[3],
											'x':			4,
											'y':			line,
											'width':		64,
											'default':		config_item[item[2]],
											'input_type':	item[1]}

						dialog_layout.append(beorn_lib.dialog.Element(item[0], parameters))

						line += 1

					line += 1
					dialog_layout.append(beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': line}))
					dialog_layout.append(beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 35, 'y': line}))

					result = beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

				break

		return result

	def resultDialog(self, settings, result):
		config_item = self.tab_window.getConfiguration(*settings.getKey())

		if config_item is not None:
			for item in result:
				if item in config_item:
					config_item[item] = result[item]

	def getDialog(self, settings):
		scm_list = []
		active_list = []
		button_list = []
		for scm in beorn_lib.scm.getSupportedSCMs():
			selected = (scm.type == self.tab_window.getConfiguration('SCMFeature', 'preferred_scm'))
			scm_list.append((selected, scm.type))

			value = scm.type in self.enabled_scms
			active_list.append((value, scm.type))

		dialog_layout = [
			beorn_lib.dialog.Element('ButtonList',{'name': 'preferred_scm',			'title':'Default SCM', 'x':4, 'y':1, 'width':64, 'items': scm_list, 'type': 'single'}),
			beorn_lib.dialog.Element('TextField', {'name': 'poll_period',			'title':'    SCM Refresh Time', 'x':4, 'y':len(scm_list) + 3, 'width':6,  'default': str(int(self.poll_period)) ,'input_type':'numeric'}),
			beorn_lib.dialog.Element('TextField', {'name': 'number_history_items',	'title':'Number History Items', 'x':4, 'y':len(scm_list) + 4, 'width':6,  'default': str(self.number_history_items) ,'input_type':'numeric'}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'enabled_scms',			'title':'  Enabled SCMs', 'x':4, 'y':(len(scm_list)) + 6, 'width':64, 'items': active_list, 'type': 'multiple'}),
			beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': len(scm_list) + 7 + len(button_list) + 1}),
			beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 35, 'y': len(scm_list) + 7 + len(button_list) + 1})
		]

		return beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

	def p4ResultsFunction(self, settings, results):
		(feature, base_key) = settings.getKey()

		for item in results:
			if item not in ['ok', 'cancel']:
				key = list(base_key)
				if item != 'options':
					key.append(item)
					self.tab_window.setConfiguration(feature, key, results[item].rstrip())
				else:
					key.append('start_server')
					self.tab_window.setConfiguration(feature, key, results[item][0])

	def resultsFunction(self, settings, results):
		if settings.getName() == 'P4':
			self.p4ResultsFunction(settings, results)

		elif settings.getName() == "Git":
			self.p4ResultsFunction(settings, results)

		else:
			if 'poll_period' in results and int(results['poll_period']) != int(self.poll_period):
				self.poll_period = float(results['poll_period'])
				self.tab_window.setConfiguration('SCMFeature', 'poll_period', int(self.preferred_scm))

			if 'number_history_items' in results and int(results['number_history_items']) != self.number_history_items:
				self.number_history_items = int(results['number_history_items'])
				self.tab_window.setConfiguration('SCMFeature', 'number_history_items', self.number_history_items)

			supported_list = beorn_lib.scm.getSupportedSCMs()
			enabled_list = []
			if 'enabled_scms' in results:
				for index, item in enumerate(results['enabled_scms']):
					# Cannot enable an SCM that is not supported.
					if item:
						enabled_list.append(supported_list[index].type)

				li = ','.join(enabled_list)
				if li != self.enabled_scms:
					self.enabled_scms = li
					self.tab_window.setConfiguration('SCMFeature', 'enabled_scms', li)

			# check if active scm is and active scm
			# Only set it if it is an enabled SCM.
			self.preferred_scm = None
			for index, scm in enumerate(supported_list):
				if results['preferred_scm'][index] and scm.type in enabled_list:
					self.preferred_scm = scm.type

			if self.preferred_scm is None and len(enabled_list) > 0:
				self.preferred_scm = enabled_list[0]

			self.tab_window.setConfiguration('SCMFeature', 'preferred_scm', self.preferred_scm)

	def getDefaultConfiguration(self):
		engines = OrderedDict()
		names = []
		active = ''

		for scm in beorn_lib.scm.getSupportedSCMs():
			names.append(scm.type)
			engines[scm.type] = scm.cls.getConfiguration()

			if active == '':
				active = scm.type

		return {'supported_scms': names,
				'enabled_scms': [],
				'preferred_scm': active,
				'poll_period': self.poll_period,
				'number_history_items': self.number_history_items,
				'engines': engines}

	def getSettingsMenu(self):
		root = SettingsNode('SCM', 'SCMFeature', None, self.getDialog, self.resultsFunction)

		if len(self.scm_list) == 0:
			self.find_scms()

		supported = self.tab_window.getConfiguration('SCMFeature', 'supported_scms')

		if supported is not None:
			for engine in beorn_lib.scm.getSupportedSCMs():
				if engine.type in supported:
					root.addChildNode(SettingsNode(engine.type, 'SCMFeature', ['engines', engine.type], self.buildDialog, self.resultsFunction))

		return root

	def getActiveScm(self):
		""" return the first found scm, preferred_scm type first """
		result = None

		for item in self.scm_list:
			if item.scm_type == self.preferred_scm:
				result = item.scm
				break

		if result is None:
			for item in self.scm_list:
				if not item.submodule:
					result = item.scm
					break

		return result

	def find_scms(self):
		if not self.cheap_lock and len(self.scm_list) == 0:
			self.cheap_lock = True

			found_scms = beorn_lib.scm.findRepositories(None)
			st_feature = self.tab_window.getFeature('SourceTreeFeature')
			source_tree = st_feature.getTree()

			if source_tree is not None:
				root_path = source_tree.getPath()
				supported = self.tab_window.getConfiguration('SCMFeature', 'supported_scms')

				for fscm in found_scms:
					if fscm.type in supported:
						config = self.tab_window.getConfiguration('SCMFeature', ['engines', fscm.type])

						if 'password' not in config:
							config['password'] = ''

						if 'user_name' not in config:
							config['user_name'] = ''

						for submodule in fscm.sub:
							new_scm = beorn_lib.scm.create(	fscm.type,
															working_dir=submodule,
															server_url=config['server'],
															user_name=config['user_name'],
															password=config['password'])

							if new_scm is not None:
								self.scm_list.append(SCMItem(fscm.type, submodule, new_scm, True, []))
								new_path = os.path.relpath(submodule, root_path)

								if new_path is not None:
									if new_path[0] != '.':
										entry = source_tree.addTreeNodeByPath(new_path)
										if entry is not None:
											entry.setSCM(new_scm, True)
									else:
										source_tree.setSCM(new_scm, True)

						for primary in fscm.primary:
							new_scm = beorn_lib.scm.create(	fscm.type,
															working_dir=primary,
															server_url=config['server'],
															user_name=config['user_name'],
															password=config['password'])

							if new_scm is not None:
								self.scm_list.append(SCMItem(fscm.type, primary, new_scm, False, []))
								new_path = os.path.relpath(primary, root_path)

								if new_path is not None:
									if new_path[0] != '.':
										entry = source_tree.addTreeNodeByPath(new_path)
										if entry is not None:
											entry.setSCM(new_scm, False)
									else:
										source_tree.setSCM(new_scm, False)

		self.cheap_lock = False

	def getItemHistory(self, item):
		result = (None, [])

		scm = item.findSCM()

		if scm is not None:
			m = item.getState(scm.getType())
			if scm_item is None or scm_item.status != 'A':
				path = item.getPath(True)
				result = (scm, scm.getHistory(path, max_entries=self.number_history_items))

		return result

	def findSCMForPath(self, path):
		""" Return a known SCM which contains the given path """
		result = None

		if len(self.scm_list) > 0:
			for scm in self.scm_list:
				break
				# TODO: this needs fixing.
				#if scm.scm.pathInSCM(path):
				#	result = scm.scm
				#	break

		return result

	def listSCMs(self):
		for scm in self.scm_list:
			yield scm

	def getCurrentSCM(self):
		""" Return the active scm, if that is not set then return the
			first SCM found. Meh - not the best solution but a solution.
		"""
		result = None

		if len(self.scm_list) > 0:
			if self.preferred_scm in self.scm_list:
				result = self.scm_list[self.preferred_scm]
			else:
				result = self.scm_list[0]

		return result

	def getPatch(self, item, version):
		result = []

		if self.preferred_scm != '':
			scm_item = item.getState(self.preferred_scm)

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
		if len(self.scm_list) == 0:
			self.find_scms()

		for scm in self.scm_list:
			self.update_source_tree(scm)

		while not self.closedown.wait(self.poll_period):
			needs_pruning = False

			for scm in self.scm_list:
				needs_pruning = needs_pruning or self.update_source_tree(scm)

			if needs_pruning:
				# TODO: this should call the pruning function
				pass

	def update_source_tree(self, scm):
		result = False

		changes = scm.scm.getTreeChanges()

		source_tree_feature = self.tab_window.getFeature('SourceTreeFeature')

		if source_tree_feature is not None:
			source_tree = source_tree_feature.getTree()

			if source_tree is not None:
				diffs = set(scm.change_list) ^ set(changes)

				if len(diffs) > 0:
					# lets get the root item for the scm
					scm_root = source_tree.findItemNode(scm.scm.getRoot())

					if scm_root is not None:
						# check to see if the item is still on the filesystem
						for item in diffs:
							if item.status != 'M':
								entry = scm_root.findItemNode(item.path)
								if entry is not None:
									result = not entry.checkOnFileSystem()

						if len(diffs) > 0:
							self.tab_window.lockTree()

							# remove old status
							for item in scm.change_list:
								entry = scm_root.findItemNode(item.path)
								if entry is not None:
									entry.removeItemState(scm.scm_type)
									entry.clearFlag()

							# add new status
							for item in changes:
								entry = scm_root.addTreeNodeByPath(item.path)
								if entry is not None:
									entry.updateItemState(scm, item)
									entry.setFlag('M')

							scm.change_list = changes

							self.tab_window.releaseTree()
							source_tree_feature.setNeedsRedraw()

		return result

	def close(self):
		self.closedown.set()
		self.polling_thread.join(5.0)

		super(SCMFeature, self).close()

# vim: ts=4 sw=4 noexpandtab nocin ai
