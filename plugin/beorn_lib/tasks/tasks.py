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
#    file: tasks
#    desc: Tasks Class that handles tasks.
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
from .timer_task import TimerTask
from .group import Group
from beorn_lib.nested_tree import NestedTreeNode

class Tasks(NestedTreeNode):
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

		raise KeyError("Does not exist")

	def __init__(self, root=None, filename=None):
		super(Tasks, self).__init__()

		self.current_user		= getpass.getuser()
		self.current_machine	= platform.node()
		self.current_id			= self.current_user + '@' + self.current_machine
		self.task_timer			= None
		self.next_timeout		= None
		self.callback			= None

		self.root = root
		self.filename = filename

		if root is None and filename is None:
			self.root = os.path.abspath(".")

	def saveWalkFunction(self, last_visited_node, node, value, level, direction, parameter):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		value.append(node.toString())

		return (node, value, False)

	def load(self):
		result = False
		if self.filename is None:
			filename = os.path.join(self.root, self.current_id)
		else:
			filename = self.filename

		if not os.path.isfile(filename):
			# if it does not exist, then empty is loaded and it is not
			# problem to save to the file, only don't want to write if the
			# the load failed.
			result = True
		else:
			try:
				in_file = open(filename, 'r')

				for line in in_file:
					if line[0] == '[':
						current_group = Group.fromString(line)
						self.addChildNode(current_group)

					elif line[0] == 'T':
						new_t = TimerTask.fromString(line)

						if new_t is not None:
							current_group.addChildNode(new_t)

					elif line[0] == 'J':
						new_t = Task.fromString(line)

						if new_t is not None:
							current_group.addChildNode(new_t)

					parts = line.strip().split(',')

				result = True

			except IOError as e:
				pass

		return result

	def getExpiredTimers(self, mark=False):
		result = []
		for group in self:
			for task in group:
				if type(task) is TimerTask and task.hasTimedOut(True):
					result.append(task)

		return result

	def taskCallback(self):
		""" Callback function for task timeouts """
		if self.callback is not None:
			expired_list = self.getExpiredTimers(True)

			for item in expired_list:
				self.callback(item)

			# Ok, set the next one.
			time_out = self.getNextTaskTimeout()

			if time_out is not None:
				self.next_timeout = time_out
				self.task_timer = threading.Timer(time_out-int(time.time()), self.taskCallback)
				self.task_timer.start()
			else:
				self.task_timer = None
				self.next_timeout = None

	def enableTaskTimeOutCallback(self, callback):
		result = False
		self.callback = callback

		if self.task_timer is None:
			time_out = self.getNextTaskTimeout()

			if time_out is not None:
				self.next_timeout = time_out
				self.task_timer = threading.Timer(time_out-int(time.time()), self.taskCallback)
				self.task_timer.start()
				result = True

		return result

	def disableTaskTimeOutCallback(self):
		self.callback = None
		self.disableTaskTimeOut()

	def checkUpdateTaskTimeout(self):
		if self.callback is not None:
			time_out = self.getNextTaskTimeout()

			if time_out is not None:
				if self.next_timeout is None or time_out < self.next_timeout:
					self.disableTaskTimeOut()
					self.enableTaskTimeOutCallback(self.callback)

	def disableTaskTimeOut(self):
		if self.task_timer is not None:
			self.task_timer.cancel()
			self.task_timer = None
			self.next_timeout = 0

	def updateAutoTask(self, line, column, task_type, item_path, contents, is_auto=False):
		if task_type not in self:
			self.addChildNode(Group(task_type))

		title = contents[0][:50]

		# TODO: add line number
		if title not in self[task_type]:
			self[task_type].addChildNode(Task(	name=title,
												filename=item_path,
												notes=contents[1:],
												line_no=line,
												column=column,
												is_auto=is_auto))
		else:
			# TODO: should check that notes has not changed.
			pass

	def getNextTaskTimeout(self):
		next_time_out = None

		for group in self:
			for task in group:
				if type(task) == TimerTask:
					if next_time_out is None or task.getTimeOutTime() < next_time_out:
						next_time_out = task.getTimeOutTime()

		return next_time_out

	def save(self):
		if self.root is not None:
			filename = os.path.join(self.root, self.current_id)
		else:
			filename = self.filename

		try:
			out_file = open(filename,'w')
			for line in self.walkTree(self.saveWalkFunction):
				out_file.write(line + '\n')

			out_file.close()
			result = True

		except IOError:
			result = False

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
