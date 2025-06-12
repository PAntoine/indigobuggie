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
#    file: notes
#    desc: The notes functionality.
#
#  author: peter
#    date: 21/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import getpass
import platform
from .note import Note
from .subject import Subject
from beorn_lib.nested_tree import NestedTreeNode

#---------------------------------------------------------------------------------
# class definition
#---------------------------------------------------------------------------------
class Notes(NestedTreeNode):
	""" Notes class """

	def __init__(self, name, directory):
		super(Notes, self).__init__(name, None)
		self.name				= " - Empty No Notes - "
		self.current_user		= getpass.getuser()
		self.current_machine	= platform.node()
		self.current_id			= self.current_user + '@' + self.current_machine
		self.directory			= directory

	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str:
			find_name = other
		elif isinstance(other, Subject):
			find_name = other.name
		else:
			return False

		for child in self.getChildren():
			if find_name == child.name:
				return True
		else:
			return False

	def load(self):
		""" Load

			The function will load the notes from the given directory. It expects the
			notes to be in that directory. It will load all the files for the given
			user. The format of the file name determines the user and machine that the
			notes are from, the format of the file is:
		"""
		files = os.listdir(self.directory)
		remove_list = []

		# load the note files
		for note_file in files:
			bits = note_file.split('@')

			if bits[0] == self.current_user:
				if bits[1] == self.current_machine:
					# we have a file that belongs to the current user and current machine.
					file_name = os.path.join(self.directory, note_file)
					self.loadFile(file_name)

					# remove the note file from the list
					remove_list.append(note_file)
					break
			else:
				# does not belong to the current user - not interested
				remove_list.append(note_file)

		# now remove the files we don't want to merge
		for r in remove_list:
			files.remove(r)

		# now compare the others against the current file
		for note_file in files:
			file_name = os.path.join(self.directory, note_file )
			self.mergeFile(file_name)

		return True

	def save(self):
		""" Save Note File

			This methods will save the note list to file. It will enumerate the Subjects and
			save all the notes within the subjects to file.
		"""
		file_name = os.path.join(self.directory , self.current_user + '@' + self.current_machine)

		try:
			out_file = open(file_name,'w')

			for subject in self.getChildren():
				data = "[%s]\n" % subject.name
				out_file.write(data)

				for note in subject.getChildren():
					out_file.write(note.export())

			out_file.close()
			result = True

		except IOError:
			result = False

		return result

	def loadFile(self, note_file):
		""" Load File

			This function will load a file and add it to the current note file. It will add
			all subjects that are found, load all notes that don't exist in the current note
			and finally if the note exists and has been changed, will add the alternate note
			to the note list.
		"""
		result = {}
		current_subject = None
		machine = note_file.split('@', 1)[1]

		try:
			in_file = open(note_file,'r')

			for line_a in in_file:
				line = line_a.strip()

				if line[0:1] == '[' and line[-1] == ']':
					self.addSubject(line[1:-1])
					current_subject = self.getSubject(line[1:-1])

				elif current_subject is not None:
					new_note = Note.load(line)

					if new_note is not None:
						current_subject.addChildNode(new_note)

			result = True
			in_file.close()

		except IOError:
			result = False

		return result

	def mergeFile(self, note_file):
		pass

	def hasSubject(self, subject_name):
		""" return true if the subject is in the notes list """
		return subject_name in self

	def addSubject(self, subject_name):
		""" Add a new notes subject.
			If the note exists the it will return that.
		"""
		result = None

		for child in self.getChildren():
			if subject_name == child.name:
				return child

		result = self.addChildNode(Subject(subject_name))
		return result

	def getSubject(self, subject_name):
		""" Return the subject if it exists """
		for child in self.getChildren():
			if subject_name == child.name:
				return child
		else:
			return None

	def removeSubject(self, subject_name):
		""" remove the subject if it exists """
		for child in self.getChildren():
			if subject_name == child.name:
				child.deleteNode(True)

	def listSubjects(self):
		""" list the names of all the subjects in notes list """
		result = []

		for child in self.getChildren():
			result.append(child.name)

		return result

	def hasNote(self, subject, title):
		""" returns true in note is in subject """
		result = False

		for child in self.getChildren():
			if subject == child.name:
				result = title in child
				break

		return result

	def addNote(self, subject_name, title, message):
		""" will add a note if it does not already exist and return the note """
		result = None
		subject = None

		if title.find('=') == -1:
			if type(subject_name) == Subject:
				if title not in subject_name:
					result = Note(title, message)
					subject_name.addChildNode(result)
				else:
					result = subject_name.getNote(title)

			else:
				for child in self.getChildren():
					if subject_name == child.name:
						subject = child
						break

				if subject is None:
					subject = Subject(subject_name)
					self.addChildNode(subject)

				if title not in subject:
					result = Note(title, message)
					subject.addChildNode(result)

		return result

	def getNote(self, subject, title):
		""" returns node if it exists, else returns None """
		result = None

		for child in self.getChildren():
			if subject == child.name:
				for note in child.getChildren():
					if title == note.name:
						result = note
						break
				break

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
