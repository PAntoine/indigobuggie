#!/bin/python
#---------------------------------------------------------------------------------
#
#                    ,--.
#                    |  |-.  ,---.  ,---. ,--.--.,--,--,
#                    | .-. '| .-. :| .-. ||  .--'|      \
#                    | `-' |\   --.' '-' '|  |   |  ||  |
#                     `---'  `----' `---' `--'   `--''--'
#
#         file: project
#  description: This class defines the project.
#
#       author: Peter Antoine
#         date: 07/09/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import time
import string
from . import errors
import getpass
from base64 import b64encode, b64decode

class Project(object):
	""" Project Class """

	def __init__(self):
		""" Initialise the Project Class

			The project has the following variables.

			Temporary values:
			filename - This is the file name that is set from either when the project was
			           loaded or the last time it was saved.

			Name                  Type       Description
			---------------       ---------  ----------------------------------------------
			name                  String     The name of the project.
			description           String[]   The project description.
			start_date            Int        The unix time stamp of the start date.
			end_date              Int        The unix time stamp of the end date.
			release               String     The release name/version.
			repository            String     The URL of the repository.
			publish_repository    String     The URL that the project will be delivered to.
			owner                 String     The user name of the owner, must be known to the
			                                 project.
            users                 String[]   The list of users that are assigned to the project
			                                 this is a sub-set of the users that currently part
											 of the project.
		"""

		self.filename			= None
		self.name				= None
		self.description		= None
		self.start_date			= None
		self.end_date			= None
		self.release			= None
		self.repository			= None
		self.publish_repository	= None
		self.owner				= None
		self.users				= []

		self.is_new = False

	def create(self, project_dir=None, project_name=None, values=None):
		""" Create Project

			This class function will create a project. It is designed to be called standalone before
			the project is loaded. It will place the project file in the directory that has been
			supplied if one ids given, else it will create it in the current working directory. If
			the given directory does not exist then it will create it in the current directory.
		"""
		if project_name == None:
			project_name = '.beorn.prj'

		if project_dir is None:
			project_dir = os.path.realpath('.')

		if not os.path.isdir(project_dir):
			os.mkdir(project_dir)

		# Ok, we now how have a project.
		if values is None:
			# Initialise to sensible values
			# Local made up name is .beorn.prj if a project directory is given then
			# the file name is beorn.bpf to so not to poo in anyones local working dir.
			self.filename		= os.path.join(project_dir, project_name)
			(self.name, _)		= os.path.splitext(os.path.basename(project_dir))
			self.description	= "Project " + self.name
			self.start_date		= int(time.time())
			self.release		= '0.1.0'
			self.owner			= getpass.getuser()
			self.users			= [self.owner]
		else:
			self.filename		= values['filename']
			self.name			= values['name']
			self.description	= values['description']
			self.start_date		= values['start_date']
			self.release		= values['release']
			self.owner			= values['owner']
			self.users			= values['users']

		self.is_new = True
		return True

	def load(self, filename):
		""" Load Project

			load(filename) -> result_code

			This function will load the project. It will expect the file to exist and be
			in the correct format as produced by the Project.save() function. This will load the
			project from the given file, also it will remember the filename and will use this name
			for updating the project later.
		"""
		result = True

		# we don't want to re-initialise a user database.
		if self.filename is not None:
			result = False

		elif filename is None:
			result = False

		else:
			self.filename = filename

			try:
				# now open the project file
				with open(self.filename) as f:
					project = f.read().splitlines()

				result = self.initialise(project)

			except IOError:
				self.filename = None
				result = False

		return result

	def save(self, filename = None):
		""" Load Project

			load(filename) -> result_code

			This function will load the project. It will expect the file to exist and be
			in the correct format as produced by the Project.save() function. This will load the
			project from the given file, also it will remember the filename and will use this name
			for updating the project later.
		"""
		# check that the project is valid
		result = self.isValid()

		if result:
			if self.is_new:
				# project was created so let make sure the directory exists
				(root, _) = os.path.split(os.path.realpath(self.filename))

				if not os.path.isdir(root):
					os.makedirs(root)

			if filename is not None:
				self.filename = filename

			if self.filename is None:
				result = ERROR_NO_FILENAME_SPECIFIED

			else:
				try:
					proj_file = open(self.filename,'w')

					# write the header
					lines = [x for x in self.export()]
					proj_file.writelines(lines)

					# write the footer and close the file
					proj_file.close()

				except IOError:
					result = ERROR_FAILED_TO_WRITE_TO_FILE

		return result

	def initialise(self, project_details):
		""" Initialise Project

				Initialise(project_details[]) -> result code

			This function will initialise the project from the List of data items that have been
			read in from the place that the project has been stored. It will set up the known parameters.

			If there are any lines in the project that do not belong the project will still load and will
			ignore the extra lines. If the project is missing any of the required fields then the project
			load will fail.
		"""
		result = True
		for item in project_details:
			parts = item.rstrip().partition(" = ")

			if len(parts) != 3:
				result = False
				break
			else:
				if parts[0] == 'name':
					self.name = b64decode(parts[2]).decode()

				elif parts[0] == 'description':
					self.description = b64decode(parts[2]).decode()

				elif parts[0] == 'start_date':
					self.start_date = int(b64decode(parts[2]))

				elif parts[0] == 'source':
					self.source = b64decode(parts[2]).decode()

				elif parts[0] == 'release':
					self.release = b64decode(parts[2]).decode()

				elif parts[0] == 'owner':
					self.owner = b64decode(parts[2]).decode()

				elif parts[0] == 'users':
					self.users = b64decode(parts[2]).decode()

		return self.isValid()

	def export(self):
		""" Export Project

				export() -> List containing the project in .ini format.

			This function will generate a List that contains the project in .ini file format, while
			can be used to update the project file.
		"""
		result = []

		if self.isValid():
			result.append("name = %s\n" % b64encode(self.name.encode()).decode())
			result.append("description = %s\n" % b64encode(self.description.encode()).decode())
			result.append("start_date = %s\n" % b64encode(str(self.start_date).encode()).decode())
			result.append("release = %s\n" % b64encode(self.release.encode()).decode())
			result.append("owner = %s\n" % b64encode(self.owner.encode()).decode())

			if self.users is None:
				result.append("users = ''\n")
			else:
				result.append("users = %s\n" % b64encode(self.users.encode()).decode())

		return result

	def update(self, new_configuration):
		""" Update

			This will update the project details from a dictionary.
		"""
		if new_configuration is not None:
			for item in new_configuration:
				if item == 'filename':
					self.filename = new_configuration[item]

				elif item == 'name':
					self.name = new_configuration[item]

				elif item == 'description':
					self.description = new_configuration[item]

				elif item == 'start_date':
					self.start_date = new_configuration[item]

				elif item == 'end_date':
					self.end_date = new_configuration[item]

				elif item == 'release':
					self.release = new_configuration[item]

				elif item == 'repository':
					self.repository = new_configuration[item]

				elif item == 'publish_repository':
					self.publish_repository = new_configuration[item]

				elif item == 'owner':
					self.owner = new_configuration[item]

				elif item == 'users':
					self.users = new_configuration[item]

	def isValid(self):
		""" Is Valid

				isValid() -> result code

			This function will simply validate the project.
		"""
		if 	self.name is None or \
			self.description is None or \
			self.start_date is None or \
			self.release is None or \
			self.owner is None or \
			self.users == []:

			result = False
		else:
			result = True

		return result

	def getValue(self, value):
		""" Get Value

			This function will return the named value from the project
			details.
		"""
		if value == 'filename':
			return self.filename

		elif value == 'name':
			return self.name

		elif value == 'description':
			return self.description

		elif value == 'start_date':
			return self.start_date

		elif value == 'end_date':
			return self.end_date

		elif value == 'release':
			return self.release

		elif value == 'repository':
			return self.repository

		elif value == 'publish_repository':
			return self.publish_repository

		elif value == 'owner':
			return self.owner

		elif value == 'users':
			return self.users

# vim: ts=4 sw=4 noexpandtab nocin ai

