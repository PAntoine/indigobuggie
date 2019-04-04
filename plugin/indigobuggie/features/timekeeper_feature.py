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


	def __init__(self, configuration):
		super(TimeKeeperFeature, self).__init__(configuration)
		self.title = "Time Keeper"
		self.selectable = True
		self.user_not_typing = True
		self.current_job = None
		self.current_window = None
		self.loaded_ok = False

		if 'tracking' in configuration:
			self.is_tracking = (configuration['tracking'] == True or configuration['tracking'] == 1)
		else:
			self.is_tracking = False

		if 'use_repo' in configuration:
			self.use_repo = (configuration['use_repo'] == True or configuration['use_repo'] == 1)
		else:
			self.use_repo = False

		if 'default_project' in configuration:
			self.default_project = configuration['default_project']
		else:
			self.default_project = 'default'

		if 'default_job' in configuration:
			self.default_job = configuration['default_job']
		else:
			self.default_job = 'default'

		self.keylist = [KeyDefinition('<cr>', 	TimeKeeperFeature.TIME_KEEPER_SELECT,				False,	self.handleSelectItem,		"Select item."),
						KeyDefinition('p', 		TimeKeeperFeature.TIME_KEEPER_ADD_PROJECT,			False,	self.handleAddProject,		"Add a project to timekeeper."),
						KeyDefinition('j', 		TimeKeeperFeature.TIME_KEEPER_ADD_JOB,				False,	self.handleAddJob,			"Add a job."),
						KeyDefinition('a', 		TimeKeeperFeature.TIME_KEEPER_AMEND,				False,	self.handleAmendNote,		"Amend a note."),
						KeyDefinition('s', 		TimeKeeperFeature.TIME_KEEPER_STOP_START_TRACKING,	False,	self.handleToggleTracking,	"Stop/Start time tracking.")]

	def initialise(self, tab_window):
		result = super(TimeKeeperFeature, self).initialise(tab_window)

		if self.tab_window.getSetting('UseUnicode') == 1:
			self.render_items = unicode_markers
		else:
			self.render_items = ascii_markers

		self.makeResourceDir('timekeeper')
		self.timekeeper = beorn_lib.TimeKeeper(os.path.join(self.tab_window.getSetting('Config_directory'), 'timekeeper'))
		self.loaded_ok = self.timekeeper.load()

		self.scm_feature = self.tab_window.getFeature('SCMFeature')

		if self.is_tracking:
			self.userStartedTyping()
			self.is_tracking = True

		return result

	def getProjectName(self):
		project_feat = self.tab_window.getFeature('ProjectFeature')

		if project_feat is not None:
			result = project_feat.getProject().getValue('name')
		else:
			result = self.tab_window.getTabName()

		return result

	def getJobName(self):
		result = self.default_job
		scm_feature = self.tab_window.getFeature('SCMFeature')

		if scm_feature is not None:
			scm = scm_feature.findSCMForPath(self.tab_window.getWorkingRoot())

			if scm is not None:
				result = scm.getCurrentVersion()

		return result

	def userStoppedTyping(self):
		# remove 'lost' events
		self.tab_window.removeEventHandler('CursorHoldI')
		self.tab_window.removeEventHandler('CursorHold')
		self.tab_window.removeEventHandler('FocusLost')

		if self.is_tracking:
			# setup the event handlers for letting us know when the user starts typing again.
			self.tab_window.addEventHandler('CursorMovedI','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
			self.tab_window.addEventHandler('CursorMoved','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)
			self.tab_window.addEventHandler('FocusGained','TimeKeeperFeature', TimeKeeperFeature.USER_STARTED_TYPING)

		self.user_not_typing = True

		if self.start_time != 0:
			elapsed_time = int(time.time()) - self.start_time
			self.start_time = 0

			if self.current_job is not None:
				self.current_job.addTime(elapsed_time)
				self.renderTree()

	def userStartedTyping(self):
		# remove start events
		self.tab_window.removeEventHandler('CursorMovedI')
		self.tab_window.removeEventHandler('CursorMoved')
		self.tab_window.removeEventHandler('FocusGained')

		# we want the events for stopping typing
		if self.user_not_typing:
			self.tab_window.addEventHandler('CursorHoldI', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)
			self.tab_window.addEventHandler('CursorHold', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)
			self.tab_window.addEventHandler('FocusLost', 'TimeKeeperFeature', TimeKeeperFeature.USER_STOPPED_TYPING)

			self.start_time = int(time.time())

			if self.current_job is None:
				project = self.timekeeper.addProject(self.getProjectName())
				self.current_job = project.addJob(self.getJobName())

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
				redraw = True

		return (redraw, line_no)

	def handleAddJob(self, line_no, action):
		redraw = False

		item = self.timekeeper.findItemWithColour(line_no)

		if item is not None and type(item) == beorn_lib.Project:
			new_job = self.tab_window.getUserInput('New Job')

			if not item.hasJob(new_job):
				if item.addJob(new_job):
					redraw = True

		return (redraw, line_no)

	def handleAmendNote(self, line_no, action):
		result = False

		item = self.timekeeper.findItemWithColour(line_no)

		if item is not None:
			if type(item) == beorn_lib.timekeeper.Job:
				self.openNote(item)
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
		if self.loaded_ok:
			self.timekeeper.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
