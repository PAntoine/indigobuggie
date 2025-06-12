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
#    file: timekeeper
#    desc: TimeKeeper Class that handles time keeper file types.
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
from .job import Job
from .project import Project
from beorn_lib.nested_tree import NestedTreeNode

class TimeKeeper(NestedTreeNode):
	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str or type(other) == str:
			for child in self.getChildren():
				if other == child.name:
					return True

		elif isinstance(other, Project):
			for child in self.getChildren():
				if other.name == child.name:
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

	def __init__(self, root=None, filename=None):
		super(TimeKeeper, self).__init__()

		self.name = " - no projects - "

		self.current_user		= getpass.getuser()
		self.current_machine	= platform.node()
		self.current_id			= self.current_user + '@' + self.current_machine

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

		if type(node) == Job:
			value.append(node.toString())

		return (node, value, False)

	def load(self):
		if self.root is not None:
			filename = os.path.join(self.root, self.current_id)
		else:
			filename = self.filename

		if not os.path.exists(filename):
			# if it does not exist, then empty is loaded and it is not
			# problem to save to the file.
			result = True
		else:
			try:
				in_file = open(filename, 'r')

				for line in in_file:
					parts = line.strip().split(',')

					project_name = parts[0]

					if project_name in self:
						project = self[project_name]
					else:
						project = Project(project_name)
						self.addChildNode(project, NestedTreeNode.INSERT_ASCENDING)

					# Odd version of timekeeper has tasks, which was never released so
					# this just filters out the tasks - have a task feature.
					if project_name[0] != '>':
						# 0 = project
						# 1 = job
						# 2 = start-time
						# 3 = total-time
						# 4 = last-commit-time
						# 5 = status
						# 6 = notes
						if parts[1] in project:
							project[parts[1]].addLineItem(*parts[2:7])
						else:
							new_job = Job(parts[1])
							project.addChildNode(new_job, NestedTreeNode.INSERT_ASCENDING)
							new_job.addLineItem(*parts[2:7])

				result = True
				in_file.close()

			except IOError as e:
				result = False

		return result

	def addProject(self, name):
		if name in self:
			project = self[name]

			if type(project) != Project:
				project = None
		else:
			project = Project(name)
			self.addChildNode(project, NestedTreeNode.INSERT_ASCENDING)

		return project

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
