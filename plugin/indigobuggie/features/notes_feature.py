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
#    file: notes_feature
#    desc: This feature manages the users notes.
#
#  author: peter
#    date: 19/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import beorn_lib
from feature import Feature, KeyDefinition

MARKER_CLOSED		= 0
MARKER_OPEN			= 1

unicode_markers = [ '▸', '▾' ]
ascii_markers   = [ '>', 'v' ]

class NotesFeature(Feature):
	NOTES_SELECT			=	1
	NOTES_ADD_SUBJECT		=	2
	NOTES_ADD_NOTE			=	3

	def __init__(self, configuration):
		super(NotesFeature, self).__init__(configuration)
		self.title = "Note Keeper"
		self.notes = None
		self.selectable = True
		self.loaded_ok = False

		self.keylist = [KeyDefinition('<cr>', 	NotesFeature.NOTES_SELECT,		False,	self.handleSelect,		"Select the Item."),
						KeyDefinition('S', 		NotesFeature.NOTES_ADD_SUBJECT,	False,	self.handleAddSubject,	"Add new Subject."),
						KeyDefinition('a', 		NotesFeature.NOTES_ADD_NOTE,	False,	self.handleAddNote,		"Add a Note to the subject."),]

	def render_function(self, last_visited_node, node, value, level, direction):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		skip_children = not node.isOpen()

		if type(node) == beorn_lib.notes.Subject:
			if node.isOpen():
				value.append( '  ' + self.render_items[MARKER_OPEN]  + ' ' + node.name)
			else:
				value.append( '  ' + self.render_items[MARKER_CLOSED]  + ' ' + node.name)
		else:
			value.append('    ' + node.name)

		node.colour = len(value)

		return (node, value, skip_children)

	def initialise(self, tab_window):
		result = super(NotesFeature, self).initialise(tab_window)

		if self.tab_window.getSetting('UseUnicode') == 1:
			self.render_items = unicode_markers
		else:
			self.render_items = ascii_markers

		if result:
			# Ok, do we have a specific project file to use?
			ib_config_dir = self.tab_window.getSetting('Config_directory')
			notes_dir = os.path.join(ib_config_dir, 'notes')

			if not os.path.isdir(notes_dir):
				os.makedirs(notes_dir)
				self.notes = beorn_lib.Notes('NOTES', notes_dir)
				self.notes.save()
				self.loaded_ok = True
			else:
				self.notes = beorn_lib.Notes('NOTES', notes_dir)
				self.loaded_ok = self.notes.load()

			result = True

		return result

	def renderTree(self):
		if self.current_window is not None:
			contents = self.getHelp(self.keylist)
			contents += self.notes.walkTree(self.render_function)
			self.tab_window.setBufferContents(self.buffer_id, contents)

	def addSubject(self, subject):
		self.notes.addSubject(subject)

	def addNote(self, subject, contents):
		result = False

		if not self.note.hasSubject(subject):
			self.notes.addSubject(subject)

		if not self.notes.hasNote(contents[0]):
			# OK, we dont have a not with the same title already
			self.notes.addNote(subject, contents[0], contents[1:])
			result = True

		return result

	def amendNote(self, subject, contents, append=False):
		result = False

		note = self.notes.getNote(subject, content[0])

		if note is not None:
			# OK, we dont have a not with the same title already
			note.append(contents[1:])
			result = True

		return result

	def deleteNote(self, subject, title):
		result = False

	def findItemWithColour(self, colour):
		""" Find the item in the tree with the specific colour.

			Due to the nature of the search it is not recursive and does not need to
			walk back up the tree.
		"""
		prev = self.notes

		for item in self.notes.getChildren():
			if item.colour == colour:
				return item

			elif item.colour > colour:
				for note in prev.getChildren():
					if note.colour == colour:
						return note

			prev = item

		for note in prev.getChildren():
			if note.colour == colour:
				return note

		return None

	def openNote(self, subject_name, title, content):
		window = self.tab_window.openFileWithContent('__ib_note__', content, readonly=False, replace=True)

		self.tab_window.bufferLeaveAutoCommand()
		self.tab_window.setWindowSyntax(window, 'markdown')
		self.tab_window.setWindowVariable(window, '__note_subject__', subject_name)
		self.tab_window.setWindowVariable(window, '__note_title__', title)

	def handleAddSubject(self, line_no, action):
		result = False

		new_subject = self.tab_window.getUserInput('New Subject')

		if not self.notes.hasSubject(new_subject):
			if self.notes.addSubject(new_subject):
				result = True

		return (result, line_no)

	def handleSelect(self, line_no, action):
		result = False

		item = self.findItemWithColour(line_no)

		if item is not None:
			if type(item) == beorn_lib.notes.Subject:
				item.toggleOpen()
				result = True

			elif type(item) == beorn_lib.notes.Note:
				self.openNote(item.getParent().name, item.name, item.getMessage())

		return (result, line_no)

	def handleAddNote(self, line_no, action):
		result = False

		item = self.findItemWithColour(line_no)

		if item is not None:
			if type(item) == beorn_lib.notes.Subject:
				subject = item

			elif type(item) == beorn_lib.notes.Note:
				subject = item.getParent()

			new_title = self.tab_window.getUserInput('Title')

			if not subject.hasNote(new_title):
				content = ['# ' + new_title + ' #', '']
				if subject.addNote(new_title, content):
					self.openNote(subject.name, new_title, content)
					result = True

		return (result, line_no)

	def onMouseClick(self, line, col):
		(redraw, line_no) = self.handleSelect(line, 0)
		if redraw:
			self.renderTree()
			self.tab_window.setPosition(self.tab_window.getCurrentWindow(), (line. col))

	def closeNotes(self):
		pass

	def onBufferWrite(self, window):
		subject = self.tab_window.getWindowVariable(window, '__note_subject__')
		title = self.tab_window.getWindowVariable(window, '__note_title__')

		note = self.notes.getNote(subject, title)

		if note is not None:
			note.amendMessage(self.tab_window.getWindowContents(window))

		self.tab_window.clearModified(window)

	def select(self):
		super(NotesFeature, self).select()
		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_notes__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_notes')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)

	def unselect(self):
		super(NotesFeature, self).unselect()
		self.closeNotes()
		self.tab_window.closeWindowByName("__ib_notes__")

	def close(self):
		if self.notes is not None and self.loaded_ok:
			self.notes.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
