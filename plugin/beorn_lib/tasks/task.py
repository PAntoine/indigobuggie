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
#    file: task
#    desc: This is the basic task.
#
#  author: peter
#    date: 24/12/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
from beorn_lib.nested_tree import NestedTreeNode

class Task(NestedTreeNode):
	TASK_STATUS_OPEN		= 0
	TASK_STATUS_COMPLETE	= 1
	TASK_STATUS_ABANDONED	= 2

	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str or type(other) == str:
			for child in self.getChildren():
				if other == child.name:
					return True

		return False

	def __getitem__(self, key):
		if type(key) == str or type(key) == str:
			for item in self.getChildren():
				if item.name == key:
					return item
		else:
			for item in self.getChildren():
				if item.name == key.name:
					return item

		raise KeyError("Does not exist")

	def __init__(self, name, filename='', status=TASK_STATUS_OPEN, line_no=0, column=0, notes=[], is_auto=False):
		super(Task, self).__init__()

		self.name = name
		self.status = status
		self.filename = filename
		self.line_no = line_no
		self.column = column
		self.is_auto = is_auto

		if type(notes) == str or type(notes) == str:
			self.notes = notes.split('\x03')
		else:
			self.notes = notes

	def toggleStatus(self):
		if self.status == Task.TASK_STATUS_OPEN:
			self.status = Task.TASK_STATUS_COMPLETE
		elif self.status == Task.TASK_STATUS_COMPLETE:
			self.status = Task.TASK_STATUS_ABANDONED
		else:
			self.status = Task.TASK_STATUS_OPEN

	def getStatus(self):
		if self.hasChild():
			for child in self:
				result = Task.TASK_STATUS_ABANDONED

				if child.getStatus() == Task.TASK_STATUS_OPEN:
					result = Task.TASK_STATUS_OPEN
					break
				elif child.getStatus() == Task.TASK_STATUS_COMPLETE:
					result = Task.TASK_STATUS_COMPLETE

			return result
		else:
			return self.status

	def isAuto(self):
		return self.is_auto

	def isActive(self):
		return self.timer_type != TASK_TIMER_EXPIRED

	def getPosition(self):
		return (self.line_no, self.column)

	def getName(self):
		return self.name

	def getNotes(self):
		return self.notes

	def getFileName(self):
		if self.filename is None:
			return ''
		else:
			return self.filename

	@classmethod
	def fromString(cls, string):
		parts = string.split(',')

		if len(parts) == 8:
			return Task(parts[1], parts[2], int(parts[3]), int(parts[4]), int(parts[5]), parts[7].split('\x03'), bool(parts[6]))
		else:
			return None

	def toString(self):
		return ','.join(['J', self.name, self.filename, str(self.status), str(self.line_no), str(self.column), str(self.is_auto),'\x03'.join(self.notes)])

	def updateNote(self, note):
		if type(note) == str or type(note) == str:
			self.notes = [note]
		else:
			self.notes = note

	def addNote(self, note):
		if type(note) == str or type(note) == str:
			self.notes.append(note)
		else:
			self.notes += note

# vim: ts=4 sw=4 noexpandtab nocin ai
