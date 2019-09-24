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
from history_node import HistoryNode
from settings_node import SettingsNode
from feature import Feature, KeyDefinition

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

unicode_markers = [ '+', '✗', '±', ' ', '▸', '▾', '?', 'm', 'g', 'r', 'l', 'ł' ]
ascii_markers   = [ '+', 'x', '~', ' ', '>', 'v', '?', 'm', 'g', 'r', 'l', 'B' ]

class SourceTreeFeature(Feature):
	SOURCE_TREE_SELECT			=	1
	SOURCE_TREE_HISTORY 		=	2
	SOURCE_TREE_HISTORY_ALL		=	3
	SOURCE_TREE_PATCH			=	4
	SOURCE_TREE_HISTORY_FILE 	=	5
	SOURCE_TREE_CLOSE_ALL_DIFFS	=	6
	SOURCE_TREE_CLOSE_ITEM		=	7
	SOURCE_TREE_CODE_REVIEW		=	8
	SOURCE_TREE_DIFF_FILE		=	9

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

	def getDialog(self, settings):
		suffix_string_list = ','.join(self.ignore_suffixes)
		directory_string_list = ','.join(self.ignore_directories)

		dialog_layout = [
			beorn_lib.dialog.Element('TextField', {'name': 'root_directory',		'title': 'Root Directory       ', 'x': 10, 'y': 1, 'default': self.root_directory}),
			beorn_lib.dialog.Element('TextField', {'name': 'ignore_suffixes',		'title': 'Suffix Ignore List   ', 'x': 10, 'y': 3, 'default': suffix_string_list}),
			beorn_lib.dialog.Element('TextField', {'name': 'ignore_directories',	'title': 'Directory Ignore List', 'x': 10, 'y': 4, 'default': directory_string_list}),
			beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': 6}),
			beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 32, 'y': 6})
		]

		return beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

	def resultsFunction(self, settings, results):
		if self.root_directory != results['root_directory']:
			self.root_directory = results['root_directory']
			self.tab_window.setConfiguration('SourceTreeFeature', 'root_directory', self.root_directory)

		ign_suff = results['ignore_suffixes'].split(',')

		if self.ignore_suffixes != ign_suff:
			self.ignore_suffixes = ign_suff
			self.tab_window.setConfiguration('SourceTreeFeature', 'ignore_suffixes', ign_suff)

		ign_dirs = results['ignore_directories'].split(',')

		if self.ignore_directories != ign_dirs:
			self.ignore_directories = ign_dirs
			self.tab_window.setConfiguration('SourceTreeFeature', 'ignore_directories', ign_dirs)

	def getDefaultConfiguration(self):
		return  {	'root_directory': '.',
					'ignore_suffixes': ['swp', 'swn', 'pyc', 'o'],
					'ignore_directories': ['.git', '.indigobuggie' ]}

	def getSettingsMenu(self):
		return SettingsNode('Source Tree', 'SourceTreeFeature', None, self.getDialog, self.resultsFunction)

	def initialise(self, tab_window):
		result = super(SourceTreeFeature, self).initialise(tab_window)

		# get the configuration
		self.root_directory = tab_window.getConfiguration('SourceTreeFeature', 'root_directory')
		self.ignore_suffixes = tab_window.getConfiguration('SourceTreeFeature', 'ignore_suffixes')
		self.ignore_directories = tab_window.getConfiguration('SourceTreeFeature', 'ignore_directories')

		# set up the rendering variables
		if tab_window.getSetting('UseUnicode') == 1:
			self.render_items = unicode_markers
		else:
			self.render_items = ascii_markers

		self.status_lookup = {	'A': self.render_items[MARKER_ADDED],
								'M': self.render_items[MARKER_CHANGED],
								'D': self.render_items[MARKER_DELETED],
								'?': self.render_items[MARKER_UNKNOWN]}

		# Ok, build the source tree.
		self.source_tree = beorn_lib.SourceTree('my name', root=self.root_directory)
		self.source_tree.setSuffixFilter(self.ignore_suffixes)
		self.source_tree.setDirectoryFilter(self.ignore_directories)
		self.source_tree.update()

		return result

	def renderHistoryItem(self, level, node):
		""" Render History Item

			output a line of text for the history Item.
		"""
		return (True, level*LINE_LEVEL_SPACE + ' ' + node.getName() + ":" + node.getTime() + " " + node.getSummary())

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
				scm_status = scm_status + scm_type.scm_type[0] + self.status_lookup[status.status] + " "

		elif node.hasChild() and node.getFlag() is not None:
			scm_status = self.status_lookup[node.getFlag()]

		# update the line
		return (skip_children, level*'  ' + open_marker + node.getName() + special_marker + scm_status)

	def all_nodes_scm_function(self, last_visited_node, node, value, level, direction):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		if type(node) == HistoryNode:
			(skip_children, line) = self.renderHistoryItem(level, node)
		else:
			(skip_children, line) = self.renderTreeItem(level, node)

		value.append(line)
		node.colour = len(value)

		return (node, value, skip_children)

	def getTree(self):
		return self.source_tree

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			contents = self.getHelp(self.keylist)
			contents += self.source_tree.walkTree(self.all_nodes_scm_function)
			self.tab_window.setBufferContents(self.buffer_id, contents)

	def handleOpenHistoryItem(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no)
		version = None

		if item is not None:
			scm = item.findSCM()
			if type(item) == HistoryNode:
					parent = item.getParent()
					version = item.getName()
			else:
				if scm is not None:
					if item.getState(scm.getType()) is not None:
						parent = item
						version = scm.getCurrentVersion()

			if scm is not None and version is not None:
				contents = scm.getFile(parent.getPath(True), version)
				self.tab_window.openFileWithContent(version + ':' + parent.getName(), contents)

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
			window_2 = self.tab_window.openFileWithContent(window_2_name, contents, True)
			self.tab_window.diffWindows(window_1, window_2)
			self.diff_window_list.append(window_2_name)

	def handleSelectItem(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no)

		if item is not None:
			if type(item) == HistoryNode:
				self.openDiff(item.getSCM(), item.getParent(), item.getVersion())

			elif item.isDir():
				item.toggleOpen()
				redraw = True

			elif item.isOnFileSystem():
				self.tab_window.openFile(item.getPath(True))

			elif item.hasState():
				scm = item.findSCM()

				if scm is not None:
					scm_item = item.getState(scm.getType())
					if scm_item is not None and scm_item.status != 'D':
						path = item.getPath(True)
						contents = scm.getFile(path)

						if type(contents) == list:
							self.tab_window.openFileWithContent(item.getVersion() + ':' + item.getParent().getName(), contents)

		return (redraw, line_no)

	def getSCMForItem(self, item):
		result = None

		active_scm = self.tab_window.getConfiguration('SCMFeature', 'active_scm')

		for (scm_item, status) in item.state():
			if scm_item.scm_type == active_scm:
				result = scm_item.scm
				break
			elif result == None:
				result = scm_item.scm

		return result

	def handleDiffFileItem(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no)

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

		item = self.source_tree.findItemWithColour(line_no)

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

	def handleItemHistoryAll(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no)

		if not item.isDir():
			if item.isOpen():
				item.toggleOpen()
				redraw = True

			elif type(item) == HistoryNode:
				item.getParent().toggleOpen()

			elif item is not None:
				path = item.getPath(True)
				item.deleteChildren()
				item.setOpen(True)
				redraw = True

				number_history_items = self.tab_window.getConfiguration('SCMFeature', 'number_history_items')

				history = []

				if not item.hasState():
					active_scm = self.tab_window.getConfiguration('SCMFeature', 'active_scm')
					scm_feature = self.tab_window.getFeature('SCMFeature')

					if scm_feature is not None:
						for scm_item in scm_feature.listSCMs():
							history = scm_item.scm.getHistory(path, max_entries=number_history_items)

							for h_item in history:
								item.addChildNode(HistoryNode(h_item, scm_item.scm), mode=beorn_lib.NestedTreeNode.INSERT_END)
				else:
					for (scm_item, status) in item.state():
						if status.status != "A":
							history = scm_item.scm.getHistory(path, max_entries=number_history_items)
							scm = scm_item.scm

							for h_item in history:
								item.addChildNode(HistoryNode(h_item, scm), mode=beorn_lib.NestedTreeNode.INSERT_END)

		return (redraw, line_no)

	def handleItemHistory(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no)

		if not item.isDir():
			if item.isOpen():
				item.toggleOpen()
				redraw = True

			elif type(item) == HistoryNode:
				item.getParent().toggleOpen()

			elif item is not None:
				active_scm = self.tab_window.getConfiguration('SCMFeature', 'active_scm')
				scm_feature = self.tab_window.getFeature('SCMFeature')

				if scm_feature is not None:
					scm = scm_feature.getSCMByName(active_scm)

					if scm is not None:
						number_history_items = self.tab_window.getConfiguration('SCMFeature', 'number_history_items')
						history = scm.getHistory(item.getPath(True), max_entries=number_history_items)
						if history != []:
							redraw = True

							item.deleteChildren()

							for h_item in history:
								item.addChildNode(HistoryNode(h_item, scm), mode=beorn_lib.NestedTreeNode.INSERT_END)

							item.setOpen(True)

		return (redraw, line_no)

	def handleShowPatch(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no)

		if item is not None and type(item) == HistoryNode:
			contents = item.getSCM().getPatch(item.getVersion())

			if contents is not None and contents != '':
				self.tab_window.openFileWithContent(item.getVersion() + '.patch', contents)

		return (False, line_no)

	def handleCodeReview(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no)

		if item is not None and type(item) == HistoryNode:
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
		if self.needs_redraw:
			self.renderTree()
			self.needs_redraw = False

	def setNeedsRedraw(self):
		self.needs_redraw = True

	def select(self):
		super(SourceTreeFeature, self).select()
		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_source_tree__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_source_tree')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)
		self.timer_task = self.tab_window.startTimerTask(self.timerCallbackFunction)

	def unselect(self):
		super(SourceTreeFeature, self).unselect()
		self.handleCloseDiffs(0, 0)
		self.tab_window.stopTimerTask(self.timer_task)
		self.timer_task = None
		self.tab_window.closeWindowByName("__ib_source_tree__")

# vim: ts=4 sw=4 noexpandtab nocin ai
