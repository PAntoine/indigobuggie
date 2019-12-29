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
from settings_node import SettingsNode
from feature import Feature, KeyDefinition

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
		self.start_time = int(time.time())

		self.keylist = [KeyDefinition('<cr>', 	TimeKeeperFeature.TIME_KEEPER_SELECT,				False,	self.handleSelectItem,		"Select item."),
						KeyDefinition('p', 		TimeKeeperFeature.TIME_KEEPER_ADD_PROJECT,			False,	self.handleAddProject,		"Add a project to timekeeper."),
						KeyDefinition('j', 		TimeKeeperFeature.TIME_KEEPER_ADD_JOB,				False,	self.handleAddJob,			"Add a job."),
						KeyDefinition('a', 		TimeKeeperFeature.TIME_KEEPER_AMEND,				False,	self.handleAmendNote,		"Amend a note."),
						KeyDefinition('s', 		TimeKeeperFeature.TIME_KEEPER_STOP_START_TRACKING,	False,	self.handleToggleTracking,	"Stop/Start time tracking.")]

	def getDialog(self, settings):
		button_list = [	(self.use_repo,		"Use repository for job/project names"),
						(self.is_tracking,	"Is tracking turned on?") ]

		button_list_start = 4
		buttons_line = button_list_start + len(button_list) + 3

		dialog_layout = [
			beorn_lib.dialog.Element('TextField', {'name': 'default_job', 'title': 'Default Job', 'x': 19, 'y': 1, 'default': self.default_job}),
			beorn_lib.dialog.Element('TextField', {'name': 'default_project', 'title': 'Default Project', 'x': 15, 'y': 2, 'default': self.default_project}),
			beorn_lib.dialog.Element('ButtonList',{'name': 'settings', 'title': 'Settings', 'x': 15, 'y': button_list_start, 'width':64,'items': button_list, 'type': 'multiple'}),
			beorn_lib.dialog.Element('Button', {'name': 'ok', 'title': 'OK', 'x': 25, 'y': buttons_line}),
			beorn_lib.dialog.Element('Button', {'name': 'cancel', 'title': 'CANCEL', 'x': 36, 'y': buttons_line})
		]

		return beorn_lib.Dialog(beorn_lib.dialog.DIALOG_TYPE_TEXT, dialog_layout)

	def resultsFunction(self, settings, results):
		if self.use_repo != results['settings'][0]:
			self.use_repo = results['settings'][0]
			self.tab_window.setConfiguration('TimeKeeperFeature', 'use_repo', self.use_repo)

		if self.is_tracking != results['settings'][1]:
			self.is_tracking = results['settings'][1]
			self.tab_window.setConfiguration('TimeKeeperFeature', 'tracking', self.is_tracking)

		if self.default_job != results['default_job']:
			self.default_job = results['default_job']
			self.tab_window.setConfiguration('TimeKeeperFeature', 'default_job', self.default_job)

		if self.default_project != results['default_project']:
			self.default_project = results['default_project']
			self.tab_window.setConfiguration('TimeKeeperFeature', 'default_project', self.default_project)

	def getDefaultConfiguration(self):
		return { 'tracking': True, 'use_repo': True, 'default_project': 'default', 'default_job': 'default' }

	def getSettingsMenu(self):
		return SettingsNode('TimeKeeper', 'TimeKeeperFeature', None, self.getDialog, self.resultsFunction)

	def initialise(self, tab_window):
		result = super(TimeKeeperFeature, self).initialise(tab_window)

		if result:
			self.use_repo = beorn_lib.config.Config.toBool(tab_window.getConfiguration('TimeKeeperFeature', 'use_repo'))
			self.is_tracking = beorn_lib.config.Config.toBool(tab_window.getConfiguration('TimeKeeperFeature', 'tracking'))

			self.default_job = tab_window.getConfiguration('TimeKeeperFeature', 'default_job')
			self.default_project = tab_window.getConfiguration('TimeKeeperFeature', 'default_project')

			if self.tab_window.getSetting('UseUnicode') == 1:
				self.render_items = unicode_markers
			else:
				self.render_items = ascii_markers

			res_dir = self.makeResourceDir('timekeeper')
			self.timekeeper = beorn_lib.TimeKeeper(res_dir)
			self.loaded_ok = self.timekeeper.load()
			self.scm_feature = self.tab_window.getFeature('SCMFeature')

			if self.is_tracking:
				self.userStartedTyping()
				self.is_tracking = True

		return result

	def getProjectName(self):
		project_feat = self.tab_window.getFeature('SettingsFeature')
		result = self.tab_window.getTabName()

		return result

	def getJobName(self):
		result = self.default_job
		scm_feature = self.tab_window.getFeature('SCMFeature')

		if scm_feature is not None:
			scm = scm_feature.getActiveScm()

			if scm is not None:
				result = scm.getCurrentVersion()

		return result

	def userStoppedTyping(self):
		# remove 'lost' events
		self.tab_window.removeEventHandler('CursorHoldI', 'TimeKeeperFeature')
		self.tab_window.removeEventHandler('CursorHold', 'TimeKeeperFeature')
		self.tab_window.removeEventHandler('FocusLost', 'TimeKeeperFeature')

		if self.is_tracking:
			# setup the event handlers for letting us know when the user starts typing again.
			self.tab_window.addEventHandler('CursorMovedI','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
			self.tab_window.addEventHandler('CursorMoved','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
			self.tab_window.addEventHandler('FocusGained','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)

		self.user_not_typing = True

		if self.start_time != 0:
			elapsed_time = int(time.time()) - self.start_time
			self.start_time = 0

			project = self.timekeeper.addProject(self.getProjectName())

			if project.hasJob(self.getJobName()):
				self.current_job = project.getJob(self.getJobName())
			else:
				self.current_job = project.addJob(self.getJobName())

			if self.current_job is not None:
				self.current_job.addTime(elapsed_time)
				self.needs_saving = True
				self.renderTree()

	def userStartedTyping(self):
		# remove start events
		self.tab_window.removeEventHandler('CursorMovedI', 'TimeKeeperFeature')
		self.tab_window.removeEventHandler('CursorMoved', 'TimeKeeperFeature')
		self.tab_window.removeEventHandler('FocusGained', 'TimeKeeperFeature')

		# we want the events for stopping typing
		if self.user_not_typing:
			self.tab_window.addEventHandler('CursorHoldI', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)
			self.tab_window.addEventHandler('CursorHold', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)
			self.tab_window.addEventHandler('FocusLost', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)

			self.start_time = int(time.time())

			self.needs_saving = True
			self.user_not_typing = False
			self.is_tracking = True

	def startTrackingUser(self):
		if self.use_repo is None or self.scm_feature is not None:
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

	def render_function(self, last_visited_node, node, value, level, direction):
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

	def close(self):
		if self.loaded_ok and self.needs_saving:
			self.timekeeper.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
