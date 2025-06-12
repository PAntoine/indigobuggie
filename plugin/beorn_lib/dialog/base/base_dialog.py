#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#
#					 ,--.
#					 |	|-.  ,---.	,---. ,--.--.,--,--,
#					 | .-. '| .-. :| .-. ||  .--'|		\
#					 | `-' |\	--.' '-' '|  |	 |	||	|
#					  `---'  `----' `---' `--'	 `--''--'
#
#	 file: base dialog.
#	 desc: This is Base class for the dialog.
#
#  author: Peter Antoine
#	 date: 11/09/2015
#---------------------------------------------------------------------------------
#					  Copyright (c) 2015 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import abc

class BaseDialog(object):
	def __init__(self):
		""" Initialise

			This function will initialise the TextDialog.
		"""
		self.elements = []
		self.element_types = {}
		# need to init the superclass
		super(BaseDialog, self).__init__()


	def initialise(self, text_layout):
			""" initialise

					This function will build the dialog from the text_layout.

					NOTE: This function should not be called from outside the init function as
					the dialog does magic and holds state, calling this will have unpredictable
					results, as frankly it is only "designed" to be called once.
			"""
			for item in text_layout:
					result = True

					if item.element in self.element_types:
							element = self.element_types[item.element].create(item.parameters)

							if element is None:
									result = False
							else:
									element.setParentDialog(self)
									self.elements.append(element)
					else:
							result = False
							break

			return result

	@abc.abstractmethod
	def resetDialog(self, defaults = False):
			""" Reset Dialog

					This function will throw away the current dialog buffer and rebuild
					it from the elements in the element list. It will fill the fields
					with the defaults (if present) in the elements. If this dialog has
					been filled before, unless the 'clean' flag is set then the previous
					values will be used where available.
			"""
			pass

	@abc.abstractmethod
	def getScreen(self, read_only = False):
			""" Refresh screen

					This function will create the list of strings that can be used to
					update the screen. It will also call the "system" update function
					so that it can then update the system screen.
			"""
			pass

	def setResult(self, values):
			""" Set result

					This function will set the result of the dialog. These are the values
					that are returned by getResult. This will keep the code consistent
					between dialog types, and will allow for the dialog to show the old
					values on next display.
			"""
			errors = []

			for index, value in values:
					error = self.elements[index].setValue(value)
					if error is not None:
							errors.append(error)

			return errors

	def getResult(self):
			""" Exit Dialog

					This function will get the values from the dialog and return them back to the caller.
			"""
			result = {}

			for element in self.elements:
					(index, value) = element.getValue()
					result[index] = value

			return result

# vim: ts=4 sw=4 noexpandtab nocin ai

