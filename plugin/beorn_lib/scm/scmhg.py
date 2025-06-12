#!/usr/bin/env python
#---------------------------------------------------------------------------------
#    file: scmhg
#    desc: This file implements the Mercurial version of the SCM.
#
#  author: Peter Antoine
#    date: 18/07/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from . import scm
import string
from . import scmbase
import subprocess

def checkForType(repository):
	""" Check For Type

		This function will check to see if the repository is a hg repository. It
		will not check to see if it is valid, just that the path passed in points
		to something that could be a hg repository.
	"""
	result = False

	if (repository[0] == '/' or repository[0] == '\\' or repository[0] == '.' or repository[0] == '~'):
		real = os.path.abspath(repository)

	elif os.path.isdir(os.path.join(repository, '.hg')):
			result = True
	else:
		if repository[0:3] == 'ssh:':
		 	# starts with SSH so could be Mercurial
		 	result = True

		elif repository[0:5] == 'https:':
			# Again starts with https so could be...
			result = True

	return result


class SCM_HG(scmbase.SCM_BASE):
	""" SCM_HG class.

		This class implements the SCM functions for the Mercurial repositories.
		It handles all the basic functions that are required to read and access the
		repository.
	"""
	def __callHG(self, command, git_dir = True):
		""" [PRIVATE] calls the hg function and returns a tuple as the result.
			The First part of the tuple is the status of the function. Did it work
			or fail. The second is the result of the function call if it worked
			else ''.

			example:
			  (status,result) = self.__callHG([... hg sub-command ...])
		"""
		try:
			if (not git_dir) or (self.url is None):
				output = subprocess.check_output(SCM_GIT.__git_root_command + command, stderr=SCM_GIT.__nul_f)
				result = True
			else:
				if self.working_dir is None:
					output = subprocess.check_output(SCM_GIT.__git_root_command + ["--repository=" + self.url] + command, stderr=SCM_GIT.__nul_f)
				else:
					output = subprocess.check_output(SCM_GIT.__git_root_command + ["--repository=" + self.working_dir] + command, stderr=SCM_GIT.__nul_f)
				result = True

		except subprocess.CalledProcessError as e:
			output = ''
			result = False

		return (result, output)


	def getSCMVersion(self):
		return None

	def getType(self):
		return 'NONE'

	def getUrl(self):
		return self.url

	def getRoot(self):
		return self.url

	def genrateRelativeReference(self, name, distance):
		""" Generate Relative Reference

			Different repositories have difference ways of referencing distance from
			a current reference. This function will normalise this.

			If it cannot generate the correct reference then it will return None.
		"""
		return None

	def hasVersion(self,version):
		return False

	def setVersion(self,version):
		return False

	def getVersion(self):
		return ''

	def getFile(self, file_name, specific_commit = None):
		return []

	def hasFileChanged(self, file_name, specific_commit = None):
		return True

	def getDirectoryListing(self,directory_name):
		return []

	def getBranch(self):
		return ''

	def getCurrentVersion(self):
		return ''

	def getHistory(self, filename = None, version = None):
		return []

	def getCommitList(self):
		return []

	def getTreeChanges(self, from_version = None, to_version = None, path = None, check_server=False):
		return []

	def getDiffDetails(self, from_version = None, to_version = None, path = None):
		return []

	def getTreeChangeDetails(self, from_version = None, to_version = None, path = None):
		return []

	def getTags(self):
		return []

	def getBranches(self):
		return []

	def searchCommits(self, search_string, selected_commits = []):
		return []

	def checkObjectExists(self, object_name, specific_commit = None):
		return False

	def isRepositoryClean(self):
		return False

	#---------------------------------------------------------------------------------
	# Functions that amend the state of the repository
	#---------------------------------------------------------------------------------

	def initialise(self, directory_path = None, bare = False):
		return False

	def addBranch(self, branch_name, branch_point = None):
		return False

	def addCommit(self, files = None, empty = False, message = None):
		return False

	def switchBranch(self, branch_name):
		return False

	def merge(self, merge_from, merge_to = None):
		return False

	def fixConflict(self, item, how = scmbase.SCM_BASE.MERGE_WORKING):
		return False

	def sync(self, pull = True, push = False):
		return False

scm.supported_scms.append(scm.SupportedSCM('hg', checkForType, SCM_HG))

