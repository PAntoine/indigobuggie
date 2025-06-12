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
#    file: job
#    desc: Job Class that handles time keeper jobs.
#
#  author: peter
#    date: 23/12/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
from beorn_lib.nested_tree import NestedTreeNode

class Job(NestedTreeNode):
	def __init__(self, name):
		super(Job, self).__init__()

		self.name = name
		self.start_time = 0
		self.total_time = 0
		self.last_commit_time = 0
		self.status = 'created'
		self.note = []

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

	def __lt__(self, rhs):
		""" Less Than

			Use the name as the definition of less than.
		"""
		return self.name < rhs.name

	def getName(self):
		return self.name

	def toString(self):
		project = self.getParent().getName()
		return ','.join([project, self.name, str(self.start_time), str(self.total_time), str(self.last_commit_time), self.status, '\x03'.join(self.note), ''])

	def addLineItem(self, start_time, item_time, last_commit_time, status, note):
		if self.start_time == 0:
			self.start_time = int(start_time)

		self.total_time += int(item_time)

		if self.last_commit_time < int(last_commit_time):
			self.last_commit_time = int(last_commit_time)

		self.status = status

		if type(note) == str or type(note) == str:
			self.note = note.split('\x03')
		else:
			self.note = note

	def getTotalString(self):
		""" return total - days:hours:mins """
		minute = 60
		hour = minute * 60
		day = hour * 24

		days = int(self.total_time / day)
		hours = int((self.total_time % day) / hour)
		minutes = int((self.total_time % hour) / minute)

		return "{:04d}:{:02d}:{:02d}".format(days, hours, minutes)

	def addTime(self, time):
		self.total_time += time

	def getNote(self):
		return self.note

	def addNote(self, note):
		if type(note) == str or type(note) == str:
			self.note = [ note ]
		else:
			self.note = note

# vim: ts=4 sw=4 noexpandtab nocin ai
