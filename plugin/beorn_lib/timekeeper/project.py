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
#    file: project
#    desc: The project object for Project.
#
#    	PS: Not the project from Project Plan. :)
#
#  author: peter
#    date: 23/12/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from .job import Job
from beorn_lib.nested_tree import NestedTreeNode

class Project(NestedTreeNode):
	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str or type(other) == str:
			for child in self.getChildren():
				if other == child.name:
					return True

		elif isinstance(other, Job):
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

	def __lt__(self, rhs):
		""" Less Than

			Use the name as the definition of less than.
		"""
		return self.name < rhs.name

	def __init__(self, name):
		super(Project, self).__init__()

		self.name = name

	def getExpiredTimers(self, time_out, mark=False):
		result = []
		for job in self.getChildren():
			timers = job.getExpiredTimers(time_out, mark)
			result += timers

		return result

	def getName(self):
		return self.name

	def hasJob(self, name):
		return name in self and type(self[name]) == Job

	def getJob(self, name):
		if self.hasJob(name):
			return self[name]
		else:
			return None

	def addJob(self, name):
		if name in self:
			job = self[name]

			if type(job) != Job:
				job = None
		else:
			job = Job(name)
			self.addChildNode(job, NestedTreeNode.INSERT_ASCENDING)

		return job

# vim: ts=4 sw=4 noexpandtab nocin ai
