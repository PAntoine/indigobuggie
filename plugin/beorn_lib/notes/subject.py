#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#
#                    ,--.
#                    |  |-.  ,---.  ,---. ,--.--.,--,--,
#                    | .-. '| .-. :| .-. ||  .--'|      \
#                    | `-' |\   --.' '-' '|  |   |  ||  |
#                     `---'  `----' `---' `--'   `--''--'
#
#    file: subject
#    desc: This class holds the subjects of the notes, which in turn will hold the
#    	   notes.
#
#  author: peter
#    date: 23/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from .note import Note
from beorn_lib.nested_tree import NestedTreeNode

#---------------------------------------------------------------------------------
# class definition
#---------------------------------------------------------------------------------
class Subject(NestedTreeNode):
	""" Subject class """

	def __init__(self, name):
		super(Subject, self).__init__(name, None)
		self.name = name
		self.open = False

	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str:
			find_name = other
		elif isinstance(other, Note):
			find_name = other.name
		else:
			return False

		for child in self.getChildren():
			if find_name == child.name:
				return True
		else:
			return False

	def toggle(self):
		self.open = not self.open

	def hasNote(self, title):
		""" return true if the subject is in the notes list """
		return title in self

	def addNote(self, title, message):
		""" will add a note if it does not already exist and return the note """
		result = None
		subject = None

		if title.find('=') == -1:
			if title not in self:
				result = Note(title, message)
				self.addChildNode(result)

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
