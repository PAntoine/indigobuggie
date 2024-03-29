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
#    file: timekeeper_feature
#    desc: This is time tracking feature.
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
import beorn_lib
from threading import Thread, Event
from .settings_node import SettingsNode
from .feature import Feature, KeyDefinition

MARKER_CLOSED		= 0
MARKER_OPEN			= 1

unicode_markers = [ '▸', '▾']
ascii_markers   = [ '>', 'v']

class TimeKeeperFeature(Feature):
	TIME_KEEPER_SELECT					= 1
	TIME_KEEPER_ADD_PROJECT				= 2
	TIME_KEEPER_ADD_JOB					= 3
	TIME_KEEPER_AMEND					= 4
	TIME_KEEPER_STOP_START_TRACKING		= 5

	USER_STARTED_TYPING = 1
	USER_STOPPED_TYPING = 2

	def __init__(self):
		super(TimeKeeperFeature, self).__init__()
		self.title = "Time Keeper"
		self.selectable = True
		self.user_not_typing = True
		self.current_job = None
		self.current_window = None
		self.loaded_ok = False
		self.needs_saving = False
		self.stopped_typing = 0
		self.started_typing = 0
		self.timer_task = None

		self.keylist = [KeyDefinition('<cr>', 	TimeKeeperFeature.TIME_KEEPER_SELECT,				False,	self.handleSelectItem,		"Select item."),
						KeyDefinition('p', 		TimeKeeperFeature.TIME_KEEPER_ADD_PROJECT,			False,	self.handleAddProject,		"Add a project to timekeeper."),
						KeyDefinition('j', 		TimeKeeperFeature.TIME_KEEPER_ADD_JOB,				False,	self.handleAddJob,			"Add a job."),
						KeyDefinition('a', 		TimeKeeperFeature.TIME_KEEPER_AMEND,				False,	self.handleAmendNote,		"Amend a note."),
						KeyDefinition('s', 		TimeKeeperFeature.TIME_KEEPER_STOP_START_TRACKING,	False,	self.handleToggleTracking,	"Stop/Start time tracking.")]

	def getDialog(self, settings):
		button_list = [	(self.tab_window.getConfiguration('TimeKeeperFeature', 'use_repo'),	"Use repository for job/project names"),
						(self.tab_window.getConfiguration('TimeKeeperFeature', 'tracking'),	"Is tracking turned on?") ]

		button_list_start = 4
		buttons_line = button_list_start + len(button_list) + 4

		dialog_layout = [
			beorn_lib.dialog.Element('TextField', {'name': 'default_job',		'title': 'Default Job',		'x': 19, 'y': 1, 'default': self.tab_window.getConfiguration('TimeKeeperFeature', 'default_job')}),
			beorn_lib.dialog.Element('TextField', {'name': 'default_project',	'title': 'Default Project', 'x': 15, 'y': 2, 'default': self.tab_window.getConfiguration('TimeKeeperFeature', 'default_project')}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'settings',			'title': 'Settings',		'x': 15, 'y': button_list_start, 'width':64,'items': button_list, 'type': 'multiple'}),
			beorn_lib.dialog.Element('TextField', {'name': 'max_stop_time',		'title': 'Max Idle Time',	'x': 15, 'y': button_list_start + len(button_list) + 2, 'width': 10,
																													'default': str(self.tab_window.getConfiguration('TimeKeeperFeature', 'max_stop_time')), 'input_type':'numeric'}),
			beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': buttons_line}),
			beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 36, 'y': buttons_line})
		]

		return beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

	def resultsFunction(self, settings, results):
		self.tab_window.setConfiguration('TimeKeeperFeature', 'use_repo', results['settings'][0])
		self.tab_window.setConfiguration('TimeKeeperFeature', 'tracking', results['settings'][1])

		if 'default_job' in results:
			self.tab_window.setConfiguration('TimeKeeperFeature', 'default_job', results['default_job'])

		if "default_project" in results:
			self.tab_window.setConfiguration('TimeKeeperFeature', 'default_project', results['default_project'])

		if "max_stop_time" in results:
			self.tab_window.setConfiguration('TimeKeeperFeature', 'max_stop_time', results['max_stop_time'])

	def getDefaultConfiguration(self):
		return {'tracking': True,
				'use_repo': True,
				'default_project': 'default',
				'default_job': 'default',
				'max_stop_time': 600}

	def getSettingsMenu(self):
		return SettingsNode('TimeKeeper', 'TimeKeeperFeature', None, self.getDialog, self.resultsFunction)

	def initialise(self, tab_window):
		result = super(TimeKeeperFeature, self).initialise(tab_window)

		if result:
			if self.tab_window.getSetting('UseUnicode') == 1:
				self.render_items = unicode_markers
			else:
				self.render_items = ascii_markers

			res_dir = self.makeResourceDir('timekeeper')
			self.timekeeper = beorn_lib.TimeKeeper(res_dir)
			self.loaded_ok = self.timekeeper.load()

			self.closedown = Event()

			# Issue: This needs to be a process.
			# Also poll_period needs to be in the config.
			if beorn_lib.config.Config.toBool(tab_window.getConfiguration('TimeKeeperFeature', 'use_repo')) is True:
				if self.tab_window.getFeature('SCMFeature') is not None:
					self.poll_period = 36
					self.timer_task = Thread(target=self.polling_scm_function)
					self.timer_task.start()

			if beorn_lib.config.Config.toBool(tab_window.getConfiguration('TimeKeeperFeature', 'tracking')) is True:
				self.userStartedTyping()

		return result

	def getProjectName(self):
		result = self.tab_window.getTabName()

		return result

	def getJobName(self):
		result =  self.tab_window.getConfiguration('TimeKeeperFeature', 'default_job')
		scm_feature = self.tab_window.getFeature('SCMFeature')

		if scm_feature is not None:
			scm = scm_feature.getActiveScm()

			if scm is not None:
				result = scm.getCurrentVersion()

		return result

	def updateTime(self, start_time, end_time):
		# only add the last start to stop time.
		elapsed_time = (end_time - start_time)
		if self.current_job is not None:
			self.current_job.addTime(elapsed_time)

		return elapsed_time

	def userStoppedTyping(self):
		now = int(time.time())

		# time changed update the time.
		if self.updateTime(self.started_typing, now) > 0:
			self.renderTree()

		# remove 'lost' events
		self.tab_window.removeEventHandler('CursorHoldI', 'TimeKeeperFeature')
		self.tab_window.removeEventHandler('CursorHold', 'TimeKeeperFeature')
		self.tab_window.removeEventHandler('FocusLost', 'TimeKeeperFeature')

		if self.is_tracking:
			# setup the event handlers for letting us know when the user starts typing again.
			self.tab_window.addEventHandler('CursorMovedI','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
			self.tab_window.addEventHandler('CursorMoved','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
			self.tab_window.addEventHandler('FocusGained','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
		else:
			# can't trust start time.
			self.started_typing = now

		self.stopped_typing = now
		self.started_typing = now
		self.user_not_typing = True

	def userStartedTyping(self):
		now = int(time.time())

		# does the stop time count, if it is less that max_stop_time then add it.
		# some reason after vim sends a stop - it sends a start, so lets ignore
		# it if stop time is zero.
		stop_duration = (now - self.stopped_typing)

		if stop_duration > 0:
			if stop_duration < int(self.tab_window.getConfiguration('TimeKeeperFeature', 'max_stop_time')):
				if self.updateTime(self.stopped_typing, now) > 0:
					self.renderTree()

			# remove start events
			self.tab_window.removeEventHandler('CursorMovedI', 'TimeKeeperFeature')
			self.tab_window.removeEventHandler('CursorMoved', 'TimeKeeperFeature')
			self.tab_window.removeEventHandler('FocusGained', 'TimeKeeperFeature')

			# we want the events for stopping typing
			if self.user_not_typing:
				self.tab_window.addEventHandler('CursorHoldI', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)
				self.tab_window.addEventHandler('CursorHold', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)
				self.tab_window.addEventHandler('FocusLost', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)

				self.needs_saving = True
				self.user_not_typing = False
				self.is_tracking = True

		self.stopped_typing = now
		self.started_typing = now

	def startTrackingUser(self):
			self.userStartedTyping()

	def select(self):
		super(TimeKeeperFeature, self).select()

		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_timekeeper__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_timekeeper')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)

	def unselect(self):
		super(TimeKeeperFeature, self).unselect()
		self.tab_window.closeWindowByName("__ib_timekeeper__")

	def renderJob(self, job):
		if job.hasChild():
			if job.isOpen():
				marker = self.render_items[MARKER_OPEN]
			else:
				marker = self.render_items[MARKER_CLOSED]
		else:
			marker = ' '

		# TODO: use a format line to max/mix the name and to get it to line up.
		return '   ' + marker + " " + job.name + " " + job.getTotalString()

	def render_function(self, last_visited_node, node, value, level, direction, parameter):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		skip_children = False

		if node.__class__.__name__ == "Job":
			value.append(self.renderJob(node))
			skip_children = not node.isOpen()

		else:
			if node.isOpen():
				value.append( level*' ' + self.render_items[MARKER_OPEN]  + ' ' + node.name)
			else:
				value.append( level*' ' + self.render_items[MARKER_CLOSED]  + ' ' + node.name)
				skip_children = True

		node.colour = len(value)

		return (node, value, skip_children)

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			contents = self.getHelp(self.keylist)
			contents += self.timekeeper.walkTree(self.render_function)
			self.tab_window.setBufferContents(self.buffer_id, contents)

	def handleSelectItem(self, line_no, action):
		redraw = False

		item = self.timekeeper.findItemWithColour(line_no)

		if item is not None:
			item.toggleOpen()
			redraw = True

		return (redraw, line_no)

	def handleAddProject(self, line_no, action):
		new_project = self.tab_window.getUserInput('New Project')

		if not self.timekeeper.hasProject(new_project):
			if self.timekeeper.addProject(new_project):
				self.needs_saving = True
				redraw = True

		return (redraw, line_no)

	def handleAddJob(self, line_no, action):
		redraw = False

		item = self.timekeeper.findItemWithColour(line_no)

		if item is not None and type(item) == beorn_lib.Project:
			new_job = self.tab_window.getUserInput('New Job')

			if not item.hasJob(new_job):
				if item.addJob(new_job):
					self.needs_saving = True
					redraw = True

		return (redraw, line_no)

	def handleAmendNote(self, line_no, action):
		result = False

		item = self.timekeeper.findItemWithColour(line_no)

		if item is not None:
			if type(item) == beorn_lib.timekeeper.Job:
				self.openNote(item)
				self.needs_saving = True
				result = True

		return (result, line_no)

	def openNote(self, item):
		content = item.getNote()
		title = "__ib__note_window__"

		self.tab_window.openFileWithContent(title, content, readonly=False)
		self.tab_window.bufferLeaveAutoCommand()

		self.tab_window.setWindowSyntax(self.tab_window.getCurrentWindow(), 'markdown')
		self.tab_window.setWindowVariable(self.tab_window.getCurrentWindow(), '__timekeeper_project__', item.getParent().getName())
		self.tab_window.setWindowVariable(self.tab_window.getCurrentWindow(), '__timekeeper_note_title__', item.getName())

	def handleToggleTracking(self, line_no, action):
		if self.is_tracking:
			self.is_tracking = False
			self.userStoppedTyping()
		else:
			self.userStartedTyping()

		return (True, line_no)

	def onMouseClick(self, line, col):
		(redraw, line_no) = self.handleSelectItem(line, 0)
		if redraw:
			self.renderTree()
			self.tab_window.setPosition(self.tab_window.getCurrentWindow(), (line_no, col))

	def onEvent(self, event_id, window_obj):
		if int(event_id) == TimeKeeperFeature.USER_STARTED_TYPING:
			self.userStartedTyping()

		elif int(event_id) == TimeKeeperFeature.USER_STOPPED_TYPING:
			self.userStoppedTyping()

	def polling_scm_function(self):
		while not self.closedown.wait(self.poll_period):
			if self.is_tracking:
				project = self.timekeeper.addProject(self.getProjectName())
				job = self.getJobName()

				if project.hasJob(job):
					self.current_job = project.getJob(job)
				else:
					self.current_job = project.addJob(job)

	def close(self):
		if self.timer_task is not None:
			self.closedown.set()

		if self.loaded_ok and self.needs_saving:
			self.timekeeper.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
