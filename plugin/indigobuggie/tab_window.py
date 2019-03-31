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
from threading import Lock

class TabWindow(object):
	def __init__(self, tab_id, name, number, root):
		""" Initialise the MutiTrack item """
		self.ident = tab_id
		self.name = name
		self.root = root
		self.tab_number = number
		self.features = []
		self.displayed = False
		self.buffer_list = []
		self.selected_feature = None
		self.tree_lock = Lock()
		self.help_enabled = False

	def toggle(self):
		self.displayed = not self.displayed

	def attachFeature(self, feature):
		self.features.append(feature)
		feature.initialise(self)

	def selectFeature(self, feature_name):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				if self.selected_feature is not None:
					self.selected_feature.unselect()

				self.selected_feature = feature
				self.selected_feature.select()
				break

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

	def getTabNumber(self):
		return self.tab_number

	def getSetting(self, setting_name):
		name = '__tab_' + setting_name

		if name in vim.current.tabpage.vars:
			return vim.current.tabpage.vars[name]
		else:
			return vim.bindeval('g:IB_' + setting_name)

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

	def lockTree(self):
		return self.tree_lock.acquire()

	def releaseTree(self):
		return self.tree_lock.release()

	def getTree(self, feature_name):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				return feature.getTree()

		return None

	def getFeature(self, feature_name):
		for feature in self.features:
			if feature.__class__.__name__ == feature_name:
				return feature

		return None

	def getSCMFeature(self):
		for feature in self.features:
			if feature.__class__.__name__ == "SCMFeature":
				return feature

		return None

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
		vim.buffers[buff_id].options['modifiable'] = 1
		vim.buffers[buff_id][:] = contents

		if readonly:
			vim.buffers[buff_id].options['modifiable'] = 0
		vim.buffers[buff_id].options['modified'] = 0
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
				for index,window in enumerate(vim.current.tabpage.windows):
					if "__ib_marker__" not in window.buffer.vars:
						# we have a winner!
						wind_num = index
						break
				else:
					# Ok, did not find one - so give up and create a new window.
					vim.command("silent rightbelow vsplit " + path)
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
			vim.command('silent  exe ' + str(wind_num)  + ' . "wincmd w"')

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

		if readonly:
			vim.command("setlocal buftype=nofile")

		vim.command("setlocal bufhidden=wipe nobuflisted noswapfile nowrap")

		return vim.current.window

	def bufferLeaveAutoCommand(self):
		vim.command("au BufWriteCmd <buffer> :py tab_control.onBufferWrite(vim.current.window)")

	def addEventHandler(self, event_name, feature_name, event_id, buffer_only=False):
		if buffer_only:
			vim.command("au " + event_name + " <buffer> :py tab_control.onEventHandler('" + feature_name + "','" + str(event_id) + "', vim.current.window)")
		else:
			vim.command("au " + event_name + " * :py tab_control.onEventHandler('" + feature_name + "','" + str(event_id) + "', vim.current.window)")

	def removeEventHandler(self, event_name):
		vim.command("au! " + event_name + " *")

	def addCommand(self, feature_name, key_info, parameter):
		vim.command(":map <buffer> <silent> <leader>" + key_info.key_value + " :py tab_control.onCommand('" + feature_name + "','" + str(key_info.action) + "','" + parameter + "', vim.eval('getcurpos()'))<cr>")

	def addCommands(self, feature_name, keylist, parameter):
		for item in keylist:
			if item.command:
				vim.command(":map <buffer> <silent> <leader>" + item.key_value + " :py tab_control.onCommand('" + feature_name + "','" + str(item.action) + "','" + parameter + "', vim.eval('getcurpos()'))<cr>")

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

			if type(window) == str or type(window) == unicode:
				window = vim.bindeval('bufwinnr("' + window + '")')

			vim.command("sign unplace * buffer=" + str(vim.current.window.buffer.number))
			vim.command(str(window) + "wincmd w")
			vim.command("q")
		except vim.error, e:
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

	def openSideWindow(self, name, keylist):
		buf_num = int(vim.bindeval("bufnr('" + name + "',1)"))
		vim.command("silent topleft 40 vsplit")
		vim.command("set winfixwidth")

		try:
			vim.command("set winwidth=40")
			vim.command("set winminwidth=40")
		except vim.error:
			pass

		vim.command("silent exe 'buffer ' . " + str(buf_num))
		vim.command("setlocal buftype=nofile bufhidden=wipe nobuflisted noswapfile nowrap")

		vim.current.buffer.vars['__ib_marker__'] = 1
		vim.current.buffer.vars['__ib_side_window__'] = 1

		self.buffer_list.append(buf_num)

		for item in keylist:
			vim.command(":map <buffer> <silent> " + item.key_value + " :py tab_control.keyPressed(" + str(item.action) + ", vim.eval('getcurpos()'))<cr>")

		for feature in self.features:
			if feature.isSelectable():
				vim.command(":map <buffer> <silent> <c-i><c-" + feature.__class__.__name__[0] + "> :py tab_control.selectFeature('" +  feature.__class__.__name__ + "')<cr>")

		vim.command(":map <buffer> <silent> <LeftRelease> :py tab_control.onMouseClickHandler()<cr>")

		return (vim.current.window, buf_num)

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

	def getWindowName(self, window_obj):
		if type(window_obj) == type(vim.current.window) and window_obj.valid:
			return window_obj.buffer.name
		else:
			return ''
	
	def getWorkingRoot(self):
		return self.root

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

	def toggleHelp(self):
		self.help_enabled = not self.help_enabled
		if self.selected_feature is not None:
			self.selected_feature.renderTree()

	def getHelp(self):
		result = ['Help - Selectable Features:']

		for feature in self.features:
			if feature.isSelectable():
				result.append("  <c-i><c-" + feature.__class__.__name__[0] + "> " + feature.getTitle())

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
			self.selected_feature.onMouseClick(int(pos[1]), int(pos[2]))

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

