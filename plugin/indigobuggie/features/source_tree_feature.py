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
#    file: source_tree_feature
#    desc: This feature handles the base source tree.
#
#  author: peter
#    date: 09/10/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import beorn_lib
from .history_node import HistoryNode
from .settings_node import SettingsNode
from queue import Queue
from .feature import Feature, KeyDefinition, UpdateItem
from threading import Thread

LINE_LEVEL_SPACE	= '  '

# render markers
MARKER_ADDED		= 0
MARKER_DELETED		= 1
MARKER_CHANGED		= 2
MARKER_SAME			= 3
MARKER_CLOSED		= 4
MARKER_OPEN			= 5
MARKER_UNKNOWN		= 6
MARKER_SUBMODULE	= 7
MARKER_SUBGIT		= 8
MARKER_SUBREPO		= 9
MARKER_LINK			= 10
MARKER_BADLINK		= 11
MARKER_OUT_OF_DATE	= 12

unicode_markers = ['+', '✗', '±', ' ', '▸', '▾', '?', 'm', 'g', 'r', 'l', 'ł', 'U']
ascii_markers	= ['+', 'x', '~', ' ', '>', 'v', '?', 'm', 'g', 'r', 'l', 'B', 'U']


class SourceTreeFeature(Feature):
	# User actions
	SOURCE_TREE_SELECT			= 1
	SOURCE_TREE_HISTORY 		= 2
	SOURCE_TREE_HISTORY_ALL		= 3
	SOURCE_TREE_PATCH			= 4
	SOURCE_TREE_HISTORY_FILE 	= 5
	SOURCE_TREE_CLOSE_ALL_DIFFS	= 6
	SOURCE_TREE_CLOSE_ITEM		= 7
	SOURCE_TREE_CODE_REVIEW		= 8
	SOURCE_TREE_DIFF_FILE		= 9
	SOURCE_TREE_CLOSE_ITEMS_ALL = 10

	# System event IDs
	SOURCE_TREE_FILE_LOADED_EVENT	= 1		# need to check for file changes.
	SOURCE_TREE_USER_STOPPED_TYPING	= 2		# time for house keeping, refresh the menu.

	# Display order
	SOURCE_TREE_DISPLAY_ORDER_NORMAL			= beorn_lib.NestedTreeNode.TREE_WALK_NORMAL			# Normal alphabetic order
	SOURCE_TREE_DISPLAY_ORDER_DIRECTORY_FIRST	= beorn_lib.NestedTreeNode.TREE_WALK_PARENTS_FIRST	# directories first
	SOURCE_TREE_DISPLAY_ORDER_DIRECTORY_LAST	= beorn_lib.NestedTreeNode.TREE_WALK_PARENTS_LAST	# directories last

	def __init__(self):
		super(SourceTreeFeature, self).__init__()
		self.title = "Source Tree"

		self.keylist = [KeyDefinition('<cr>', 	SourceTreeFeature.SOURCE_TREE_SELECT,			False,	self.handleSelectItem,		"Select a tree item."),
						KeyDefinition('h',		SourceTreeFeature.SOURCE_TREE_HISTORY,			False,	self.handleItemHistory,		"Show the history of an item."),
						KeyDefinition('H',		SourceTreeFeature.SOURCE_TREE_HISTORY_ALL,		False,	self.handleItemHistoryAll,	"Show the history of an item for SCMS."),
						KeyDefinition('p',		SourceTreeFeature.SOURCE_TREE_PATCH,			False,	self.handleShowPatch,		"Show the patch for a history item."),
						KeyDefinition('o',		SourceTreeFeature.SOURCE_TREE_HISTORY_FILE,		False,	self.handleOpenHistoryItem,	"Open the historical version of the file."),
						KeyDefinition('D',		SourceTreeFeature.SOURCE_TREE_CLOSE_ALL_DIFFS,	False,	self.handleCloseDiffs,		"Close all the open diffs."),
						KeyDefinition('d',		SourceTreeFeature.SOURCE_TREE_DIFF_FILE,		False,	self.handleDiffFileItem,	"Diff the file against the current head."),
						KeyDefinition('x',		SourceTreeFeature.SOURCE_TREE_CLOSE_ITEM,		False,	self.handleCloseItem,		"Close the tree items."),
						KeyDefinition('X',		SourceTreeFeature.SOURCE_TREE_CLOSE_ITEMS_ALL,	False,	self.handleCloseItemAll,	"Close all the parents of the item."),
						KeyDefinition('c',		SourceTreeFeature.SOURCE_TREE_CODE_REVIEW,		False,	self.handleCodeReview,		"Create a Code review for the history Item."),
					]

		self.selectable = True

		self.source_tree = None
		self.tab_window = None
		self.buffer_id = None
		self.current_window = None

		self.diff_file_path = None
		self.diff_window_list = []
		self.render_items = []
		self.needs_redraw = False

		self.created = False

		self.update_queue = Queue()
		self.update_thread = Thread(target=self.updateTreeThread, args=(self.update_queue,))

	def getDialog(self, settings):
		suffix_string_list = ','.join(self.ignore_suffixes)
		directory_string_list = ','.join(self.ignore_directories)

		display_order = []

		display_index = int(self.tab_window.getConfiguration('SourceTreeFeature', 'display_order'))
		for index, text in enumerate(["Alphabetic Ordering", "Directories First", "Files First"]):
			if index == display_index:
				display_order.append((True, text))
			else:
				display_order.append((False, text))

		button_list = [	(self.tab_window.getConfiguration('SourceTreeFeature', 'hide_dot_files'),		"Hide Dot files."),
						(self.tab_window.getConfiguration('SourceTreeFeature', 'show_hidden_files'),	"Show hidden files."),
						(self.tab_window.getConfiguration('SourceTreeFeature', 'follow_current_file'),	"Show the current file in the source tree.") ]

		dialog_layout = [
			beorn_lib.dialog.Element('TextField', {'name': 'ignore_suffixes',		'title': 'Suffix Ignore List   ',	'x': 10,	'y': 1, 'default': suffix_string_list}),
			beorn_lib.dialog.Element('TextField', {'name': 'ignore_directories',	'title': 'Directory Ignore List',	'x': 10,	'y': 2, 'default': directory_string_list}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'settings',				'title': 'Settings',				'x': 15,	'y': 3, 'width':64,'items': button_list, 'type': 'multiple'}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'display_order',			'title': 'Directory Tree Order',	'x':4,		'y': 5 + len(button_list), 'width':64, 'items': display_order, 'type': 'single'}),

			beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': 9 + len(button_list)}),
			beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 36, 'y': 9 + len(button_list)})
		]

		return beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

	def resultsFunction(self, settings, results):
		ign_suff = results['ignore_suffixes'].split(',')

		self.tab_window.setConfiguration('SourceTreeFeature', 'display_order', results['display_order'].index(True))

		if self.ignore_suffixes != ign_suff:
			self.ignore_suffixes = ign_suff
			self.tab_window.setConfiguration('SourceTreeFeature', 'ignore_suffixes', ign_suff)

		ign_dirs = results['ignore_directories'].split(',')

		if self.ignore_directories != ign_dirs:
			self.ignore_directories = ign_dirs
			self.tab_window.setConfiguration('SourceTreeFeature', 'ignore_directories', ign_dirs)

		self.tab_window.setConfiguration('SourceTreeFeature', 'hide_dot_files',		 results['settings'][0])
		self.tab_window.setConfiguration('SourceTreeFeature', 'show_hidden_files',	 results['settings'][1])
		self.tab_window.setConfiguration('SourceTreeFeature', 'follow_current_file', results['settings'][2])

	def getDefaultConfiguration(self):
		return  {	'ignore_suffixes': ['swp', 'swn', 'swo', 'pyc', 'o'],
					'ignore_directories': ['.git', '.indigobuggie' ],
					'display_order': SourceTreeFeature.SOURCE_TREE_DISPLAY_ORDER_NORMAL,
					'hide_dot_files': True,
					'show_hidden_files': False,
					'follow_current_file': True}

	def getSettingsMenu(self):
		return SettingsNode('Source Tree', 'SourceTreeFeature', None, self.getDialog, self.resultsFunction)

	def getUpdateQueue(self):
		return self.update_queue

	def getOrder(self):
		return int(self.tab_window.getConfiguration('SourceTreeFeature', 'display_order'))

	def clearSourceTreeChange(self, scm_root, scm_name, change_item):
		result = False

		scm_root_item = self.source_tree.findItemNode(scm_root)

		if scm_root_item is not None:
			entry = scm_root_item.findItemNode(change_item.path)

			if entry is not None:
				state = entry.getState(scm_name)

				# The also clears the flags on the parents.
				entry.removeItemState(scm_name)

				if state.status == 'A':
					# the item is new. So we need to remove itself from the tree.
					entry.deleteNode(True)
				result = True

		return result

	def updateSourceTree(self, scm_root, scm_name, change_item):
		result = False

		scm_root_item = self.source_tree.findItemNode(scm_root)

		if scm_root_item is not None:
			entry = scm_root_item.findItemNode(change_item.path)

			if entry is None:
				# add new status (inc. new item if it did not exist before)
				entry = scm_root_item.addTreeNodeByPath(change_item.path)

			if entry is not None:
				entry.updateItemState(scm_name, change_item)
				result = True
			else:
				# TODO: log that path could not be added
				pass

		return result

	def updateSourceTreeNodeAsSCM(self, scm_root, scm, submodule):
		result = False
		scm_root_item = self.source_tree.findItemNode(os.path.abspath(scm_root))

		# This may cause the tree to be re-based to the level at the SCM is.
		if scm_root_item is None:
			# add new status (inc. new item if it did not exist before)
			scm_root_item = self.source_tree.addTreeNodeByPath(os.path.abspath(scm_root), rebase_tree=True)

		if scm_root_item is not None:
			scm_root_item.setSCM(scm, submodule)

		return result

	def addToUpdateThread(self, scm_change):
		if type(scm_change) == str and scm_change == "scms_updated":
			# need to loop through the tree to update nodes that are SCMs
			self.update_queue.put(UpdateItem("scms_updated", None, None, None))
		else:
			# schedule and update for the SCM
			for change in scm_change['changes']:
				if not self.source_tree.isSuffixFiltered(change.path):
					self.update_queue.put(UpdateItem("scm_update", os.path.abspath(scm_change['root']), scm_change['type'], change))

			# changes that have been cleared - revert, commit, clean, etc...
			for unchanged in scm_change['unchanged']:
				self.update_queue.put(UpdateItem("cleared", scm_change['root'], scm_change['type'], unchanged))

			self.renderTree()

	def updateTreeThread(self, queue):
		""" Update the tree from another feature.
			It expects a queue of UpdateItem items. It will use the "status" flag
			as what to do with the update. Currently "exit" will exit and "update"
			will updated the tree entry.
		"""
		redraw = False

		self.source_tree.update()
		self.renderTree()
		self.created = True

		while (True):
			item = queue.get()

			if item.status == 'exit':
				break

			elif item.status == "tree_update":
				# TODO: may need to time limit these so they don't happen too often.
				self.source_tree.update()
				self.source_tree.prune()
				self.needs_redraw = True

			elif item.status == "scm_update":
				self.needs_redraw = self.updateSourceTree(item.scm_root, item.scm_name, item.change)

			elif item.status == "cleared":
				self.clearSourceTreeChange(item.scm_root, item.scm_name, item.change) or redraw
				self.needs_redraw = True

			elif item.status == "scms_updated":
				scm_feature = self.tab_window.getFeature('SCMFeature')

				if scm_feature is not None:
					for scm in scm_feature.listSCMs():
						self.updateSourceTreeNodeAsSCM(scm.path, scm.scm, scm.submodule)
						self.source_tree.update()
						self.needs_redraw = True

	def initialise(self, tab_window):
		result = super(SourceTreeFeature, self).initialise(tab_window)

		# get the configuration
		directory = tab_window.getConfiguration('SettingsFeature', 'root_directory')

		self.ignore_suffixes = tab_window.getConfiguration('SourceTreeFeature', 'ignore_suffixes')
		self.ignore_directories = tab_window.getConfiguration('SourceTreeFeature', 'ignore_directories')

		if directory == '.':
			self.root_directory = os.path.abspath(directory)
		else:
			self.root_directory = directory

		# set up the rendering variables
		if tab_window.getSetting('UseUnicode') == 1:
			self.render_items = unicode_markers
		else:
			self.render_items = ascii_markers

		self.status_lookup = {	'A': self.render_items[MARKER_ADDED],
								'M': self.render_items[MARKER_CHANGED],
								'D': self.render_items[MARKER_DELETED],
								'U': self.render_items[MARKER_OUT_OF_DATE],
								'?': self.render_items[MARKER_UNKNOWN],
								'C': ' '} # cleared - added for safety - should not be used.

		# Ok, build the source tree.
		name = os.path.splitext(os.path.basename(self.root_directory))[0]

		self.tab_window = tab_window
		self.source_tree = beorn_lib.SourceTree(name, root=self.root_directory)

		self.source_tree.setSuffixFilter(self.ignore_suffixes)
		self.source_tree.setDirectoryFilter(self.ignore_directories)

		# start excepting updates to the tree.
		self.update_thread.start()

		# do the first create of the tree.
		self.update_queue.put(UpdateItem('create', None, None, None))

		return result

	def renderHistoryItem(self, level, node):
		""" Render History Item

			output a line of text for the history Item.
		"""
		return (True, level*LINE_LEVEL_SPACE + ' ' + node.getName() + ":" + node.getTime() + " " + node.getSummary().split('\n',1)[0])

	def renderTreeItem(self, level, node):
		""" Render a normal tree Item """

		skip_children = False

		open_marker = '  '

		if node.isDir():
			if node.isOpen():
				open_marker = self.render_items[MARKER_OPEN] + ' '
			else:
				open_marker = self.render_items[MARKER_CLOSED] + ' '
				skip_children = True

		elif node.hasChild() and not node.isOpen():
			skip_children = True

		# Handle special markers - is SCM or is link.
		node_scm = node.getSCM()

		if node_scm is not None:
			if node.isSubmodule():
				special_marker = ' [' + node_scm.getType()[0].lower() + '] '
			else:
				special_marker = ' [' + node_scm.getType()[0] + '] '
		elif node.isLink():
			special_marker = ' ' + self.render_items[MARKER_LINK] + ' '
		else:
			special_marker = ' '

		# now add the scm statuses
		scm_status = ''
		if node.hasState():
			for (scm_type, status) in node.state():
				scm_status = scm_status + scm_type[0] + self.status_lookup[status.status] + " "

		elif node.hasChild() and node.getFlag() is not None:
			scm_status = self.status_lookup[node.getFlag()]

		# update the line
		string = "{}{}{}{}{}".format(level*'  ', open_marker, node.getName(), special_marker, scm_status)
		return (skip_children, string)

	def all_nodes_scm_function(self, last_visited_node, node, value, level, direction, parameter):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		if self.tab_window.getConfiguration('SourceTreeFeature', 'hide_dot_files') and node.getName() != '' and node.getName()[0] == '.':
			# Ignore this file/directory and it's children as it is a .dot file and we are ignoring them.
			skip_children = True
		else:
			# render the rest of the tree.
			if type(node) == HistoryNode:
				(skip_children, line) = self.renderHistoryItem(level, node)
			else:
				(skip_children, line) = self.renderTreeItem(level, node)

			if level > 0:
				value.append(line)

			node.colour = len(value)

		return (node, value, skip_children)

	def rebaseTree(self, new_base):
		self.source_tree = self.source_tree.rebaseTree(new_base)
		return self.source_tree.getPath()

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			self.stopFollowSourceFile()

			contents = self.getHelp(self.keylist)
			if self.created is True:
				contents += self.source_tree.walkTree(self.all_nodes_scm_function, self.getOrder())

				scm_feature = self.tab_window.getFeature('SCMFeature')

				if scm_feature is not None:
					contents.append("")
					contents.append("[ Current Branches ]")
					for scm in scm_feature.listSCMs():
						contents.append("  %s: %s" % (scm.name, scm.scm.getBranch()))
			else:
				contents.append("updating tree, please wait...")

			self.tab_window.setBufferContents(self.buffer_id, contents)

			self.startFollowSourceFile()

	def openTreeToFile(self, path):
		entry = self.source_tree.findItemNode(path)

		if entry is not None:
			self.renderTree()
			self.setMenuPosition(entry.getColour() + 1)

	def handleOpenHistoryItem(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())
		version = None

		if item is not None:
			scm = item.findSCM()

			if type(item) == HistoryNode and item.findSCM() is not None:
				parent = item.getParent()
				version = item.getName()
			else:
				if item.getState(scm.getType()) is not None:
					parent = item
					version = scm.getCurrentVersion()

			if version is not None and version != 'none':
				contents = scm.getFile(parent.getPath(True), version)
				self.tab_window.openFileWithContent(version + ':' + parent.getName(), contents, readonly=True)

		return (False, line_no)

	def openDiff(self, scm, item, version):
		file_path = item.getPath(True)

		if file_path != self.diff_file_path:
			self.handleCloseDiffs(0, 0)

		self.diff_file_path = file_path

		contents = scm.getFile(item.getPath(True), version)
		if contents is not None:
			window_1 = self.tab_window.openFile(file_path)

			window_2_name = version + ':' + os.path.basename(file_path)
			window_2 = self.tab_window.openFileWithContent(window_2_name, contents, force_new=True, readonly=True)
			self.tab_window.diffWindows(window_1, window_2)
			self.diff_window_list.append(window_2_name)

	def handleSelectItem(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None:
			if type(item) == HistoryNode and item.getSCM() is not None:
				self.openDiff(item.getSCM(), item.getParent(), item.getVersion())

			elif item.isDir():
				item.toggleOpen()
				redraw = True

			elif item.isOnFileSystem():
				self.handleCloseDiffs(0,0)
				self.tab_window.openFile(item.getPath(True))

			elif item.hasState():
				self.handleCloseDiffs(0,0)
				scm = item.findSCM()

				# TODO: Deleted is the one of the ways that this case will happen.
				#
				# Looks like I am missing a state. The four states of files should be:
				#  Added  - On file system not in server.
				#  Deleted - Not on file system in repository.
				#  Amended - Changed on file system not in repository.
				#  Conflicted - Changed on repository and server.
				#
				#  Plus, this case that is not relevant yet (Can add for git)
				#  Removed - On local repo, removed from remote repository.

				if scm is not None:
					scm_item = item.getState(scm.getType())
					if scm_item is not None and scm_item.status != 'D':
						path = item.getPath(True)
						contents = scm.getFile(path)

						if type(contents) == list:
							self.tab_window.openFileWithContent(item.getVersion() + ':' + item.getParent().getName(), contents, readonly=True)

		return (redraw, line_no)

	def getSCMForItem(self, item):
		result = None

		active_scm = self.tab_window.getConfiguration('SCMFeature', 'active_scm')
		scm_feature = self.tab_window.getFeature('SCMFeature')

		if scm_feature is not None:
			for (scm_item, status) in item.state():
				result = item.findSCM(scm_item)

		return result

	def handleDiffFileItem(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None:
			if type(item) == HistoryNode:
				self.handleSelectItem(line_no, action)

			elif item.isOnFileSystem() and item.hasState():
				scm = self.getSCMForItem(item)

				if scm is not None:
					version_id = scm.getCurrentVersion()
					self.openDiff(scm, item, version_id)

		return (redraw, line_no)

	def handleCloseDiffs(self, line_no, action):
		for window in self.diff_window_list:
			self.tab_window.closeWindow(window)

		self.diff_window_list = []

		self.tab_window.diffModeOff()

		return(False, line_no)

	def handleCloseItem(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None:
			if item.hasChild() and item.isOpen():
				item.setOpen(False)
				redraw = True

			else:
				parent = item.getParent()

				if parent is not None:
					parent.setOpen(False)
					if parent.colour is not None:
						line_no = parent.colour
					redraw = True

		return (redraw, line_no)

	def handleCloseItemAll(self, line_no, action):
		redraw = False
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None and item is not None:
			if item.hasChild() and item.isOpen():
				item.setOpen(False)

			# TODO: fails - openParents dont exist.
			#
			# This needs to change to walk up the tree to find
			# an open parent and set the line number to that.
			#
			# Else, set the line_no to 1
			#
#			top = item.openParents(False)
#			redraw = True
#
#			if len(top) > 1:
#				line_no = top[1].getColour()

		return (redraw, line_no)

	def handleItemHistoryAll(self, line_no, action):
		redraw = False
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None and not item.isDir():
			if item.isOpen():
				item.toggleOpen()
				redraw = True

			elif type(item) == HistoryNode:
				item.getParent().toggleOpen()
				redraw = True

			elif item is not None:
				path = item.getPath(True)
				item.deleteChildren()
				item.setLeaf(True)
				item.setOpen(True)
				redraw = True

				number_history_items = self.tab_window.getConfiguration('SCMFeature', 'number_history_items')

				history = []

				scm_feature = self.tab_window.getFeature('SCMFeature')

				if scm_feature is not None:
					for scm_item in scm_feature.listSCMs():
						status = item.getState(scm_item.scm_type)

						if status is None or status.status != "A":
							history = scm_item.scm.getHistory(path, max_entries=number_history_items)

							if history is not None:
								for h_item in history:
									item.addChildNode(HistoryNode(h_item, scm_item.scm), mode=beorn_lib.NestedTreeNode.INSERT_END)

		return (redraw, line_no)

	def handleItemHistory(self, line_no, action):
		redraw = False
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None and not item.isDir():
			if item.isOpen():
				item.toggleOpen()
				redraw = True

			elif type(item) == HistoryNode:
				item.getParent().toggleOpen()
				redraw = True

			elif item is not None:
				active_scm = self.tab_window.getConfiguration('SCMFeature', 'preferred_scm')
				scm_feature = self.tab_window.getFeature('SCMFeature')

				if scm_feature is not None:
					scm = item.findSCM(active_scm)

					if scm is not None:
						number_history_items = self.tab_window.getConfiguration('SCMFeature', 'number_history_items')
						history = scm.getHistory(item.getPath(True), max_entries=number_history_items)

						if history != [] and history is not None:
							redraw = True

							item.deleteChildren()

							for h_item in history:
								item.addChildNode(HistoryNode(h_item, scm), mode=beorn_lib.NestedTreeNode.INSERT_END)
						else:
							item.deleteChildren()
							dummy_item = beorn_lib.scm.HistoryItem('none', 'No History in ' + active_scm, 0, None, None)
							item.addChildNode(HistoryNode(dummy_item, scm), mode=beorn_lib.NestedTreeNode.INSERT_END)

						item.setLeaf(True)
						item.setOpen(True)
						redraw = True
					else:
						item.deleteChildren()
						dummy_item = beorn_lib.scm.HistoryItem('none', 'SCM Not active:' + active_scm, 0, None, None)
						item.addChildNode(HistoryNode(dummy_item, scm), mode=beorn_lib.NestedTreeNode.INSERT_END)
						item.setLeaf(True)
						item.setOpen(True)
						redraw = True

		return (redraw, line_no)

	def handleShowPatch(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())
		self.handleCloseDiffs(0, 0)

		if item is not None and type(item) == HistoryNode and item.getSCM() is not None:
			contents = item.getSCM().getPatch(item.getVersion())

			if contents is not None and contents != '':
				self.tab_window.openFileWithContent(item.getVersion() + '.patch', contents, readonly=True)

		return (False, line_no)

	def handleCodeReview(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None and type(item) == HistoryNode and item.getSCM() is not None:
			code_reviews = self.tab_window.getFeature('CodeReviewFeature')

			if code_reviews is not None:
				code_reviews.addReview(item.getSCM().getChangeList(item.getVersion()), True)

		return (False, line_no)

	def onMouseClick(self, line, col):
		(redraw, line_no) = self.handleSelectItem(line, 0)
		if redraw:
			self.renderTree()
			window = self.tab_window.getCurrentWindow()
			self.tab_window.setPosition(window, (line, col))

	def timerCallbackFunction(self, timer_id):
		self.update_queue.put(UpdateItem("tree_update", None, None, None))

		if self.needs_redraw:
			self.renderTree()
			self.needs_redraw = False

	def setNeedsRedraw(self):
		self.needs_redraw = True

	def startFollowSourceFile(self):
		""" Will set the event for following the current file in the buffer.
			This will check to see if the user wants this feature turned on
			first.
		"""
		if self.tab_window.getConfiguration('SourceTreeFeature', 'follow_current_file') is True:
			self.tab_window.addEventHandler('BufWinEnter','SourceTreeFeature', SourceTreeFeature.SOURCE_TREE_FILE_LOADED_EVENT)

	def stopFollowSourceFile(self):
		self.tab_window.removeEventHandler('BufWinEnter', "SourceTreeFeature")

	def onEvent(self, event_id, window_obj):
		if event_id == SourceTreeFeature.SOURCE_TREE_FILE_LOADED_EVENT:
			if self.tab_window.isNormalWindow(window_obj):
				name = self.tab_window.getWindowName()

				if name is not None and name != '':
					self.openTreeToFile(name)
		else:
			# for now update the tree - and kick off a tree update.
			self.update_queue.put(UpdateItem("tree_update", None, None, None))

	def select(self):
		super(SourceTreeFeature, self).select()
		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_source_tree__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_source_tree')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)
		self.timer_task = self.tab_window.startTimerTask(self.timerCallbackFunction)

		self.tab_window.addEventHandler('CursorHoldI', 'SourceTreeFeature', SourceTreeFeature.SOURCE_TREE_USER_STOPPED_TYPING)
		self.tab_window.addEventHandler('CursorHold', 'SourceTreeFeature', SourceTreeFeature.SOURCE_TREE_USER_STOPPED_TYPING)
		self.tab_window.addEventHandler('FocusLost', 'SourceTreeFeature', SourceTreeFeature.SOURCE_TREE_USER_STOPPED_TYPING)


	def unselect(self):
		super(SourceTreeFeature, self).unselect()
		self.handleCloseDiffs(0, 0)
		self.tab_window.stopTimerTask(self.timer_task)
		self.timer_task = None
		self.tab_window.closeWindowByName("__ib_source_tree__")

		self.tab_window.removeEventHandler('CursorHoldI', 'SourceTreeFeature')
		self.tab_window.removeEventHandler('CursorHold', 'SourceTreeFeature')
		self.tab_window.removeEventHandler('FocusLost', 'SourceTreeFeature')

	def close(self):
		self.update_queue.put(UpdateItem('exit', '', '', None))
		self.update_thread.join(5.0)

		super(SourceTreeFeature, self).close()

# vim: ts=4 sw=4 noexpandtab nocin ai
