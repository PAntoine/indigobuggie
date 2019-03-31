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
#    file: time_manager_feature
#    desc: This feature manages tasks.
#
#  author: peter
#    date: 19/01/2019
#---------------------------------------------------------------------------------
#                     Copyright (c) 2019 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
import beorn_lib
from feature import Feature, KeyDefinition

unicode_markers = ['▸', '▾', '±', 'r', '✗','☐','☑','☒']
ascii_markers   = ['>', 'v', '~', 'r', 'x','-','+','x']

class MyTasksFeature(Feature):
	TASK_MANAGER_SELECT			= 1
	TASK_MANAGER_NEW_GROUP		= 2
	TASK_MANAGER_NEW_TASK		= 3
	TASK_MANAGER_NEW_TIMER		= 4
	TASK_MANAGER_CANCEL_TASK	= 5
	TASK_MANAGER_EDIT_TASK		= 6
	TASK_MANAGER_TOGGLE_STATE	= 7
	TASK_MANAGER_GOTO			= 8

	MARKER_CLOSED			= 0
	MARKER_OPENED			= 1
	MARKER_ACTIVE			= 2
	MARKER_REPEAT			= 3
	MARKER_EXPIRED			= 4
	MARKER_TASK_OPEN		= 5
	MARKER_TASK_COMPLETE	= 6
	MARKER_TASK_ABANDONED	= 7
	MARKER_NONE_TIMER		= 5 # TODO: This flag is missing - ADD

	def __init__(self, configuration):
		result = super(MyTasksFeature, self).__init__(configuration)
		self.title = "Task Manager"
		self.selectable = True
		self.loaded_ok = False
		self.tasks = None
		self.note_window = None

		if 'auto_tasks' in configuration:
			self.auto_tasks = (configuration['auto_tasks'] == True or configuration['auto_tasks'] == 1)
		else:
			self.auto_tasks = False

		if 'markers' in configuration:
			self.marker_list = configuration['markers']
		else:
			self.marker_list = []

		self.keylist = [KeyDefinition('<cr>', 	MyTasksFeature.TASK_MANAGER_SELECT,			False,	self.handleSelectItem ,	"Select an Item."),
						KeyDefinition('t',		MyTasksFeature.TASK_MANAGER_TOGGLE_STATE,	False,	self.handleToggleState,	"Toggle the state of the object."),
						KeyDefinition('n',		MyTasksFeature.TASK_MANAGER_NEW_GROUP,		False,	self.handleNewGroup,	"Create a new Group."),
						KeyDefinition('a',		MyTasksFeature.TASK_MANAGER_NEW_TASK,		False,	self.handleNewTask,		"Create a new Task."),
						KeyDefinition('A',		MyTasksFeature.TASK_MANAGER_NEW_TIMER,		False,	self.handleNewTimer,	"Create a new Timer."),
						KeyDefinition('c',		MyTasksFeature.TASK_MANAGER_CANCEL_TASK,	False,	self.handleCancelTask,	"Cancel a timer Task."),
						KeyDefinition('e',		MyTasksFeature.TASK_MANAGER_EDIT_TASK,		False,	self.handleEditTask,	"Edit the task."),
						KeyDefinition('g',		MyTasksFeature.TASK_MANAGER_GOTO,			False,	self.handleGoto,		"Goto the auto task file and line.")
					]

	def initialise(self, tab_window):
		result = super(MyTasksFeature, self).initialise(tab_window)

		# Ok, do we have a specific project file to use?
		self.makeResourceDir('my_tasks')

		ib_config_dir = self.tab_window.getSetting('Config_directory')
		self.tasks = beorn_lib.Tasks(os.path.join(ib_config_dir, 'my_tasks'))

		if self.tab_window.getSetting('UseUnicode') == 1:
			self.render_items = unicode_markers
		else:
			self.render_items = ascii_markers

		self.loaded_ok = self.tasks.load()

		if self.auto_tasks:
			self.tab_window.addEventHandler('BufWritePost','MyTasksFeature', 0)

		self.tab_window = tab_window

		self.tasks.enableTaskTimeOutCallback(self.expiredTimerCallback)

		return True

	def renderTimer(self, task, level):
		if task.getStatus() == task.TASK_STATUS_OPEN:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_OPEN]
		elif task.getStatus() == task.TASK_STATUS_COMPLETE:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_COMPLETE]
		else:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_ABANDONED]

		t_type = task.getType()

		if t_type == beorn_lib.tasks.TASK_TIMER_REPEAT:
			timer_mark = self.render_items[MyTasksFeature.MARKER_REPEAT]

		elif t_type == beorn_lib.tasks.TASK_TIMER_EXPIRED:
			timer_mark = self.render_items[MyTasksFeature.MARKER_EXPIRED]

		elif t_type == beorn_lib.tasks.TASK_TIMER_NON:
			timer_mark = ' '
		else:
			timer_mark = self.render_items[MyTasksFeature.MARKER_ACTIVE]

		return '  '*level + state_marker + " " + task.getTimeOut() + " " + timer_mark + " " + task.name

	def renderTask(self, task, level):
		if task.getStatus() == task.TASK_STATUS_OPEN:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_OPEN]
		elif task.getStatus() == task.TASK_STATUS_COMPLETE:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_COMPLETE]
		else:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_ABANDONED]

		return '  '*level + state_marker + " " + task.name

	def renderGroup(self, task, level):
		if task.isOpen():
			marker = self.render_items[MyTasksFeature.MARKER_OPENED]
		else:
			marker = self.render_items[MyTasksFeature.MARKER_CLOSED]

		if task.getStatus() == beorn_lib.tasks.Task.TASK_STATUS_OPEN:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_OPEN]

		elif task.getStatus() == beorn_lib.tasks.Task.TASK_STATUS_COMPLETE:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_COMPLETE]

		else:
			state_marker = self.render_items[MyTasksFeature.MARKER_TASK_ABANDONED]

		return '  '*level + marker + " " + state_marker + " " + task.name

	def render_function(self, last_visited_node, node, value, level, direction):
		""" This function will collect the values from all nodes that
			it encounters in the order that they were walked.
		"""
		if value is None:
			value = []

		skip_children = False

		if node.__class__.__name__ == "Group":
			value.append(self.renderGroup(node, level))
			skip_children = not node.isOpen()

		elif node.__class__.__name__ == "Task":
			value.append(self.renderTask(node, level))
			skip_children = not node.isOpen()

		elif node.__class__.__name__ == "TimerTask":
			value.append(self.renderTimer(node, level))
			skip_children = not node.isOpen()
		else:
			if node.isOpen():
				value.append( level*' ' + self.render_items[MyTasksFeature.MARKER_OPENED]  + ' ' + node.name)
			else:
				value.append( level*' ' + self.render_items[MyTasksFeature.MARKER_CLOSED]  + ' ' + node.name)
				skip_children = True

		node.colour = len(value)

		return (node, value, skip_children)

	def renderTree(self):
		if self.is_selected and self.current_window is not None:
			contents = self.getHelp(self.keylist)
			contents += self.tasks.walkTree(self.render_function)
			self.tab_window.setBufferContents(self.buffer_id, contents)

	def select(self):
		result = super(MyTasksFeature, self).select()

		(self.current_window, self.buffer_id) = self.tab_window.openSideWindow("__ib_task_manager__", self.keylist)
		self.tab_window.setWindowSyntax(self.current_window, 'ib_my_task')
		self.renderTree()
		self.tab_window.setPosition(self.current_window, self.position)

	def unselect(self):
		result = super(MyTasksFeature, self).unselect()
		self.current_window = None
		self.tab_window.closeWindowByName("__ib_task_manager__")

	def onEvent(self, event_id, window_obj):
		if "ib_marker" not in window_obj.vars:
			# Ok, this is not one of our special windows:
			wind_cont = self.tab_window.getWindowContents(window_obj)

			for index,line in enumerate(wind_cont):
				for item in self.marker_list:
					pos = line.find(item)

					if pos > -1 and self.tab_window.findSyntaxGroup(index+1, pos+1, 'Comment'):
						begin_col = self.tab_window.findSyntaxBeginning(index+1, pos+1, 'Comment') + 1
						end = self.tab_window.findSyntaxRegionEnd(index+1, begin_col, 'Comment')

						content = []
						for buf_line in wind_cont[index:end]:
							content.append(buf_line[begin_col:])

						new_start = content[0].find(item)
						content[0] = content[0][new_start + len(item) + 1:].rstrip()

						self.tasks.updateAutoTask(index, begin_col, item, self.tab_window.getWindowName(window_obj), content, is_auto=True)

	def openNote(self, item):
		out_content = [	'# ' + item.getName() + ' #',
						'' ] + item.getNotes()

		self.note_window = self.tab_window.openFileWithContent('Task:' + item.getParent().getName() + "-" + item.getName(), out_content, readonly=item.isAuto())

		if not item.isAuto():
			self.tab_window.bufferLeaveAutoCommand()

		self.tab_window.setWindowSyntax(self.note_window, 'markdown')
		self.tab_window.setWindowVariable(self.note_window, '__ib_task_title__', item.getName())
		self.tab_window.setWindowVariable(self.note_window, '__ib_task_group__', item.getParent().getName())

	def handleSelectItem(self, line_no, action):
		redraw = False

		item = self.tasks.findItemWithColour(line_no)

		if item is not None:
			if item.hasChild() or item.__class__.__name__ == "Group":
				item.toggleOpen()
				redraw = True
			else:
				self.openNote(item)

		return (redraw, line_no)

	def handleToggleState(self, line_no, action):
		redraw = False

		item = self.tasks.findItemWithColour(line_no)

		if item is not None:
			if not item.hasChild():
				item.toggleStatus()
				redraw = True

		return (redraw, line_no)

	def handleGoto(self, line_no, action):
		redraw = False
		item = self.tasks.findItemWithColour(line_no)

		if item is not None and item.__class__.__name__ == "Task":
			file_name = item.getFileName()
			if file_name != '' and os.path.isfile(file_name):
				window = self.tab_window.openFile(file_name)
				self.tab_window.setWindowPos(window, item.getPosition()[0]+1)

		return (redraw, line_no)

	def handleNewGroup(self, line_no, action):
		redraw = False

		new_group = self.tab_window.getUserInput('New Group')

		if new_group != '' and not new_group in self.tasks:
			self.tasks.addChildNode(beorn_lib.tasks.Group(name=new_group))
			redraw = True

		return (redraw, line_no)

	def handleNewTask(self, line_no, action):
		redraw = False

		item = self.tasks.findItemWithColour(line_no)

		if item is not None:
			if item.__class__.__name__ == "Group":
				parent = item
			else:
				parent = item.getParent()

			new_task = self.tab_window.getUserInput('New Task Name')

			if new_task != '' and not new_task in parent:
				parent.addChildNode(beorn_lib.tasks.Task(name=new_task))
				redraw = True

		return (redraw, line_no)

	def validatePeriod(self, period_string, date=False):
		period = None

		try:
			period = int(period_string)

			if date:
				period += int(time.time())
		except ValueError:
			period = None

		if period is None and date:
			try:
				period = int(time.mktime(time.strptime(period_string, "%Y-%m-%d")))
			except:
				period = None

		if period is None:
			try:
				period = int(time.mktime(time.strptime(period_string, "%Y-%m-%d %h:%M")))
			except:
				period = None

		if period is None:
			parts = period_string.lower().split(' ')
			multipler = 0
			size = None

			if len(parts) == 2:
				try:
					size = float(parts[0])

					if parts[1][0] == 's':
						multipler = 1

					elif parts[1][0:2] == 'm':
						multipler = 60

					elif parts[1][0] == 'h':
						multipler = 60 * 60

					elif parts[1][0] == 'd':
						multipler = 60 * 60 * 24

					elif parts[1][0] == 'w':
						multipler = 60 * 60 * 24 * 7

					elif parts[1][0:2] == 'mo':
						multipler = 60 * 60 * 24 * 31	# Meh, 31 days will do

					elif parts[1][0] == 'y':
						multipler = 60 * 60 * 24 * 365 	# ignoring leap years

					if multipler != 0:
						period = size * multipler

				except ValueError:
					pass

		# if less that 10 years and a date, make it relative to now
		if period is not None and date and period < (60 * 60 * 24 * 365 * 10):
			period += int(time.time())

		return period

	def handleNewTimer(self, line_no, action):
		redraw = False

		item = self.tasks.findItemWithColour(line_no)

		if item is not None:
			if item.__class__.__name__ == "Group":
				parent = item
			else:
				parent = item.getParent()

			new_task = self.tab_window.getUserInput('New Timed Task Name')

			if new_task != '' and not new_task in parent:
				# O - one shot - until due date/time
				# R - repeat   - every period forever
				# U - repeat until - every period until due date/time
				task_object = None

				while task_object is None:
					timer_type = self.tab_window.getUserInput('Timer Type [O, R, U]')

					if timer_type == '':
						break

					if timer_type not in ['O','o','R','r','U','u', '']:
						continue

					if timer_type in ['U','u']:
						period = self.validatePeriod(self.tab_window.getUserInput('Specify Period'))

						if period is not None:
							expiry_date = self.validatePeriod(self.tab_window.getUserInput('Specify expiry Time'), date=True)

							if expiry_date is not None:
								task_object = beorn_lib.tasks.TimerTask(new_task, expiry_date=expiry_date, period=period, timer_type=beorn_lib.tasks.TASK_TIMER_UNTIL)

					elif timer_type in ['R','r']:
						period = self.validatePeriod(self.tab_window.getUserInput('Specify Period'))

						if period is not None:
								task_object = beorn_lib.tasks.TimerTask(new_task, period=period, timer_type=beorn_lib.tasks.TASK_TIMER_REPEAT)

					elif timer_type in ['O', 'o']:
						expiry_date = self.validatePeriod(self.tab_window.getUserInput('Specify expiry Time'), date=True)

						if expiry_date is not None:
							task_object = beorn_lib.tasks.TimerTask(new_task, expiry_date=expiry_date, timer_type=beorn_lib.tasks.TASK_TIMER_ONESHOT)


				if task_object is not None:
					parent.addChildNode(task_object)
					self.tasks.checkUpdateTaskTimeout()
					redraw = True

		return (redraw, line_no)

	def handleEditTask(self, line_no, action):
		redraw = False

		item = self.tasks.findItemWithColour(line_no)

		if item is not None and item.__class__.__name__ != "Group":
			pass			# TODO: handle the edit.
			redraw = True

		return (redraw, line_no)

	def handleCancelTask(self, line_no, action):
		redraw = False

		item = self.tasks.findItemWithColour(line_no)

		if item is not None and item.__class__.__name__ != "Group":
			item.cancelTask()
			redraw = True

		return (redraw, line_no)

	def onMouseClick(self, line, col):
		(redraw, line_no) = self.handleSelectItem(line, 0)
		if redraw:
			self.renderTree()
			self.tab_window.setPosition(self.tab_window.getCurrentWindow(), (line. col))

	def expiredTimerCallback(self, expired_item):
		self.renderTree()

	def onBufferWrite(self, window):
		title_name	= self.tab_window.getWindowVariable(window, '__ib_task_title__')
		group_name	= self.tab_window.getWindowVariable(window, '__ib_task_group__')

		if group_name in self.tasks:
			group = self.tasks[group_name]

			if title_name in group:
				item = group[title_name]
				item.updateNote(self.tab_window.getWindowContents(window))

		self.tab_window.clearModified(window)

	def close(self):
		self.tasks.disableTaskTimeOutCallback()
		if self.loaded_ok:
			self.tasks.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
