#!/bin/python
#---------------------------------------------------------------------------------
#		  file: scmbase
#  description: This is the base class for the scm.
#
#		author: Peter Antoine
#		  date: 21/09/2013
#---------------------------------------------------------------------------------
#					  Copyright (c) 2013 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from collections import OrderedDict
from . import scm
from beorn_lib.source_tree import SourceTree


#---------------------------------------------------------------------------------
# base class (and default) SCM class
#---------------------------------------------------------------------------------
class SCM_BASE(object):
	def __init__(self, repo_url, working_dir=None, user_name=None, password=None, server_url=None):
		self.server_url = server_url

		if working_dir is not None:
			self.working_dir = os.path.abspath(working_dir)
		else:
			self.working_dir = os.path.abspath('.')

		if repo_url is None:
			self.repo_dir = self.working_dir
		else:
			self.repo_dir = os.path.abspath(repo_url)

		self.password = password
		self.user_name = user_name
		self.server_url = server_url

		self.version = ''

		self.password_function = None

	MERGE_WORKING	= 0
	MERGE_THEIRS	= 1
	MERGE_OURS		= 2

	#---------------------------------------------------------------------------------
	# Functions that query the state of the repository
	#---------------------------------------------------------------------------------
	@staticmethod
	def findAllReposInTree(path):
		""" Find all repos in tree.

			This function will return two lists, one of the repos that are found in
			the tree and the second all the sub-repos (submodules, etc...).
		"""
		return ([], [])

	@classmethod
	def getConfiguration(cls):
		result = OrderedDict()
		result['url'] = '.'
		result['working_dir'] = None

		return result

	@classmethod
	def getDialogLayout(cls):
		return None

	@classmethod
	def startLocalServer(cls, local_source_path):
		""" This function will start a local server for the SCMs that require servers.
			It will crate the server in the directory provided.
		"""
		return None

	@classmethod
	def stopLocalServer(cls):
		""" This function will stop the local server """
		return True

	#---------------------------------------------------------------------------------
	# Functions that query the state of the repository
	#---------------------------------------------------------------------------------
	def getSCMVersion(self):
		return None

	def getType(self):
		return 'NONE'

	def getUrl(self):
		return self.server_url

	def getUserName(self):
		return self.user_name

	def getPassword(self):
		return self.password

	def getRoot(self):
		return self.working_dir

	def setPasswordFunction(self, password_func):
		self.password_function = password_func

	def getPassword(self, user=None):
		if self.password_function is not None:
			self.password = self.password_function(user)
		return self.password

	def getName(self):
		if self.server_url is not None:
			return os.path.splitext(os.path.basename(self.server_url))[0]
		elif self.working_dir is not None:
			return os.path.splitext(os.path.basename(self.working_dir))[0]
		else:
			return self.getType()

	def generateFileName(self, name, branch=None):
		""" Generate File Name

			Different SCMs have different file structures that means that
			files say on branches (see SVN and P4) may not be in the same
			place. So this will work out where the files are based on the
			branch if specified or the current branch.
		"""
		return os.path.join(self.working_dir, name)

	def genrateRelativeReference(self, name, distance):
		""" Generate Relative Reference

			Different repositories have difference ways of referencing distance from
			a current reference. This function will normalise this.

			If it cannot generate the correct reference then it will return None.
		"""
		return None

	def pathInSCM(self, path):
		return path.startswith(self.working_dir)

	def hasVersion(self,version):
		return False

	def setVersion(self,version):
		return False

	def getVersion(self):
		return ''

	def getFile(self, file_name, specific_commit = None):
		return []

	def getChangeList(self, specific_commit):
		""" This function will return a change list for the specified change """
		return None

	def getPatch(self, specific_commit = None):
		return []

	def hasFileChanged(self, file_name, specific_commit = None):
		return True

	def getDirectoryListing(self,directory_name):
		return []

	def getSourceTree(self, version: str = None) -> SourceTree:
		""" This function will return the SCM contents as a SourceTree.  """
		return SourceTree(self.getName())

	def getTreeListingGenerator(self):
		""" This function will return the directory listing for the given commit.  """
		if False:
			yield None
		else:
			raise StopIteration

	def getBranch(self):
		return ''

	def getCurrentVersion(self):
		return ''

	def getHistory(self, filename=None, version=None, max_entries=None):
		return []

	def getCommitDetails(self, commit_id):
		return None

	def getCommitList(self):
		return []

	def getTreeChanges(self, from_version = None, to_version = None, path = None, check_server=False):
		return []

	def getTreeChangesGenerator(self):
		if False:
			yield None
		else:
			raise StopIteration

	def getDiffDetails(self, from_version = None, to_version = None, path = None):
		return []

	def getTreeChangeDetails(self, from_version = None, to_version = None, path = None):
		return []

	def getTags(self):
		return (-1, [])

	def getBranches(self):
		return (None, [])

	def searchCommits(self, search_string, selected_commits = []):
		return []

	def checkObjectExists(self, object_name, specific_commit = None):
		return False

	def isRepositoryClean(self):
		return False

	#---------------------------------------------------------------------------------
	# Functions that amend the state of the repository
	#---------------------------------------------------------------------------------

	def initialise(self, create_if_required=False, bare=False):
		""" Initialise the repository.

			If the repository does not exist it will be created if the create_if_required flag
			is set.
		"""
		return False

	def addBranch(self, branch_name, branch_point = None, switch_to_branch=False):
		return False

	def resetChanges(self, amend_filesystem=False):
		return False

	def addCommit(self, files = None, empty = False, message = None):
		return False

	def addItem(self, item):
		return False

	def removeItem(self, item, leave_on_filesystem=True):
		return False

	def switchBranch(self, branch=None, name=None):
		return False

	def merge(self, merge_from, merge_to = None):
		return False

	def fixConflict(self, item, how = MERGE_WORKING):
		return False

	def sync(self, pull = True, push = False):
		return False

	def cleanRepository(self, deep_clean=False):
		pass

# vim: ts=4 sw=4 noexpandtab nocin ai
