#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#	  _____			  _ _				 ______					   _
#	 (_____)		 | (_)				(____  \				  (_)
#		_	____   _ | |_  ____  ___	 ____)	)_	 _	____  ____ _  ____
#	   | | |  _ \ / || | |/ _  |/ _ \	|  __  (| | | |/ _	|/ _  | |/ _  )
#	  _| |_| | | ( (_| | ( ( | | |_| |	| |__)	) |_| ( ( | ( ( | | ( (/ /
#	 (_____)_| |_|\____|_|\_|| |\___/	|______/ \____|\_|| |\_|| |_|\____)
#						 (_____|					  (_____(_____|
#
#	 file: tab_window
#	 desc: Tab Window.
#
#  author: peter
#	 date: 01/10/2018
#---------------------------------------------------------------------------------
#					  Copyright (c) 2018 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import vim
import base64
from . import features
import beorn_lib
from threading import Lock
from collections import namedtuple as namedtuple

BackgroundServer = namedtuple('BackgroundServer', ['name', 'callback'])


class TabWindow(object):
	def __init__(self, name, tab_id, number):
		""" Initialise the TabWindow item """
		self.ident = tab_id
		self.name = name
		self.tab_number = number
		self.features = []
		self.displayed = False
		self.buffer_list = []
		self.selected_feature = None
		self.tree_lock = Lock()
		self.help_enabled = False
		self.active_timers = {}
		self.background_server = []
		self.resource_dir = None
		# working directory on open. As this may change and we need consistency.
		self.working_directory = vim.eval("getcwd()")

	def setCWD(self, directory):
		vim.command("cd " + directory)
		self.working_directory = vim.eval("getcwd()")

	def getCWD(self):
		return self.working_directory

	def toggle(self):
		self.displayed = not self.displayed

	def attachFeature(self, feature):
		self.features.append(feature)

	def initialiseFeatures(self):
		for feature in self.features:
			feature.initialise(self)

	def selectFeature(self, feature_name):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				if self.selected_feature is not None:
					self.selected_feature.unselect()

				self.selected_feature = feature
				self.selected_feature.select()
				break

	def setConfiguration(self, feature_name, item, value):
		settings = self.getFeature("SettingsFeature")
		return settings.setConfigItem(feature_name, item, value)

	def getConfiguration(self, feature_name, item):
		settings = self.getFeature("SettingsFeature")
		result = settings.getConfigItem(feature_name, item)

		if result is None:
			# did not find the configuration - see if it is in the feature
			# it might be new and the configuration file is out of date.
			feature = self.getFeature(feature_name)
			if feature is not None:
				config = feature.getDefaultConfiguration()

				if item in config:
					result = config[item]

		return result

	def unselectCurrentFeature(self):
		if self.selected_feature is not None:
			self.selected_feature.unselect()

	def selectCurrentFeature(self):
		if self.selected_feature is not None:
			self.selected_feature.select()

	def setPosition(self, window, position):
		if type(window) == type(vim.current.window):
			buf_num = window.number
		else:
			buf_num = vim.bindeval('winbufnr(' + str(window) + ')')

		if buf_num != -1:
			vim.command('call setpos(".", [' + str(buf_num) + ',' + str(position[0]) + ',' + str(position[1]) + ',0])')

	def getIdent(self):
		return self.ident

	def getTabName(self):
		return self.name

	def getTabNumber(self):
		return self.tab_number

	def getSetting(self, setting_name):
		name = '__tab_' + setting_name

		if name in vim.current.tabpage.vars:
			return vim.current.tabpage.vars[name]
		else:
			return vim.bindeval('g:IB_' + setting_name)

	def getPassword(self, prompt, default=None):
		if default is not None:
			result = vim.eval("inputsecret('" + prompt + ": ','" + default + "')")
		else:
			result = vim.eval("inputsecret('" + prompt + ": ')")
		vim.command("echo ")

		return result

	def getUserInput(self, prompt, default=None):
		if default is not None:
			result = vim.eval("input('" + prompt + ": ','" + default + "')")
		else:
			result = vim.eval("input('" + prompt + ": ')")
		vim.command("echo ")

		return result

	def entered(self):
		pass

	def left(self):
		pass

	def getFeature(self, feature_name):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				return feature

		return None

	def getFeatures(self):
		for feature in self.features:
			yield feature

	def renderTree(self):
		# HACK: TODO remove
		for feature in self.features:
			if feature.__class__.__name__ == "SourceTreeFeature":
				return feature.renderTree()

		return None

	def keyPressed(self, value, cursor_pos):
		if self.selected_feature is not None:
			self.selected_feature.keyPressed(value, cursor_pos)

	def setBufferContents(self, buff_id, contents, readonly=True):

		vim_mode = vim.eval("mode()")

		if vim_mode[0] != 'c' and vim_mode != 'r':
			if readonly:
				vim.buffers[buff_id].options['buftype'] = 'nofile'
				vim.buffers[buff_id].options['bufhidden'] = 'wipe'
				vim.buffers[buff_id].options['buflisted'] = False
				vim.buffers[buff_id].options['swapfile'] = False
				vim.buffers[buff_id].options['filetype'] = 'detect'

			vim.buffers[buff_id].options['modifiable'] = True

			# Avoid a vim crash it seems to not like updating empty buffers.
			if len(vim.buffers[buff_id]) == 0:
				vim.buffers[buff_id].append(contents)
			else:
				vim.buffers[buff_id][:] = contents

			if readonly:
				vim.buffers[buff_id].options['modifiable'] = False

			vim.buffers[buff_id].options['modified'] = False
			vim.command("redraw")

	def getUsefullWindow(self):
		wind_num = vim.bindeval("winnr('#')") - 1

		if "__ib_marker__" in vim.current.tabpage.windows[wind_num].buffer.vars:
			# ok, we are not going to use this - it is special, so search for another.
			if len(vim.current.tabpage.windows) == 2:
				if wind_num == 0:
					wind_num = 1
				else:
					wind_num = 0
			else:
				wind_num = -1
				for index, window in enumerate(vim.current.tabpage.windows):
					if "__ib_marker__" not in window.buffer.vars:
						# we have a winner!
						wind_num = index
						break
				else:
					# Ok, did not find one - so give up and create a new window.
					vim.command("silent rightbelow vsplit")
					wind_num = vim.bindeval("winnr()") - 1

		return wind_num + 1

	def findNotOurWindow(self):
		result = -1
		for index, window in enumerate(vim.current.tabpage.windows):
			if "__ib_marker__" not in window.buffer.vars:
				result = index + 1
				break

		return result

	def openFile(self, path):
		buf_number = int(vim.bindeval("bufnr('" + path + "')"))

		if len(vim.current.tabpage.windows) == 1:
			# Ok, the only window that is open is the menu window, open a new window.
			vim.command("silent rightbelow vsplit " + path)
		else:
			wind_num = self.getUsefullWindow()
			vim.command('silent  exe ' + str(wind_num) + ' . "wincmd w"')

		if buf_number == -1:
			# does not exist - open it.
			try:
				vim.command('silent edit ' + path)
			except vim.error:
				pass
		else:
			# bring the buffer to the current window.
			vim.command("silent buffer " + str(buf_number))

		return vim.current.window

	def openFileWithContent(self, name, contents, force_new=False, readonly=True, replace=False):
		# escape name - some chars cause problems
		name = name.replace('#', '\\#')

		buf_number = vim.bindeval("bufnr('" + name + "')")
		if int(buf_number) != -1:
			# the buffer exists? Is it in a window?
			wind_num = vim.bindeval("bufwinnr('" + str(buf_number) + "')")
			if wind_num != -1 and not replace:
				# If the buffer is in a window - lets exit.
				return
			else:
				self.setBufferContents(int(buf_number), contents, readonly=readonly)
		else:
			# we need to create the buffer.
			buf_number = vim.eval("bufnr('" + name + "', 1)")
			self.setBufferContents(int(buf_number), contents, readonly=readonly)

		# Ok, we have a buffer we need to put it in a window.
		if force_new:
			# easy, force new - always create a new window.
			vim.command("silent rightbelow vsplit " + name)
			wind_num = vim.bindeval("winnr()")
		else:
			wind_num = self.findNotOurWindow()

			if wind_num == -1:
				# did not find a good window --- create a new one
				vim.command("silent rightbelow vsplit " + name)
				wind_num = vim.bindeval("winnr()")

		# Ok, put the buffer in a window
		vim.command(str(wind_num) + " wincmd w")
		vim.command("silent buffer " + str(buf_number))

		buf = vim.buffers[int(buf_number)]
		if readonly:
			buf.options['buflisted'] = False
			buf.options['modifiable'] = False

		#vim.windows[wind_num].options['wrap'] = False

		return vim.current.window

	def bufferLeaveAutoCommand(self):
		vim.command("au BufWriteCmd <buffer> :py3 tab_control.onBufferWrite(vim.current.window)")

	def addEventHandler(self, event_name, feature_name, event_id, buffer_only=False):
		vim.command("augroup " + feature_name)

		if buffer_only:
			vim.command("au " + event_name + " <buffer> :py3 tab_control.onEventHandler('" + feature_name + "','" + str(event_id) + "', vim.current.window)")
		else:
			vim.command("au " + event_name + " * :py3 tab_control.onEventHandler('" + feature_name + "','" + str(event_id) + "', vim.current.window)")

		vim.command("augroup END")

	def removeEventHandler(self, event_name, feature_name):
		vim.command("augroup " + feature_name)
		vim.command("au! " + event_name + " *")
		vim.command("augroup END")

	def addCommand(self, feature_name, key_info, parameter):
		vim.command(":map <buffer> <silent> <leader>" + key_info.key_value + " :py3 tab_control.onCommand('" + feature_name + "','" + str(key_info.action) + "','" + parameter + "', vim.eval('getcurpos()'))<cr>")

	def addCommands(self, feature_name, keylist, parameter):
		for item in keylist:
			if item.command:
				vim.command(":map <buffer> <silent> <leader>" + item.key_value + " :py3 tab_control.onCommand('" + feature_name + "','" + str(item.action) + "','" + parameter + "', vim.eval('getcurpos()'))<cr>")

	def diffWindows(self, window_1, window_2):
		vim.command(str(window_2.number) + "wincmd w")
		vim.command("diffthis")
		vim.command(str(window_1.number) + "wincmd w")
		vim.command("diffthis")

	def diffModeOff(self):
		vim.command("diffoff!")

	def closeWindow(self, window):
		try:
			if vim.bindeval('winnr("$")') == 2:
				# create a spare empty window so the layout does not break
				vim.command("vnew")

			if type(window) == str or type(window) == str:
				wind_name = window.replace('#', '\\#')
				wind_name = wind_name.replace(':', '\\:')
				window = vim.bindeval('bufwinnr("' + wind_name + '")')

			if window != -1:
				vim.command("sign unplace * buffer=" + str(vim.current.window.buffer.number))
				vim.command(str(window) + "wincmd w")
				vim.command("q")
		except vim.error:
			pass

	def closeWindowByName(self, name):
		for buf in vim.buffers:
			if os.path.basename(buf.name) == name:
				vim.command("bwipe! " + name)
				break

	def findWindow(self, marker):
		result = None
		for window in vim.windows:
			if marker in window.vars:
				result = window
				break
		return result

	def openBottomWindow(self, name, contents=None):
		buf_num = int(vim.bindeval("bufnr('" + name + "',1)"))
		vim.command("bot new")
		vim.command("silent buffer " + str(buf_num))
		vim.command("setlocal bufhidden=wipe nobuflisted noswapfile nowrap")

		if contents is not None:
			vim.buffers[buf_num-1][:] = contents

		vim.current.buffer.vars['__ib_marker__'] = 1
		return vim.current.window

	def setSideWindowKeys(self, clear=False):
		if clear:
			vim.command(":mapclear <buffer>")

		settings = self.getFeature("SettingsFeature")
		key_list = settings.getConfigItem("SettingsFeature", 'select_keys')

		for key in key_list:
			vim.command(":map <buffer> <silent> " + key_list[key] + " :py3 tab_control.selectFeature('" + key + "')<cr>")

	def openSideWindow(self, name, keylist):
		buf_num = int(vim.bindeval("bufnr('" + name + "',1)"))
		vim.command("silent topleft 40 vsplit")
		vim.command("set winfixwidth")

		try:
			vim.command("set winwidth=40")
			vim.command("set winminwidth=40")

			vim.command("silent exe 'buffer! ' . " + str(buf_num))
			vim.command("setlocal buftype=nofile bufhidden=wipe nobuflisted noswapfile nowrap")

			vim.current.buffer.vars['__ib_marker__'] = 1
			vim.current.buffer.vars['__ib_side_window__'] = 1
		except vim.error:
			print("Failed to open side window - don't know why?", name)

		self.buffer_list.append(buf_num)

		for item in keylist:
			vim.command(":map <buffer> <silent> " + item.key_value + " :py3 tab_control.keyPressed(" + str(item.action) + ", vim.eval('getcurpos()'))<cr>")

		self.setSideWindowKeys()

		vim.command(":map <buffer> <silent> <LeftRelease> :py3 tab_control.onMouseClickHandler()<cr>")

		return (vim.current.window, buf_num)

	def setSideWindowPosition(self, line, col=None):
		for index, window in enumerate(vim.current.tabpage.windows, 1):
			if '__ib_side_window__' in window.buffer.vars:
				window.cursor = (line, window.cursor[1])

	def closeSideWindow(self):
		for index, window in enumerate(vim.current.tabpage.windows, 1):
			if '__ib_side_window__' in window.buffer.vars:
				vim.command(str(index) + " close")

	def findSyntaxGroup(self, line, column, highlight):
		result = False

		# interesting vim bug - calling synstack() set outside the range causes eval and bindval to crash.
		if len(vim.current.buffer[line-1]) < column:
			column = len(vim.current.buffer[line-1]) - 1

		if column > 0:
			stack = vim.eval('synstack(' + str(line) + ',' + str(column) + ')')

			for item in stack:
				if vim.eval('synIDattr(synIDtrans(' + str(item) + '), "name")') == highlight:
					result = True
					break

		return result

	def findSyntaxBeginning(self, line, column, hightlight):
		""" This function finds the beginning of the syntax group on the same line """
		result = column

		while result > 0:
			result -= 1

			if not self.findSyntaxGroup(line, result, hightlight):
				break

		return result

	def findSyntaxRegionEnd(self, start_line, column, hightlight):
		next_line = start_line
		last_line = vim.bindeval('line("$")') - 1

		while next_line < last_line:
			if self.findSyntaxGroup(next_line, column, hightlight):
				next_line += 1
			else:
				next_line -= 1
				break

		return next_line

	def getCurrentWindow(self):
		return vim.current.window

	def setWindowPos(self, window, position):
		vim.command(str(window.number) + " wincmd w")
		vim.command('call setpos(".", [' + str(window.buffer.number) + ',' + str(position) + ', 0, 0])')

	def addSigns(self, window, positions):
		if type(window) == type(vim.current.window) and window.valid:
			buf_num = window.buffer.number

			if buf_num != -1:
				for index, pos in enumerate(positions):
					if pos.type == 0:
						vim.command("sign place " + str(index+1) + " line=" + str(pos.start+1) + " name=ib_line buffer=" + str(buf_num))
					else:
						vim.command("sign place " + str(index+1) + " line=" + str(pos.start+1) + " name=ib_item buffer=" + str(buf_num))

	def isNormalWindow(self, window_obj=None):
		if window_obj is None:
			# assume we want the current window.
			window_obj = self.getCurrentWindow()

		if window_obj is None or window_obj.buffer is None:
			return False
		else:
			return window_obj.buffer.options['buftype'] == '' and '__ib_marker__' not in window_obj.buffer.vars

	def setWindowVariable(self, window_obj, name, value):
		if type(window_obj) == type(vim.current.window) and window_obj.valid:
			window_obj.vars[name] = value

	def getWindowVariable(self, window_obj, name):
		if type(window_obj) == type(vim.current.window) and window_obj.valid and name in window_obj.vars:
			return window_obj.vars[name]
		else:
			return None

	def setWindowSyntax(self, window_obj, syntax_format):
		if type(window_obj) == type(vim.current.window) and window_obj.valid:
			# The following should work, but does not - so having to do it the wrong way.
			#window_obj.buffer.options['syntax'] = syntax_format
			vim.command("setlocal syntax=" + syntax_format)

	def setWindowContents(self, window_obj, contents, readonly):
		if type(window_obj) == type(vim.current.window) and window_obj.valid:
			window_obj.buffer[:] = contents
			window_obj.buffer.options['modified'] = 0

			if readonly:
				window_obj.buffer.options['modifiable'] = 0

			vim.command("redraw")

	def getWindowContents(self, window_obj):
		if type(window_obj) == type(vim.current.window) and window_obj.valid:
			return window_obj.buffer[:]
		else:
			return None

	def getWindowName(self, window_obj=None):
		if window_obj is None:
			if  vim.current.buffer is None:
				return ''
			else:
				return vim.current.buffer.name

		elif type(window_obj) == type(vim.current.window) and window_obj.valid:
			return window_obj.buffer.name
		else:
			return ''

	def getResourceDir(self, project_name=None):
		""" This function will find the project config file. This maybe in one of a few
			locations.

				1. if project_name is not None, search in the config directory.
				2. if use_local is set, then look for a project.ipf in the project tree.
				3. else, we scan the projects in the project config directory, load the
				config and see if the current directory is a child of any of the projects
				root directories.

			WARNING: This remembers the result of the first call by settings. So that
			         it might not make sense when reading why it works. Soz. But this
					 note should help. :)
		"""
		result = None

		if self.resource_dir is not None:
			return self.resource_dir
		else:
			resource_root =	os.path.expanduser(self.getSetting("config_directory")).decode("utf-8")

			if self.getSetting("use_local_dir") == 1:
				return os.getcwd()

			elif project_name is not None and project_name != "":
				result = os.path.join(resource_root, project_name)
			else:
				if self.getSetting('use_local_dir') == 1:
					if os.path.isfile('project.ipf'):
						return os.path.join(os.path.cwd())
					else:
						for path, dirs, files in os.walk(os.path.cwd()):
							for f in files:
								if f == 'project.ipf':
									result = os.path.join(path)
									break
				else:
					# Ok, lets see if the CWD is part of the root_directory of one of the projects.
					for dir_name in os.listdir(resource_root):
						check_file = os.path.join(resource_root, dir_name, 'project.ipf')

						if os.path.isfile(check_file):
							project_config = beorn_lib.Config(check_file)
							project_config.load()

							root_dir = project_config.find("SettingsFeature", 'root_directory')

							if root_dir is not None:
								# is the current working directory equal to or a sub directory of the root directory in the project.
								if os.path.commonprefix([root_dir, os.getcwd()]) == root_dir:
									# does the directory contain a "project.ipf" file?
									result = os.path.join(resource_root, dir_name)
									break

				if result is None:
					# we need to default to the default project name
					result = os.path.join(resource_root, os.path.basename(os.getcwd()))

		# lets not change the dir at runtime - and save a few cycles.
		self.resource_dir = result

		return result

	def clearModified(self, window_obj):
		if type(window_obj) == type(vim.current.window) and window_obj.valid:
			window_obj.buffer.options['modified'] = 0

	def getCurrentPos(self):
		pos = vim.bindeval('getcurpos()')
		return (pos[1], pos[2])

	def onBufferWrite(self, window_number):
		if self.selected_feature is not None:
			self.selected_feature.onBufferWrite(window_number)

	def isHelpEnabled(self):
		return self.help_enabled

	def _renderDialog(self, dialog, old_line, old_col):
		vim.current.buffer.options['modifiable']	= True

		# Why? This avoids a rendering issue with GVIM and the underline character.
		vim.current.buffer[old_line] = ' '*old_col + 'x'
		vim.command("redraw")
		vim.current.buffer[old_line] = ' '*old_col + ' '
		vim.command("redraw")
		# Oh, the bit of the screen with the cursor on must change.

		vim.current.buffer[:] = dialog.getScreen()
		vim.current.buffer.options['modifiable']	= False

		(col, line) = dialog.getCursorPos()
		if (col, line) != (0, 0):
			# add a cursor
			aline = vim.current.buffer[line]

			# check the cursor is in the field.
			if col <= len(aline):
				if aline[col-1] == ' ':
					nline = aline[:col-1] + '_' + aline[col:]
				else:
					nline = aline[:col] + '\u0332' + aline[col:]
			else:
				nline = aline

			vim.current.buffer.options['modifiable']	= True
			vim.current.buffer[line] = nline
			vim.current.buffer.options['modifiable']	= False
			vim.command("redraw")

		return (line, col)

	def showDialog(self, settings):
		""" show dialog

			This function handles drawing the dialog for the vim client.
			This will handle the actual working of the dialog and the managing
			of handing the key inputs. This function will not return until
			the user has exited the menu.
		"""
		exit_dialog = False

		# HACK: These values need to be exposed from within the dialog.,
		key_conversion_dict = {
				'KEY_VALUE_EXIT':		-1,
				'KEY_VALUE_UP':			0,
				'KEY_VALUE_DOWN':		1,
				'KEY_VALUE_LEFT':		2,
				'KEY_VALUE_RIGHT':		3,
				'KEY_VALUE_SELECT':		4,
				'KEY_VALUE_DELETE':		5,
				'KEY_VALUE_BACKSPACE':	6,
				'KEY_VALUE_TAB':		7}

		current_window = vim.current.window
		dialog = settings.getDialog(settings)

		if dialog is not None:
			dialog.resetDialog()

			# create the window
			wind_num = self.getUsefullWindow()
			vim.command('silent  exe ' + str(wind_num) + ' . "wincmd w"')

			# need to display the client
			vim.current.buffer.options['buftype']		= 'nofile'
			vim.current.buffer.options['bufhidden']		= 'wipe'
			vim.current.buffer.options['buflisted']		= False
			vim.current.buffer.options['swapfile']		= False
			vim.current.buffer.options['modifiable']	= False
			vim.current.buffer.options['syntax']		= 'beorn_menu'

			# set the vim window options
			vim.current.window.options['wrap']			= False

			(old_line, old_col) = self._renderDialog(dialog, 0, 0)

			# handle the keyboard loop.
			while not exit_dialog:
				key = vim.eval('Beorn_waitForKeypress()')

				if len(key) > 1:
					if key in key_conversion_dict:
						# special keys need to convert
						key = key_conversion_dict[key]
					else:
						key = ' '

				if key == -1:
					print("Exit has been pressed")
					break

				(exit_dialog, refresh) = dialog.handleKeyboardInput(key)

				if refresh:
					(old_line, old_col) = self._renderDialog(dialog, old_line, old_col)

			# get the result of the dialog input
			if exit_dialog:
				settings.handleResults(dialog.getResult())

			# clear the screen on exit
			# TODO: should close the buffer, go back to the previous buffer.
			vim.current.buffer.options['modifiable']	= True
			vim.current.buffer[:] = []

			# go back to the window we started from
			vim.current.window = current_window

	def toggleHelp(self):
		self.help_enabled = not self.help_enabled
		if self.selected_feature is not None:
			self.selected_feature.renderTree()

	def getHelp(self):
		result = ['Help - Selectable Features:']

		for feature in self.features:
			if feature.isSelectable():
				result.append("  <c-i><c-" + feature.getFeatureKey() + "> " + feature.getTitle())

		return result

	def onCommand(self, feature_name, command_id, parameter, window_number):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				feature.onCommand(command_id, parameter, window_number)

	def onEventHandler(self, feature_name, event_id, window_obj):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				feature.onEvent(event_id, window_obj)

	def onMouseClickHandler(self):
		if self.selected_feature is not None:
			pos = vim.eval('getcurpos()')
			self.selected_feature.onMouseClick(int(pos[1])-1, int(pos[2]))

	def onTimerCallbackHandler(self, timer_id):
		if timer_id in self.active_timers:
			self.active_timers[timer_id](timer_id)

	def startTimerTask(self, timer_callback):
		result = int(vim.eval('timer_start(1000, "IB_TimerCallBack", {"repeat": -1})'))
		self.active_timers[result] = timer_callback
		return result

	def stopTimerTask(self, timer_id):
		if timer_id in self.active_timers:
			vim.eval('timer_stop(' + str(timer_id) + ')')
			del self.active_timers[timer_id]

	def startBackgroundServer(self, server_name, server_callback, parameter):
		result = False
		found = False

		for bs in self.background_server:
			if bs is not None and bs.name == server_name:
				found = True
				break

		if found is not True:
			command = 'call IB_StartBackgroundServer(' + str(self.ident) + ',' + str(len(self.background_server)) + ',\"' + server_name + '\",\"' + base64.b64encode(bytes(parameter, "utf-8")).decode() + '\")'
			vim.command(command)
			self.background_server.append(BackgroundServer(server_name, server_callback))
			result = True

		return result

	def sendBackgroundServerMessage(self, server_name, message):
		for bs in self.background_server:
			if bs is not None and bs.name == server_name:
				vim.eval('ch_sendraw(' + str(bs.channel) + ', ' + message + ')')
				break

	def onServerCallback(self, server_id, message):
		s_id_int = int(server_id)

		if len(self.background_server) > s_id_int and self.background_server[s_id_int] is not None:
				self.background_server[s_id_int].callback(message)

	def stopBackgroundServer(self, server):
		for index,bs in enumerate(self.background_server):
			if bs is not None and bs.name == server:
				# TODO: fix this
				#vim.eval('IB_StopBackgroundServer(' + str(index) + ')')
				self.background_server[index] = None
				break

	def close(self):
		for feature in self.features:
			feature.close()

		for buff in self.buffer_list:
			try:
				vim.command("bwipe! " + str(buff))
			except vim.error:
				pass

		self.features = []

# vim: ts=4 sw=4 noexpandtab nocin ai
