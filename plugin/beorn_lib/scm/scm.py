#!/usr/bin/env python
#---------------------------------------------------------------------------------
#    file: scm
#    desc:
#
#  author: Peter Antoine
#    date: 18/07/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from . import scmbase
from collections import namedtuple as namedtuple

#---------------------------------------------------------------------------------
# Module Named Tuples
#---------------------------------------------------------------------------------
Commit		= namedtuple('Commit', ['commit_id', 'parents', 'description'])
Branch		= namedtuple('Branch', ['commit_id', 'name', 'parents', 'remote'])
Tag			= namedtuple('Tag', ['commit_id', 'name'])
Details		= namedtuple('Details', ['version', 'summary', 'timestamp', 'author'])
Change		= namedtuple('Change', ['original_line', 'original_length', 'new_line', 'new_length', 'lines'])
HistoryItem	= namedtuple('HistoryItem', ['version', 'summary', 'timestamp', 'parents', 'children'])
ChangeList	= namedtuple('ChangeList', ['commit_id', 'timestamp', 'author', 'description', 'changes'])
ChangeItem	= namedtuple('ChangeItem', ['version', 'parent', 'change_type', 'original_file', 'new_file', 'change_list'])
SCMItem		= namedtuple('SCMItem', ['type', 'name'])
SCMStatus	= namedtuple('SCMStatus', ['status', 'path'])
SCMFound	= namedtuple('SCMFound', ['type', 'primary', 'sub'])
SupportedSCM = namedtuple('SupportedSCM', ['type', 'check_function', 'cls'])

#---------------------------------------------------------------------------------
# Module Constants.
#---------------------------------------------------------------------------------
MERGE_WORKING	= scmbase.SCM_BASE.MERGE_WORKING
MERGE_THEIRS	= scmbase.SCM_BASE.MERGE_THEIRS
MERGE_OURS		= scmbase.SCM_BASE.MERGE_OURS

SOURCE_STATUS_ADDED		= 1
SOURCE_STATUS_MODIFIED	= 2
SOURCE_STATUS_DELETED	= 3

#---------------------------------------------------------------------------------
# Supported SCM List.
#
# This list is designed to be amended when an scm is imported. This will allow
# for selective support of SCMs.
#---------------------------------------------------------------------------------
supported_scms = []

#---------------------------------------------------------------------------------
# Module functions.
#---------------------------------------------------------------------------------
def new(repository, remote_url=None):
	""" Create New SCM container.

		This function will detect what type of SCM is being created and then
		instantiate the correct one. If the correct one is not supported it will
		instantiate the default and base SCM.
	"""
	result = None

	repo_type = isRepository(repository)
	repo_url = repository

	if repo_type is None:
		(repo_type, repo_url) = findRepositoryRoot(repository)

	if repo_type is not None:
		result = create(repo_type, remote_url, repo_url)

	return result

def findRepositories(wanted=None):
	""" Find all the repositories in the sub tree """
	result = []

	for scm in supported_scms:
		if wanted is None or scm.type in wanted:
			(main, sub) = scm.cls.findAllReposInTree('.')
			result.append(SCMFound(scm.type, main, sub))

	return result

def create(repo_type, repository_url=None, working_dir=None, user_name=None, password=None, server_url=None):
	""" create_scm

		This is a generic access function that will create the create type of
		SCM interface.SCM
	"""
	result = None

	for scm in supported_scms:
		if repo_type == scm.type:
			result = scm.cls(repository_url, working_dir, user_name, password, server_url=server_url)
			break
	else:
		result = scmbase.SCM_BASE(working_dir, repository_url)

	return result

def startLocalServer(repo_type, working_dir = None):
	""" create_scm

		This is a generic access function that will create the create type of
		SCM interface.
	"""
	result = None

	for scm in supported_scms:
		if repo_type == scm.type:
			result = scm.cls.startLocalServer(working_dir)
			break

	return result

def stopLocalServer(repo_type):
	""" stop local server """
	result = None

	for scm in supported_scms:
		if repo_type == scm.type:
			result = scm.cls.stopLocalServer()
			break

	return result

def getSupportedSCMs():
	""" return a list of the supported SCM types """
	return supported_scms

def isRepository(repository_url):
	result = None

	for scm in supported_scms:
		if scm.check_function(repository_url):
			return scm.type

	return result

def findRepositoryRoot(repository = None):
	""" Find Repository Root

		This function will search from the current directory, to the root until
		the root is reached.
	"""
	# use the current directory if none is given
	if repository is None:
		repository = os.path.abspath('.')
	else:
		repository = os.path.abspath(repository)

	old_path = ''
	repo_type = None

	while old_path != repository:
		# new check all the supported scms
		repo_type = isRepository(repository)
		if repo_type is not None:
			break
		else:
			old_path = repository
			repository = os.path.dirname(repository)
	else:
		# did not find the repository
		repository = None

	return (repo_type, repository)

def createChangeHunk(change, lines = None):
	""" Create Change Hunk

		This function will create the change hunk.
	"""
	change_range = change.split()
	# get the original line details
	temp = change_range[1].split(',', 3)
	original_line = int(temp[0][1:])

	if len(temp) < 2:
		original_length = 1
	else:
		original_length = int(temp[1])

	# get the change line details
	temp = change_range[2].split(',', 3)
	new_line = int(temp[0][1:])

	if len(temp) < 2:
		new_length = 1
	else:
		new_length = int(temp[1])

	return Change(original_line, original_length, new_line, new_length, lines)


def parseUnifiedDiff(version, parent_version, diff_array):
	""" Parse Unified Diff

		This function will take a list of the contents of the diff and then
		generate a list of ChangeItems with the original and new file.
	"""
	in_diff = False
	found = False
	looking_for_first_diff = False
	in_diff = False
	result = []
	lines = None
	start_line = None
	original_file = None
	change_list = []
	new_file = None

	for change in diff_array:
		if change[0:4] == 'diff':
			if found:
				change_list.append(createChangeHunk(start_line, lines))

				if original_file is not None and new_file is not None:
					change_type = 'M'

				elif original_file is None:
					change_type = 'A'

				else:
					change_type = 'D'

				result.append(ChangeItem(version, parent_version, change_type, original_file, new_file, change_list))

			new_file = None
			original_file = None
			change_type = 'U'
			change_list = []
			looking_for_first_diff = True
			in_diff = False
			found = True
			lines = None

		elif looking_for_first_diff:
			if change[0:3] == '---':
				# found the original file
				if change[4:] != '/dev/null':
					original_file = change[6:]

			elif change[0:3] == '+++':
				# found the new file
				if change[4:] != '/dev/null':
					new_file = change[6:]

			elif change[0:2] == '@@':
				lines = []
				start_line = change
				looking_for_first_diff = False
				in_diff = True

			elif change[0:12] == 'Binary files':
				# Ok, one side of the diff is a binary file, let's get the names
				parts = change[13:-7].split(' and ')

				if parts[0] != '/dev/null':
					original_file = parts[0]

				if parts[1] != '/dev/null':
					new_file = parts[1]

		elif change[0:2] == '@@':
			if in_diff:
				# Ok, the file has more than 1 change in it.
				change_list.append(createChangeHunk(start_line, lines))
				lines = []

			start_line = change

		else:
			if in_diff:
				if lines is None:
					lines = [change]
				else:
					lines.append(change)

	# catch the last diff
	if found:
		if in_diff:
			change_list.append(createChangeHunk(start_line, lines))

		if original_file is not None and new_file is not None:
			change_type = 'M'

		elif original_file is None:
			change_type = 'A'

		else:
			change_type = 'D'

		result.append(ChangeItem(version, parent_version, change_type, original_file, new_file, change_list))

	return result

# vim: ts=4 sw=4 noexpandtab nocin ai
