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
#    file: timer task
#    desc: This is the class for holding a timer task.
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

TASK_TIMER_ONESHOT	= 1
TASK_TIMER_REPEAT	= 2
TASK_TIMER_UNTIL	= 3
TASK_TIMER_EXPIRED	= 4
TASK_TIMER_NON		= 5

class TimerTask(NestedTreeNode):
	valid_timers = [TASK_TIMER_ONESHOT, TASK_TIMER_REPEAT, TASK_TIMER_UNTIL, TASK_TIMER_NON]

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

	def __init__(self, name, status=TASK_STATUS_OPEN, notes=[], expiry_date=0, period=0, timer_type=TASK_TIMER_NON):
		super(TimerTask, self).__init__()

		self.name = name
		self.status = status
		self.expiry_date = int(expiry_date)
		self.period = period
		self.timer_type = timer_type
		self.line_no = 0
		self.column = 0
		self.start_time = int(time.time())
		self.time_out = 0

		if type(notes) == str or type(notes) == str:
			self.notes = notes.split('\x03')
		else:
			self.notes = notes

		self.setTimeOutTime()

	def toggleStatus(self):
		if self.status == TimerTask.TASK_STATUS_OPEN:
			self.status = TimerTask.TASK_STATUS_COMPLETE
		elif self.status == TimerTask.TASK_STATUS_COMPLETE:
			self.status = TimerTask.TASK_STATUS_ABANDONED
		else:
			self.status = TimerTask.TASK_STATUS_OPEN

	def getStatus(self):
		if self.hasChild():
			for child in self:
				result = TimerTask.TASK_STATUS_ABANDONED

				if child.getStatus() == TimerTask.TASK_STATUS_OPEN:
					result = TimerTask.TASK_STATUS_OPEN
					break
				elif child.getStatus() == TimerTask.TASK_STATUS_COMPLETE:
					result = TimerTask.TASK_STATUS_COMPLETE

			return result
		else:
			return self.status

	def setTimeOutTime(self):
		if self.timer_type == TASK_TIMER_ONESHOT:
			self.time_out = self.expiry_date

		elif self.timer_type == TASK_TIMER_REPEAT:
			now = int(time.time()) - self.start_time
			offset = self.period - (now % self.period)
			self.time_out = int(time.time()) + offset

		elif self.timer_type == TASK_TIMER_UNTIL and self.expiry_date > int(time.time()):
			now = int(time.time()) - self.start_time
			offset = self.period - (now % self.period)
			self.time_out = int(time.time()) + offset
		else:
			self.time_out = None

	def hasTimedOut(self, set_expired=False):
		if self.timer_type != TASK_TIMER_EXPIRED and self.time_out is not None and self.time_out <= int(time.time()):
			if set_expired:
				if self.timer_type == TASK_TIMER_ONESHOT:
					self.timer_type = TASK_TIMER_EXPIRED
				elif self.timer_type != TASK_TIMER_REPEAT and self.expiry_date <= int(time.time()):
					self.timer_type = TASK_TIMER_EXPIRED

			# update the timeout time.
			self.setTimeOutTime()

			return True
		else:
			return False

	def getTimeOutTime(self):
		return self.time_out

	def isExpired(self):
		return self.timer_type == TASK_TIMER_EXPIRED

	def isAuto(self):
		return False

	def isActive(self):
		return self.timer_type != TASK_TIMER_EXPIRED

	def getPosition(self):
		return (self.line_no, self.column)

	def getName(self):
		return self.name

	def getNotes(self):
		return self.notes

	def getFileName(self):
		return ''

	@classmethod
	def fromString(cls, string):
		parts = string.split(',')

		if len(parts) == 8:
			new_task = TimerTask(parts[1], int(parts[2]), parts[7].split('\x03', int(parts[3]), int(parts[4]), int(parts[5])))
			new_task.start_time = int(parts[6])
			return new_task
		else:
			return None

	def toString(self):
		return ','.join(["T",self.name, str(self.status), str(self.expiry_date), str(self.period), str(self.timer_type), str(self.start_time),'\x03'.join(self.notes)])

	def setTimer(self, timer_type, due_date=0, period=0):
		result = False
		now = int(time.time())

		if due_date > now and period >= 0 and timer_type in TimerTask.valid_timers:
			self.due_date = due_date
			self.period = period
			self.timer_type = timer_type
			result = True

		return result

	def getType(self):
		return self.timer_type

	def getTimeOut(self):
		return time.strftime("%Y-%m-%d %H:%M", time.gmtime(self.time_out))

	def getDueDate(self):
		return self.due_date

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
