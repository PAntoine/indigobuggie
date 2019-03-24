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
#    file: code_review_feature
#    desc: This is the implementation of the CodeReview feature.
#
#  author: peter
#    date: 19/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
import getpass
import beorn_lib
from feature import Feature, KeyDefinition
from beorn_lib.code_review import LocalCodeReviews, CodeReview, CodeReviews, Change, ChangeFile, Hunk, Comment
from collections import namedtuple as namedtuple

ListItem = namedtuple('ListItem', ['hunk', 'start', 'end'])
SignItem = namedtuple('SignItem', ['start', 'type'])

unicode_markers = [ '±', '✓', '✗', 'm', '▸', '▾' ]
ascii_markers   = [ '~', '+', 'x', 'm', '>', 'v' ]

MARKER_OPEN		= 0
MARKER_APPROVED	= 1
MARKER_DELETED	= 2
MARKER_MERGED	= 3
MARKER_CLOSED	= 4
MARKER_OPENED	= 5

class CodeReviewFeature(Feature):
	CODE_REVIEW_SELECT			=	1
	CODE_REVIEW_ADD_COMMENT		=	2
	CODE_REVIEW_UP_VOTE			=	3
	CODE_REVIEW_DOWN_VOTE		=	4
	CODE_REVIEW_APPROVE			=	5
	CODE_REVIEW_MERGED			=	6
	CODE_REVIEW_ABANDON			=	7
	CODE_REVIEW_SHOW			=	8
	CODE_REVIEW_DELETE_COMMENT	=	9

	def __init__(self, configuration):
		result = super(CodeReviewFeature, self).__init__(configuration)
		self.title = "Code Review"
		self.code_reviews = None
		self.selectable = True
		self.left_name = None
		self.right_name = None
		self.hunk_list = {}
		self.current_file = None
		self.comment_window = None
		self.current_comment = None
		self.default = None
		self.engines = {}

		if 'engines' in configuration:
			for engine in configuration['engines']:
				self.engines[engine] = dict(configuration['engines'][engine])

		if 'default' in configuration:
			if configuration['default'] in self.engines:
				self.default = configuration['default']

		self.keylist = [KeyDefinition('<cr>', 	CodeReviewFeature.CODE_REVIEW_SELECT,			False, self.handleSelectItem,	"Select an Item."),
						KeyDefinition('c',		CodeReviewFeature.CODE_REVIEW_ADD_COMMENT,		True,  self.handleAddComment,	"Add Comment to a Code Review"),
						KeyDefinition('s',		CodeReviewFeature.CODE_REVIEW_SHOW,				False, self.handleShow,			"Show the contents."),
						KeyDefinition('+',		CodeReviewFeature.CODE_REVIEW_UP_VOTE,			False, self.handleVote,			"Add a up vote to the review."),
						KeyDefinition('-',		CodeReviewFeature.CODE_REVIEW_DOWN_VOTE,		False, self.handleVote,			"Down vote the review."),
						KeyDefinition('a',		CodeReviewFeature.CODE_REVIEW_APPROVE,			False, self.handleApproval,		"Approve the review."),
						KeyDefinition('m',		CodeReviewFeature.CODE_REVIEW_MERGED,			False, self.handleApproval,		"Merge the Review."),
						KeyDefinition('A',		CodeReviewFeature.CODE_REVIEW_ABANDON,			False, self.handleApproval,		"Abandon the review."),
						KeyDefinition('d',		CodeReviewFeature.CODE_REVIEW_DELETE_COMMENT,	False, self.handleDeleteComment,"Delete the review comment."),
				]

	def initialise(self, tab_window):
		result = super(CodeReviewFeature, self).initialise(tab_window)

		if result:
			if self.tab_window.getSetting('UseUnicode') == 1:
				self.render_items = unicode_markers
			else:
				self.render_items = ascii_markers

			self.status_lookup = {	CodeReview.CODE_REVIEW_STATUS_OPEN		:self.render_items[MARKER_OPEN],
									CodeReview.CODE_REVIEW_STATUS_APPROVED	:self.render_items[MARKER_APPROVED],
									CodeReview.CODE_REVIEW_STATUS_ABANDONED :self.render_items[MARKER_DELETED],
									CodeReview.CODE_REVIEW_STATUS_MERGED	:self.render_items[MARKER_MERGED]}

			# Ok, do we have a specific project file to use?
			self.makeResourceDir('code_review')

			ib_config_dir = self.tab_window.getSetting('Config_directory')
			code_review_dir = os.path.join(ib_config_dir, 'code_review')

			self.code_reviews = CodeReviews(code_review_dir)

			for item in self.engines:
				self.code_reviews.addReviewEngine(item, self.engines[item])

			self.code_reviews.load()

			result = True

		return result

	def renderFunction(self, last_visited_node, node, value, level, direction):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		skip_children = False
		line = ''

		if node.isOpen():
			marker = self.render_items[MARKER_OPENED]
		else:
			marker = self.render_items[MARKER_CLOSED]

		if type(node) == CodeReview:
			num_comments = node.getNumComments()

			if node.isOpen():
				line = level*'  ' + marker + ' ' + node.getTitle() + " " + self.status_lookup[int(node.getState())] + ' [' + str(num_comments) + ']'
			else:
				line = level*'  ' + marker + ' ' + node.getTitle() + " " + self.status_lookup[int(node.getState())] + ' [' + str(num_comments) + ']'
				skip_children = True

		elif type(node) == Change:
			up = 0
			down = 0

			votes = node.getVotes()
			for vote in votes:
				if votes[vote]:
					up += 1
				else:
					down += 1

			num_comments = node.getNumComments()

			if node.isOpen():
				line = level*'  ' + marker + ' ' + node.getID() + ' ' + str(up) + '/' + str(down) + ' [' + str(num_comments) + ']'
			else:
				line = level*'  ' + marker + ' ' + node.getID() + ' ' + str(up) + '/' + str(down) + ' [' + str(num_comments) + ']'
				skip_children = True

		elif type(node) == ChangeFile:
			num_comments = node.getNumComments()

			if node.isOpen():
				line = level*'  ' + marker + ' ' + node.getName() + ' [' + str(num_comments) + ']'
			else:
				line = level*'  ' + marker + ' ' + node.getName() + ' [' + str(num_comments) + ']'
				skip_children = True

		elif type(node) == Hunk:
			line = level*'  ' + marker + ' ' + node.toString(True) + ' [' + str(node.getNumComments()) + ']'
			skip_children = not node.isOpen()

		elif type(node) == Comment:
			line = level*'  ' + 'c: ' + node.getTitle()
		else:
			line = level*'  ' + marker + ' ' + node.getName()
			skip_children = not node.isOpen()

		if line != '':
			value.append(line)
			node.colour = len(value)

		return (node, value, skip_children)

	def addReview(self, change, is_local, engine=None):
		use_engine = None
		result = False

		if engine is None:
			use_engine = self.default
		else:
			if engine in self.engines:
				use_engine = engine

		if use_engine is not None and use_engine in self.code_reviews:
			result = self.code_reviews[use_engine].addReview(change, is_local)

		return result

	def openComment(self, comment, edit=False):
		if self.current_comment == comment:
			# Dont open a comment that is already open.
			return

		window = self.tab_window.findWindow('__code_review_comment_id__')

		if window is None:
			# TODO: this is a temp workaround
			self.comment_window = self.tab_window.openBottomWindow('__ib_comment__')
		else:
			self.comment_window = window

		parent = comment.getParent()

		if type(parent) == Hunk:
			self.tab_window.setWindowVariable(self.comment_window, '__code_review_id__', parent.getParent().getParent().getParent().getID())
			self.tab_window.setWindowVariable(self.comment_window, '__code_change_id__', parent.getParent().getParent().getID())
			self.tab_window.setWindowVariable(self.comment_window, '__code_review_filename__', parent.getParent().getName())
			self.tab_window.setWindowVariable(self.comment_window, '__code_review_hunk__', parent.getID())

		elif type(parent) == ChangeFile:
			self.tab_window.setWindowVariable(self.comment_window, '__code_review_id__', parent.getParent().getParent().getID())
			self.tab_window.setWindowVariable(self.comment_window, '__code_change_id__', parent.getParent().getID())
			self.tab_window.setWindowVariable(self.comment_window, '__code_review_filename__', parent.getName())

		elif type(parent) == Change:
			self.tab_window.setWindowVariable(self.comment_window, '__code_review_id__', parent.getParent().getID())
			self.tab_window.setWindowVariable(self.comment_window, '__code_change_id__', parent.getID())
		else:
			return

		self.current_comment = comment

		self.tab_window.bufferLeaveAutoCommand()
		self.tab_window.setWindowSyntax(self.comment_window, 'markdown')
		self.tab_window.setWindowVariable(self.comment_window, '__code_review_left__', int(comment.getCommentSide()))
		self.tab_window.setWindowVariable(self.comment_window, '__code_review_line__', comment.getLine())
		self.tab_window.setWindowVariable(self.comment_window, '__code_review_comment_id__', comment.getID())

		self.tab_window.setWindowContents(self.comment_window, comment.getContents(), readonly=edit)
		self.tab_window.addEventHandler('BufUnload','CodeReviewFeature', 'comment_unload', True)

	def onBufferWrite(self, window_obj):
		review_id	= self.tab_window.getWindowVariable(self.comment_window, '__code_review_id__')
		left		= self.tab_window.getWindowVariable(self.comment_window, '__code_review_left__')
		line		= self.tab_window.getWindowVariable(self.comment_window, '__code_review_line__')
		comment_id	= self.tab_window.getWindowVariable(self.comment_window, '__code_review_comment_id__')
		filename	= self.tab_window.getWindowVariable(self.comment_window, '__code_review_filename__')
		change_id	= self.tab_window.getWindowVariable(self.comment_window, '__code_change_id__')
		hunk_id		= self.tab_window.getWindowVariable(self.comment_window, '__code_review_hunk__')

		if hunk_id is not None:
			owner_item	= self.code_reviews.findHunk(review_id, change_id, filename, hunk_id)

		elif filename is not None:
			owner_item	= self.code_reviews.findChangeFile(review_id, change_id, filename)

		elif change_id is not None:
			owner_item = self.code_reviews.findChange(review_id, change_id)

		if owner_item is not None:
			comment = owner_item[comment_id]

			buf = self.tab_window.getWindowContents(self.comment_window)
			if comment is not None:
				if len(buf[:]) == 1 and buf[0] == '':
					# remove the comment.
					comment.deleteNode()
					self.tab_window.setWindowVariable(self.comment_window, '__code_review_comment_id__', 0)
				else:
					# amend the comment
					comment.setContents(buf[:])
					comment.makeLocal()	# make all the comments parents local

				owner_item.setOpen(True)
				self.renderTree()

		self.tab_window.clearModified(self.comment_window)

	def findHunkFromLeft(self, line):
		hunk = None
		hunk_line = 0

		for item in self.left_list:
			if line <= item.end:
				# found the item.
				hunk = item.hunk
				hunk_line = (line - item.start) + hunk.original_line
				break

		return (hunk, hunk_line)

	def findHunkFromRight(self, line):
		hunk = None
		hunk_line = 0

		for item in self.right_list:
			if line <= item.end:
				# found the item.
				hunk = item.hunk
				hunk_line = (line - item.start) + hunk.new_line
				break

		return (hunk, hunk_line)

	def onCommand(self, command_id, parameter, position):
		if int(command_id) == CodeReviewFeature.CODE_REVIEW_ADD_COMMENT:
			if self.current_file is not None:
				left_side = (parameter == 'left')
				if left_side:
					(hunk, line) = self.findHunkFromLeft(int(position[1]) - 1)
				else:
					(hunk, line) = self.findHunkFromRight(int(position[1]) - 1)

				comment = Comment(self.code_reviews.getUser(), int(time.time()), [], line, left_side)
				hunk.addChildNode(comment)
				self.openComment(comment)

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			contents = self.getHelp(self.keylist)
			contents += self.code_reviews.walkTree(self.renderFunction)

			self.tab_window.setBufferContents(self.buffer_id, contents)

	def closeDiffs(self):
		if self.left_name is not None:
			self.tab_window.closeWindow(self.left_name)

		if self.right_name is not None:
			self.tab_window.closeWindow(self.right_name)

		self.left_name = None
		self.right_name = None

		self.current_file = None
		self.tab_window.diffModeOff()

	def getCommentLines(self, change_item):
		left = []
		right = []

		for hunk in change_item.getChildren():
			for comment in hunk.getChildren():
				if comment.getCommentSide():
					# It's on the left
					left.append(SignItem(comment.getLine(), 1))
				else:
					right.append(SignItem(comment.getLine(), 1))

		return (left, right)

	def getHunkRelativeSigns(self, hunk, right_start, left_start):
		left = []
		right = []

		for comment in hunk.getChildren():
			if comment.getCommentSide():
				# It's on the left
				off = (comment.getLine() - hunk.getStart()) + int(left_start)
				left.append(SignItem(off, 1))
			else:
				off = (comment.getLine() - hunk.getChangeStart()) + int(right_start)
				right.append(SignItem(off, 1))

		return (left, right)

	def handleSelectItem(self, line_no, action):
		redraw = False
		item = self.code_reviews.findItemWithColour(line_no)

		if item is not None:
			if type(item) == Comment:
				self.openComment(item)
			else:
				item.toggleOpen()
			redraw = True

		return (redraw, line_no)

	def handleShow(self, line_no, action):
		redraw = False
		item = self.code_reviews.findItemWithColour(line_no)

		if item is not None and type(item) == ChangeFile:
			left = []
			right = []

			self.left_list = []
			self.right_list = []

			left_sign = []
			right_sign = []

			for child in item.getChildren():
				if type(child) == Hunk:
					(l,r) = child.getChange()

					left_start = len(left)
					left.append('--- ' + item.getName() + ' ' + child.toString())
					left += l
					self.left_list.append(ListItem(child, left_start, len(left)))
					left_sign.append(SignItem(left_start, 0))

					right_start = len(right)
					right.append('--- ' + item.getName() + ' ' + child.toString())
					right += r
					self.right_list.append(ListItem(child, right_start, len(right)))
					right_sign.append(SignItem(right_start, 0))

					(left_coms, right_coms) = self.getHunkRelativeSigns(child, right_start, left_start)
					right_sign += right_coms
					left_sign += left_coms

			self.closeDiffs()
			self.current_file = item

			self.left_name = '[left_' + item.getParent().getID() + ']' + item.getName()
			left_win  = self.tab_window.openFileWithContent(self.left_name, left, False)
			self.tab_window.addSigns(left_win, left_sign)
			self.tab_window.addCommands(self.__class__.__name__, self.keylist, 'left')
			self.tab_window.addEventHandler('CursorMoved','CodeReviewFeature', 'left', True)

			self.right_name = '[right_' + item.getParent().getID() + ']' + item.getName()
			right_win  = self.tab_window.openFileWithContent(self.right_name, right, True)
			self.tab_window.addSigns(right_win, right_sign)
			self.tab_window.addCommands(self.__class__.__name__, self.keylist, 'right')
			self.tab_window.addEventHandler('CursorMoved','CodeReviewFeature', 'right', True)

			self.tab_window.diffWindows(left_win, right_win)

		return (redraw, line_no)


	def handleAddComment(self, line_no, action):
		redraw = False
		item = self.code_reviews.findItemWithColour(line_no)

		if item is not None:
			comment = None

			if type(item) == Hunk:
				comment = Comment(self.code_reviews.getUser(), int(time.time()), [], item.getStart(), True)
				item.addChildNode(comment)
				self.openComment(comment)

			elif type(item) == Comment:
				parent = item.getParent()
				comment = Comment(self.code_reviews.getUser(), int(time.time()), [], parent.getStart())
				item.addChildNode(comment)
				self.openComment(comment)

			elif type(item) in [ChangeFile, Change]:
				comment = Comment(self.code_reviews.getUser(), int(time.time()), [], 0)
				item.addChildNode(comment)
				self.openComment(comment)

		return (redraw, line_no)

	def handleVote(self, line_no, action):
		redraw = False
		item = self.code_reviews.findItemWithColour(line_no)

		vote = (action == CodeReviewFeature.CODE_REVIEW_UP_VOTE)

		if item is not None:
			if type(item) == Hunk:
				item.getParent().getParent().vote(getpass.getuser(), vote)
				redraw = True

			elif type(item) == ChangeFile:
				item.getParent().vote(getpass.getuser(), vote)
				redraw = True

			elif type(item) == Change:
				item.vote(getpass.getuser(), vote)
				redraw = True

		return (redraw, line_no)

	def handleApproval(self, line_no, approval):
		redraw = False
		item = self.code_reviews.findItemWithColour(line_no)

		if item is not None and type(item) == Change:
			item.setState(getpass.getuser(), approval)
			redraw = True

		return (redraw, line_no)

	def handleDeleteComment(self, line_no, action):
		redraw = False
		item = self.code_reviews.findItemWithColour(line_no)

		if item is not None and type(item) == Comment:
			item.deleteNode(True)
			redraw = True

		return (redraw, line_no)

	def onMouseClick(self, line, col):
		(redraw, line_no) = self.handleSelectItem(line, 0)
		if redraw:
			self.renderTree()
			window = self.tab_window.getCurrentWindow()
			self.tab_window.setPosition(window, (line, col))

	def onEvent(self, event_id):
		if event_id == "comment_unload":
			window = self.tab_window.findWindow('__code_review_comment_id__')

			if window is not None:
				self.comment_window = None
				self.current_comment = None

				if window:
					del window.vars['__code_review_comment_id__']
		else:
			window = self.tab_window.getCurrentWindow()
			position = self.tab_window.getCurrentPos()
			left_side = (event_id == 'left')
			if left_side:
				(hunk, line) = self.findHunkFromLeft(int(position[0]) - 1)
			else:
				(hunk, line) = self.findHunkFromRight(int(position[0]) - 1)

			if hunk is not None:
				comment = hunk.getCommentForLine(line, left_side)

				if comment is not None:
					self.openComment(comment)

			self.tab_window.setWindowPos(window, position[0])

	def closeCommentWindow(self):
		window = self.tab_window.findWindow('__code_review_id__')

		if window is not None:
			self.comment_window = None
			self.current_comment = None
			self.tab_window.closeWindow(window.number)

	def getTree(self):
		return self.code_reviews

	def select(self):
		result = super(CodeReviewFeature, self).select()
		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_code_review__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_code_review')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)

	def unselect(self):
		self.closeCommentWindow()
		self.closeDiffs()
		result = super(CodeReviewFeature, self).unselect()
		self.tab_window.closeWindowByName("__ib_code_review__")

	def close(self):
		self.closeDiffs()

		if self.code_reviews is not None:
			self.code_reviews.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
