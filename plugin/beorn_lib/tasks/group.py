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
#    file: group
#    desc: Group class that holds the groups that the tasks belong to.
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
import getpass
import platform
import threading
from .task import Task
from beorn_lib.nested_tree import NestedTreeNode

class Group(NestedTreeNode):
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

	def __init__(self, name):
		super(Group, self).__init__()

		self.name = name

	@classmethod
	def fromString(cls, string):
		return Group(string[1:-2])

	def toString(self):
		return "[" + self.name + "]"

	def getName(self):
		return self.name

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
			return Task.TASK_STATUS_OPEN

# vim: ts=4 sw=4 noexpandtab nocin ai
