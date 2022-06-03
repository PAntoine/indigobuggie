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
#    file: history_tree_feature
#    desc: This handles history (and branch) trees.
#
#  author: peter
#    date: 30/10/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2022 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import time
import beorn_lib
from .feature import Feature, KeyDefinition

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


class HistoryTreeFeature(Feature):
	# User actions
	HISTORY_TREE_SELECT			= 1
	HISTORY_TREE_DIFF			= 2
	HISTORY_TREE_CHANGES		= 3
	HISTORY_TREE_CLOSE_DIFFS	= 4
	HISTORY_TREE_REFRESH		= 5
	HISTORY_TREE_OPEN_CURRENT	= 6
	HISTORY_TREE_CLOSE_ITEM		= 7

	def __init__(self):
		super(HistoryTreeFeature, self).__init__()
		self.title = "History Tree"
		self.notes = None
		self.selectable = True
		self.needs_saving = False
		self.tab_window = None
		self.version_id = "HEAD~20"

		self.version_changed = True
		self.source_tree = None
		self.changes_only = True

		self.details = None

		self.diff_window_list = []

		# safe default - set on select
		self.render_items = ascii_markers

		self.selected_scm = None

		self.keylist = [KeyDefinition('<cr>',	HistoryTreeFeature.HISTORY_TREE_SELECT,			False,	self.handleSelectItem,	"Select a tree item."),
						KeyDefinition('d',		HistoryTreeFeature.HISTORY_TREE_DIFF,			False,	self.handleDiffItem,	"Diff the history version against current."),
						KeyDefinition('D',		HistoryTreeFeature.HISTORY_TREE_CLOSE_DIFFS,	False,	self.handleCloseDiffs,	"Close the diffs that have been opened here"),
						KeyDefinition('c',		HistoryTreeFeature.HISTORY_TREE_CHANGES,		False,	self.handleChangesOnly,	"Only list the files that have changes."),
						KeyDefinition('o',		HistoryTreeFeature.HISTORY_TREE_OPEN_CURRENT,	False,	self.handleOpenCurrent,	"Open the current version of file on the file system."),
						KeyDefinition('x',		HistoryTreeFeature.HISTORY_TREE_CLOSE_ITEM,		False,	self.handleCloseItem,	"Close the tree items."),
						KeyDefinition('r',		HistoryTreeFeature.HISTORY_TREE_REFRESH,		False,	self.handleRefreshTree,	"Refresh the tree - for file system changes.")]

	def setCurrentVersion(self, scm=None, version_id=None):

		if scm is None:
			scm_feature = self.tab_window.getFeature('SCMFeature')

			if scm_feature is not None:
				cs = scm_feature.getCurrentSCM()
				if cs is not None:
					self.selected_scm = cs.scm
		else:
			self.selected_scm = scm

		if version_id is None:
			if self.selected_scm  is not None:
				self.version_id = self.selected_scm.getVersion()
		else:
			self.version_id = version_id

		self.details = self.selected_scm.getCommitDetails(self.version_id)

		self.version_changed = True
		self.updateTree()
		self.renderTree()

	def initialise(self, tab_window):
		self.tab_window = tab_window

		# set up the rendering variables
		if self.tab_window.getSetting('UseUnicode') == 1:
			self.render_items = unicode_markers
		else:
			self.render_items = ascii_markers

		self.status_lookup = {	'A': self.render_items[MARKER_ADDED],
								'M': self.render_items[MARKER_CHANGED],
								'D': self.render_items[MARKER_DELETED],
								'U': self.render_items[MARKER_OUT_OF_DATE],
								'?': self.render_items[MARKER_UNKNOWN],
								'C': ' '}  # cleared - added for safety - should not be used.

		return True

	def isSelectable(self):
		return self.selectable

	def updateTree(self):
		if self.version_changed:
			if self.selected_scm is not None:
				self.source_tree = self.selected_scm.getSourceTree(self.version_id)
			else:
				scm_feature = self.tab_window.getFeature('SCMFeature')

				if scm_feature is not None:
					scm = scm_feature.getCurrentSCM()

					if scm is not None:
						self.selected_scm = scm.scm
						self.source_tree = self.selected_scm.getSourceTree(self.version_id)

			self.version_changed = False
		else:
			pass
			# TODO: refresh the tree against the current working version.

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

		flag = ' '
		if node.getFlag() in self.status_lookup:
			flag = self.status_lookup[node.getFlag()]

		# update the line
		string = "{}{}{} {}".format(level*'  ', open_marker, node.getName(), flag)
		return (skip_children, string)

	def all_nodes_function(self, last_visited_node, node, value, level, direction, parameter):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		if node.getName() != '' and node.getName()[0] == '.' and self.tab_window.getConfiguration('SourceTreeFeature', 'hide_dot_files'):
			# Ignore this file/directory and it's children as it is a .dot file and we are ignoring them.
			skip_children = True

		elif self.changes_only and node.getFlag() is None:
			skip_children = True

		else:
			# render the rest of the tree.
			(skip_children, line) = self.renderTreeItem(level, node)

			if level > 0:
				value.append(line)
				node.colour = len(value) + 4	# The offset for the header -  know magic number.

		return (node, value, skip_children)

	def getOrder(self):
		""" Get Order

			Default to the normal tree walk, but if source tree is available (very likely)
			then use that config - assuming the user will want the same order for all of
			the trees that are displayed (and same the issue of having to configure more
			things.
		"""
		result = beorn_lib.NestedTreeNode.TREE_WALK_NORMAL
		config = self.tab_window.getConfiguration('SourceTreeFeature', 'display_order')

		if config is not None:
			result = int(config)

		return result

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			tab = self.tab_window.tab_control.getCurrentTab()

			if tab is not None and tab.ident == self.tab_window.ident:

				if self.version_id == "None":
					self.setCurrentVersion()

				contents = self.getHelp(self.keylist)
				contents.append("Version: " + self.version_id)
				contents.append("Date   : " + time.strftime("%Y-%m-%d", time.gmtime(int(self.details.timestamp))))
				contents.append("Author : " + self.details.author)
				contents.append(" ")

				if self.source_tree is not None:
					contents += self.source_tree.walkTree(self.all_nodes_function, self.getOrder())

				self.tab_window.setBufferContents(self.buffer_id, contents)

	def handleSelectItem(self, line_no, action):
		redraw = False

		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None:
			if item.isDir():
				item.toggleOpen()
				redraw = True
			else:
				if self.selected_scm is not None:
					self.handleCloseDiffs(0, 1)
					contents = self.selected_scm.getFile(item.getPath(True), self.version_id)
					self.tab_window.openFileWithContent(self.version_id + ':' + item.getName(), contents, readonly=True)

		return (redraw, line_no)

	def handleDiffItem(self, line_no, action):
		redraw = False
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None and item.getFlag() != 'D':
			# always close the diffs.
			self.handleCloseDiffs(0, 1)

			if self.selected_scm is not None:
				file_path = item.getPath(True)

				window_1 = self.tab_window.openFile(file_path)

				contents = self.selected_scm.getFile(file_path, self.version_id)
				window_2_name = self.version_id + ':' + item.getName()
				window_2 = self.tab_window.openFileWithContent(window_2_name, contents, force_new=True, readonly=True)

				self.tab_window.diffWindows(window_1, window_2)
				self.diff_window_list.append(window_2_name)

		return (redraw, line_no)

	def handleCloseDiffs(self, line_no, action):
		for window in self.diff_window_list:
			self.tab_window.closeWindow(window)

		if action == 1:
			# close the diffs in the source tree feature - otherwise things get confusing.
			source_tree_feature = self.tab_window.getFeature('SourceTreeFeature')
			if source_tree_feature is not None:
				source_tree_feature.handleCloseDiffs(0, 1)

		self.diff_window_list = []

		self.tab_window.diffModeOff()

		return(False, line_no)

	def handleChangesOnly(self, line_no, action):
		self.changes_only = not self.changes_only
		return (True, line_no)

	def handleRefreshTree(self, line_no, action):
		self.version_changed = True
		self.updateTree()
		return (True, line_no)

	def handleOpenCurrent(self, line_no, action):
		item = self.source_tree.findItemWithColour(line_no, self.getOrder())

		if item is not None and item.getFlag() != 'D':
			# always close the diffs.
			self.handleCloseDiffs(0, 1)

			if self.selected_scm is not None:
				file_path = item.getPath(True)
				self.tab_window.openFile(file_path)

		return (False, line_no)

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

	def select(self):
		super(HistoryTreeFeature, self).select()
		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_history_tree__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_history_tree')

		if self.selected_scm is None:
			self.setCurrentVersion()

		self.updateTree()
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)

	def unselect(self):
		super(HistoryTreeFeature, self).unselect()
		self.tab_window.closeWindowByName("__ib_history_tree__")

# vim: ts=4 sw=4 noexpandtab nocin ai
