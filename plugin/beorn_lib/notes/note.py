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
#    file: note
#    desc: This holds the note.
#
#  author: peter
#    date: 23/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
import binascii
from beorn_lib.nested_tree import NestedTreeNode

#---------------------------------------------------------------------------------
# class definition
#---------------------------------------------------------------------------------
class Note(NestedTreeNode):
	""" Note class """

	#---------------------------------------------------------------------------------
	# class Methods
	#---------------------------------------------------------------------------------
	@classmethod
	def load(cls, file_string):
		""" Load

			This function will import the note from a string of the same format as
			exported.
		"""
		result = None

		parts = file_string.rstrip().partition(" = ")

		if len(parts) == 3:
			bits = parts[2].split(':')

			if len(bits) >= 3:
				title = parts[0]
				date  = int(bits[0])
				checksum = int(bits[1])
				message = ':'.join(bits[2:])

				result = cls(title, message, date, checksum)

		return result

	#---------------------------------------------------------------------------------
	# Instance Methods
	#---------------------------------------------------------------------------------
	def __init__(self, name = '', message = '', date = 0, checksum = 0, subject = None):
		super(Note, self).__init__(name, None)

		self.name		= name			# the name of the note
		self.message	= message		# the notes body
		self.versions	= []			# are the alternative versions of the message
		self.subject	= subject
		self.amended	= False

		if date == 0:
			self.date = int(time.time())
		else:
			self.date = date

		if type(message) == list:
			self.message = '\x03'.join(message)

		# set the checksum
		self.checksum = binascii.crc32(bytes(name, "utf-8")) & 0xffffffff
		self.checksum = binascii.crc32(bytes(self.message, "utf-8"), self.checksum) & 0xffffffff

	def amendMessage(self, message):
		if type(message) == list:
			self.message = '\x03'.join(message)
		else:
			self.message = message

	def getMessage(self):
		return self.message.split('\x03')

	def append(self, message):
		if type(message) == list:
			self.message += '\x03' + '\x03'.join(message)
		else:
			self.message += '\x03' + message

	def export(self):
		""" Export

			This function will export the note in a format that can be saved to file.
		"""
		return "%s = %d:%d:%s\n" % (self.name, self.date, self.checksum, self.message)

# vim: ts=4 sw=4 noexpandtab nocin ai
