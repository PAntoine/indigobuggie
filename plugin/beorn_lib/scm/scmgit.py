#!/usr/bin/env python
#---------------------------------------------------------------------------------
#	 file: scm-git
#	 desc:
"""
	This class implements the git functions that are required for the GIT scm.
"""
#  author: Peter Antoine
#	 date: 18/07/2013
#---------------------------------------------------------------------------------
#					  Copyright (c) 2013 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import sys
from . import scm
import time
import string
from . import scmbase
import getpass
import subprocess
from collections import OrderedDict
from beorn_lib.source_tree import SourceTree
from typing import Union


def checkForType(repository):
	""" Check For Type

		This function will check to see if the repository is a git repository. It
		will not check to see if it is valid, just that the path passed in points
		to something that could be a git repository.

		This check SPECIFICALLY does not validate a submodule, that is bad juju
		and causes all sorts of problems, you should always use the root repo or
		the real repo that is used for the submodule.
	"""
	result = False

	if os.path.isdir(repository):
		real = os.path.abspath(repository)
		if real[-4:] == '.git':
			result = True
		elif os.path.isdir(os.path.join(real, '.git')):
			result = True
	else:
		if repository[-1] != '/':
			result = ('.git' == repository[-4:])

		elif '.git' == repository[-5:-2]:
			result = True

		elif repository[0:3] == 'git:':
			result = True

	return result


class SCM_GIT(scmbase.SCM_BASE):
	""" SCM_GIT class.

		This class implements the SCM functions for the git repositories.
		It handles all the basic functions that are required to read and access the
		repository.
	"""

	# private List which is the root of all git commands
	__git_root_command = ["git", "--no-pager"]

	# unlovable hack to redirect stderr to the bin
	__nul_f = open(os.devnull, 'w')

	def __init__(self, repo_url, working_dir=None, user_name=None, password=None, server_url=None):
		self.version = 'HEAD'
		super(SCM_GIT, self).__init__(repo_url, working_dir, user_name, password, server_url)

	def __callGit(self, command, git_dir = True):
		""" [PRIVATE] calls the git function and returns a tuple as the result.
			The First part of the tuple is the status of the function. Did it work
			or fail. The second is the result of the function call if it worked
			else ''.

			example:
			  (status,result) = self.__callGit([... git sub-command ...])
		"""
		try:
			if (not git_dir) or (self.working_dir is None):
				if sys.platform == 'win32':
					CREATE_NO_WINDOW = 0x08000000
					output = subprocess.check_output(SCM_GIT.__git_root_command + command, stderr=SCM_GIT.__nul_f, creationflags=CREATE_NO_WINDOW).decode()
				else:
					output = subprocess.check_output(SCM_GIT.__git_root_command + command, stderr=SCM_GIT.__nul_f).decode()

				result = True
			else:
				command_list = SCM_GIT.__git_root_command[:]

				if self.repo_dir is not None:
					command_list.append("--git-dir=" + os.path.join(self.repo_dir, '.git'))

				if self.working_dir is not None:
					command_list += ["-C", self.working_dir]

				command_list += command

				if sys.platform == 'win32':
					CREATE_NO_WINDOW = 0x08000000
					output = subprocess.check_output(command_list, stderr=SCM_GIT.__nul_f, creationflags=CREATE_NO_WINDOW).decode()
				else:
					output = subprocess.check_output(command_list, stderr=SCM_GIT.__nul_f).decode()
				result = True

		except subprocess.CalledProcessError:
			output = ''
			result = False

		return (result, output)

	#---------------------------------------------------------------------------------
	# Functions that query the state of the repository
	#---------------------------------------------------------------------------------
	@staticmethod
	def findAllReposInTree(path):
		""" Find All Repos in Tree

			This function will walk the directory tree and find all the
			repositories in the tree. It will report the submodules and
			the actual git trees. These are detectable (in two ways) but
			as we are searching the tree anyway, then look for ".git" items
			that are files as these are submodules and directories are
			full repos.

			This code is ignoring 'bare' repos - dirs that normally end
			in *.git as that is only convention and cant be relied on.
		"""
		sub_modules = []
		git_repos = []

		# search children for repos
		for root, dirs, files in os.walk(path, followlinks=True):
			if '.git' in files:
				sub_modules.append(os.path.abspath(root))

			if '.git' in dirs:
				# want any links to be relative the main repo.
				git_repos.append(os.path.abspath(root))

		# Now need to search for parent trees.
		(working_path, _) = os.path.split(os.path.abspath(path))
		while working_path != '':
			if '.git' in os.listdir(working_path):
				git_path = os.path.join(working_path, '.git')

				if os.path.isdir(git_path):
					git_repos.append(os.path.abspath(working_path))
				else:
					sub_modules.append(os.path.abspath(working_path))

			(temp, _) = os.path.split(working_path)

			if temp == working_path:
				break
			else:
				working_path = temp

		return (git_repos, sub_modules)

	@classmethod
	def getConfiguration(cls):
		result = OrderedDict()
		result['server'] = ''
		result['repo_url'] = None
		result['working_dir'] = '.'
		result['user_name'] = ''
		result['password'] = ''
		return result

	@classmethod
	def getDialogLayout(cls):
		return [('TextField', 'text', 'repo_url', "Repository Url"),
				('TextField', 'text', 'working_dir', "Working Directory")]

	#---------------------------------------------------------------------------------
	# Functions that query the state of the repository
	#---------------------------------------------------------------------------------
	def getSCMVersion(self):
		(result, output) = self.__callGit(["version"])

		if result:
			return output
		else:
			return None

	def getType(self):
		return 'Git'

	def getRoot(self):
		return self.working_dir

	def generateRelativeReference(self, name, distance):
		""" Generate Relative Reference

			Different repositories have difference ways of referencing distance from
			a current reference. This function will normalise this.

			If it cannot generate the correct reference then it will return None.
		"""
		if distance == 0:
			result = name

		elif distance < 0:
			result = name + "~" + str(abs(distance))
		else:
			result = None

		return result

	def hasVersion(self, version):
		""" Check for Version

			If this function will check to see if the repository has the specific
			required version in it.

			It return 'True', if the version exists and 'False' if it does not.
		"""
		(_, output) = self.__callGit(["rev-parse", "--quiet", "--verify", version])

		if output == "":
			return False
		else:
			return True

	def setVersion(self, version):
		""" This function will set the version.

			For the GIT_SCM this is the commit number. It will check to see if the commit
			is valid, if so it will set the version to that value. If the commit does not
			exist then then function will not change the version and it will return False.

			If the commit exists, it will set the version to the commit and it will then
			return True.
		"""
		if self.version == version:
			return True
		else:
			(result, output) = self.__callGit(["checkout", version])

			if result:
				self.version = version

		return result

	def getVersion(self):
		""" This function will return the version.

			This returns the current version that the class is set to, it is not the
			same as what the repository is currently pointing to. To get that the
			function getCurrentVersion() will return that value.
		"""
		if self.version != '':
			return self.version
		else:
			return 'HEAD'

	def normaliseFilename(self, filename):
		""" Make the filename local to the repo.

			Some of git's commands need paths that are relative to the repo and are
			in unix style path separators. This function does that.
		"""
		if filename.startswith(self.working_dir):
			result = os.path.relpath(filename, self.working_dir)
		else:
			result = filename

		return result.replace("\\", "/")

	def getFile(self, file_name, specific_commit=None):
		""" This function will return a List containing the requested file.

			This function will read the commit version. If the version is set then it will
			use that version, if that is not set then it will use the branch as the repo
			part of the name.

			If the file cannot be found/read then the function will return an empty string
			the file status should be checked before calling this function, or use the
			empty list as an indication of a problem (note: that empty files are allowed
			in git repo's).
		"""
		if specific_commit is not None:
			commit = specific_commit
		else:
			if self.version != '':
				commit = self.version
			else:
				commit = 'HEAD'

		(_, output) = self.__callGit(["cat-file", "blob",  commit + ':' + self.normaliseFilename(file_name)])

		return output.splitlines()

	def getChangeList(self, specific_commit):
		""" This function will return a change list for the specified change """
		#(result, output) = self.__callGit(["show", '-p', '--expand-tabs=0', specific_commit])
		(result, output) = self.__callGit(["show", '-p', specific_commit])

		if result:
			contents = output.splitlines()

			author = contents[1][8:]
			timestamp = int(time.mktime(time.strptime(contents[2][8:-6], "%a %b %d %H:%M:%S %Y")))

			comment = []
			for index, line in enumerate(contents[4:]):
				if line[:4] == 'diff':
					break
				else:
					# remove the leading 4 chars.
					comment.append(line[4:])

			# removed the first line of the comments if it is empty (common format for git)
			if comment[0] == '':
				comment = comment[1:]

			return scm.ChangeList(contents[0][7:], timestamp, author, comment, scm.parseUnifiedDiff(specific_commit, None, contents))
		return None

	def getPatch(self, specific_commit = None):
		""" This function will return a List containing the requested file.

			This function will read the commit version. If the version is set then it will
			use that version, if that is not set then it will use the branch as the repo
			part of the name.

			If the file cannot be found/read then the function will return an empty string
			the file status should be checked before calling this function, or use the
			empty list as an indication of a problem (note: that empty files are allowed
			in git repo's).
		"""
		if specific_commit is not None:
			commit = specific_commit
		else:
			if self.version != '':
				commit = self.version
			else:
				commit = 'HEAD'

		(_, output) = self.__callGit(["show", commit])

		return output.splitlines()

	def hasFileChanged(self, file_name, specific_commit = None):
		""" This function will test if the version of the file has changed

			This function will read the commit version. If the version is set then it will
			use that version, if that is not set then it will use the branch as the repo
			part of the name.

			If the version of the file specified is different from the file in the local
			file system then the function will return True, also if the file cannot be found
			locally or does not exist then it will also return True.

		"""
		if specific_commit != None:
			commit = specific_commit
		else:
			if self.version != '':
				commit = self.version
			else:
				commit = 'HEAD'

		(result, _) = self.__callGit(["diff", "--quiet", commit, '--', file_name])

		return not result

	def checkObjectExists(self, file_name, specific_commit = None):
		""" This function will check if an repository object exist for the current commit/version.

			This function will read the commit version. If the version is set then it will
			use that version, if that is not set then it will use the branch as the repo
			part of the name.

			If the file cannot be found/read then the function will return an empty string
			the file status should be checked before calling this function, or use the
			empty list as an indication of a problem (note: that empty files are allowed
			in git repo's).
		"""
		if specific_commit != None:
			commit = specific_commit
		else:
			if self.version != '':
				commit = self.version
			else:
				commit = 'HEAD'

		(result, _) = self.__callGit(["cat-file", "blob",  commit + ':' + file_name])

		return result

	def getDirectoryListing(self, directory_name):
		""" This function will return the directory listing for the given commit.
		"""
		if self.version != '':
			commit = self.version
		else:
			commit = 'HEAD'

		result = []

		(status, output) = self.__callGit(["ls-tree", commit, directory_name + '/', "--abbrev", "--full-tree"])

		if status:
			lines = output.splitlines()

			for line in lines:
				parts = line.split()

				# decode the file type
				if parts[1] == 'blob':
					item_type = 'file'
				elif parts[1] == 'tree':
					item_type = 'dir'
				elif parts[1] == 'commit':
					item_type = 'module'
				else:
					item_type = 'unknown'

				# add the new element to the result
				result.append(scm.SCMItem(item_type, os.path.basename(parts[3])))

		return result

	def getSourceTree(self, version: str = None) -> SourceTree:
		""" This function will return the SCM contents as a SourceTree.  """

		commit = 'HEAD'
		if version is not None:
			commit = version
		elif self.version != '':
			commit = self.version

		result = SourceTree(self.getName() + ":" + commit, self.working_dir)

		(status, output) = self.__callGit(["ls-tree", commit, self.working_dir + os.sep, "-r", "--abbrev", "--full-tree"])

		if status:
			lines = output.splitlines()

			for line in lines:
				parts = line.split()

				# add the new element to the result
				result.addTreeNodeByPath(parts[3])

			# add the untracked files a well.
			(status, output) = self.__callGit(["ls-files", "--others", "--exclude-standard"])

			if status:
				lines = output.splitlines()

				for line in lines:
					entry = result.addTreeNodeByPath(line)
					entry.setFlag('A')

				# update the changed files from the version to now.
				(status, output) = self.__callGit(['diff', '--name-status', '-r', commit])

				if status:
					lines = output.splitlines()

					for line in lines:
						bits = line.lstrip().split()
						if len(bits) >= 2:
							entry = result.findItemNode(bits[1])

							if entry is None:
								# add new status (inc. new item if it did not exist before)
								entry = result.addTreeNodeByPath(bits[1])

							if entry is not None:
								entry.setFlag(bits[0])
		return result

	def getBranch(self):
		""" This function will return the current branch """
		(_, output) = self.__callGit(["rev-parse", "--abbrev-ref", "HEAD"])
		return output.strip('\n')

	def getCurrentVersion(self):
		""" Get the current symbolic reference for the branch.

			So it will return the first of the following that exists. It will
			return the annotated tag, the current branch, or the current commit
			hash.

			If none of the above exists, then it returns the empty string.
		"""

		(status, output) = self.__callGit(["describe", "--abbrev=0"])

		if status:
			result = output

		else:
			(status, output) = self.__callGit(["rev-parse", "--abbrev-ref", "HEAD"])

			if status and output != "HEAD":
				result = output.strip('\n')

			else:
				(status, output) = self.__callGit(["rev-parse", "--short", "HEAD"])

				if status:
					result = output
				else:
					result = ''

		return result.strip()

	def getHistory(self, filename=None, version=None, max_entries=None):
		""" Get the history of the commit or the filename.

			This function will get the commit history. If the filename is given then the commit history will
			will just be the history for the current file. Else it will give the history for the full current
			branch.
		"""

		if version != None:
			commit = version
		elif self.version != '':
			commit = self.version
		else:
			commit = 'HEAD'

		result = []

		command = ["rev-list", "--timestamp", "--oneline", commit]

		if max_entries is not None:
			command.append('--max-count=' + str(max_entries))

		if filename is not None:
			command += ["--", filename]

		(status, output) = self.__callGit(command)

		if status:
			lines = output.splitlines()

			# build a tuple List of (version,description) - where version == commit hash
			for line in lines:
				parts = line.split(' ',2)
				result.append(scm.HistoryItem(parts[1], parts[2], parts[0], None, None))

		return result

	def getCommitDetails(self, commit_id) -> Union[None, scm.Details]:
		""" Get the commit details of the specific commit. """
		result = None

		(status, output) = self.__callGit(["log", "--oneline", "--pretty=\"%at %h ''%cn'' %s\"", "-1", commit_id])

		if status:
			hash_off = output.find(' ')
			name_off = output[hash_off:].find("''")
			name_off = hash_off + output[hash_off:].find("''") + 2
			subj_off = name_off + output[name_off+2:].find("''") + 2

			timestamp = output[1:hash_off]
			hash_id = output[hash_off+1:hash_off + name_off - 1]

			name = output[name_off:subj_off]
			subject = output[subj_off+3:]

			result = scm.Details(version=hash_id, summary=subject, timestamp=timestamp, author=name)

		return result

	def getCommitList(self):
		""" Get Commit List

			This function gets the WHOLE history of the repository in chronological order. It also will
			return all the parents of the given commits. This will allow for the commits to be collected
			together as a graph and the repository graph can be searched.

			This function returns a list of Commit() named tuples.
		"""
		result = []

		(status, output) = self.__callGit(['log', '--pretty=%h:%p#%s', '--all', '--reverse'])

		if status:
			lines = output.splitlines()

			for line in lines:
				parts = line.split('#')
				result.append(scm.Commit(parts[0][0:7], parts[0][8:].split(), parts[1]))

		return result

	def getTreeChanges(self, from_version = None, to_version = None, path = None, check_server=False):
		""" Get Tree Changes

			This function will return the changes between two versions.
			If no versions are given then it will return a list of changes against the current working tree.

			If to_revision is given only, then the current working tree will be diff'ed against the given
			revision.

			If from_version is not given then the repository is diff'ed from the current version, else it
			is diff'ed against the given version.

			If a path is given then the differences in the given path are returned.

			The function will return a list of the changes, as a tuple.

				([A|D|M|U] , relative repository path)

				A = file/directory added
				D = file/directory deleted
				M = file/directory modified
				U = file/directory has been changed on the server (out of date).

		"""

		new_files = []

		if to_version is None and from_version is None:
			# No versions, so simply use ls-files against the HEAD
			git_command = ['status', '--porcelain', '-u']

		elif to_version is None:
			# OK, have a from_version so we need to include the
			# local file-system and the index.
			git_command = ['diff', '--name-status', '-r', from_version, 'HEAD']

			# will need the untracked files
			(status, output) = self.__callGit(['ls-files', '-o', '--full-name'])
			new_files = output.splitlines()
		else:
			# Ok, have both from and to so we ignore the index and
			# the local file system.
			git_command = ['diff-tree', '--name-status', '-r', from_version, to_version]

		# OK, do we have a path
		if path is not None:
			git_command.extend(['--', path])

		(status, output) = self.__callGit(git_command)

		lines = output.splitlines()

		result = []

		if status:
			for line in lines:
				bits = line.lstrip().split()
				if len(bits) >= 2:
					# what sort of change are you?
					if bits[0] == 'M' or bits[0] == 'C':
						result.append(scm.SCMStatus('M', bits[1]))

					elif bits[0] == 'A' or bits[0][0] == '?':
						result.append(scm.SCMStatus('A', bits[1]))

					elif bits[0] == 'D' or bits[0] == 'R':
						result.append(scm.SCMStatus('D', bits[1]))

		for file_name in new_files:
			result.append(scm.SCMStatus('A', file_name))

		if check_server is True:
			# TODO: work out what I actually want to do here. Should it show all
			#       differences against the upstream (including locally saved commits)
			#       or only 3-party commits and there change - the divergences.
			# result += self._checkServerForChanges(from_version, to_version)
			pass

		return result

	def getDiffDetails(self, from_version = None, to_version = None, path = None):
		""" Get Diff Details

			TODO: need to fill in this documentation.

		"""
		git_command = ['diff', '--full-index', '-r', '--diff-filter=ADM', '--unified=0']

		# ok, sort out the from version
		if from_version is not None:
			git_command.append(from_version)

		# ok, sort the tp version
		if to_version is not None:
			version = to_version
		else:
			version = self.getVersion()

		git_command.append(version)

		# OK, do we have a path
		if path is not None:
			git_command.extend(['--', path])

		(_, output) = self.__callGit(git_command)

		lines = output.splitlines()

		return scm.parseUnifiedDiff(version, from_version, lines)

	def getTreeChangeDetails(self, from_version = None, to_version = None, path = None):
		""" Get Tree Changes

			This function will return the changes between two versions, by commit.
			If no versions are given then it will return a list of changes against the current working tree.

			If to_revision is given only, then the current working tree will be diff'ed against the given
			revision.

			If from_version is not given then the repository is diff'ed from the current version, else it
			is diff'ed against the given version.

			If a path is given then the differences in the given path are returned.

			The function will return a list of the changes, with a list of the details of the changes, it
			will return the start line and the number of lines affected on both sides of the change.

				([A|D|M] , relative repository path)

				A = file/directory added
				D = file/directory deleted
				M = file/directory modified

		"""
		result = []

		git_command = ['log', '--pretty=%h %p']

		# ok, sort out the from version
		if from_version is None:
			version = ''
		else:
			version = from_version + '..'

		# ok, sort the to version
		if to_version is not None:
			version += to_version
		else:
			version += self.getVersion()

		git_command.append(version)

		# OK, do we have a path
		if path is not None:
			git_command.extend(['--', path])

		# Get the list of commits between versions
		(status, output) = self.__callGit(git_command)

		if status:
			commits = output.splitlines()

			# now get the changes for each commit
			for commit_pair in commits:

				# Ignoring items with multiple parents - one is enough for doing a diff
				parts = commit_pair.split(' ', 3)
				commit = parts[0]
				parent = parts[1]

				(status, output) = self.__callGit(['show', '--unified=0', commit])

				lines = output.splitlines()

				changes = scm.parseUnifiedDiff(commit, parent, lines)

				# there were changes?
				if len(changes) > 0:
					result.append(changes)

		return result

	def getBlame(self, filename):
		""" Get the blame history for a single file.

			This function will get the list of changes on the current file and return the author and the commit
			that the change was made on. This is returned as a list of tuples.
		"""

		if self.version != '':
			commit = self.version
		else:
			commit = 'HEAD'

		# get the history either of the file or the commit/tag/branch
		(status, output) = self.__callGit(["blame", "--abbrev", commit, filename])

		result = []

		if status:
			lines = output.splitlines()

			for line in lines:
				commit_hash = line[0:8]
				rest = line[10:].split(')')
				details = rest[0].split()

				name_length = (len(details)-4)
				user_name = string.join(details[0:name_length])

				# add the commit_hash, user_name, and the current_line as a tuple to the output.
				result.append((commit_hash, user_name, rest[1]))

		return result

	def getTags(self):
		""" The function will return the tags of the current repository.

			This function returns a simple tuple of the tag details.
		"""
		(status, output) = self.__callGit(["show-ref", "--tags", "-d", "--abbrev"])

		current = -1
		result = []

		if status:
			lines = output.splitlines()

			for line in lines:
				parts = line.split()

				if parts[1][-3:] == "^{}":
					# we have the object reference - we can add that
					# also need to remove "refs/tags/" from the front of the reference
					current = len(result)
					result.append((parts[0], parts[1][10:-3]))

		return (current, result)

	def getBranches(self, remotes=True):
		""" The function will return the branches of the current repository.

			This function returns a simple tuple of the branch details.
		"""
		if remotes:
			(status, output) = self.__callGit(["branch", "-v"])
		else:
			(status, output) = self.__callGit(["branch", "-av"])

		current = -1
		result = []

		if status:
			lines = output.splitlines()

			for line in lines:
				parts = line.split()
				remote = None

				# add the branch_name, commit, branch_description to the tuple.
				if parts[0] == '*':
					current = len(result)
					branch_name = parts[1]
					commit		= parts[2]
					comment		= ' '.join(parts[3:])
				else:
					branch_name = parts[0]
					commit		= parts[1]
					comment		= ' '.join(parts[2:])

				if branch_name[0:7] == 'remotes':
					# we have a remote, decode the name
					[remote, branch_name] = branch_name[8:].split('/', 1)

				# add the new branch item to the list
				result.append(scm.Branch(commit, branch_name, comment, remote))

		return (current, result)

	def searchCommits(self, search_string, selected_commits = None):
		""" The function will return a list of files that have the strings in them.

			This function returns a simple tuple of the files that have the string in
			them. It will search the current branch for the commit, if the user has not
			specified a specific list of references that are to be searched.

			It returns a tuple of the version(commit hash), the file name, line number
			and the matching line from the file.
		"""
		if selected_commits is not None:
			commits = selected_commits

		elif self.version != '':
			commits = [self.version]
		else:
			commits = ['HEAD']

		(status, output) = self.__callGit(["grep", "-n", "-F", search_string, ''.join(commits)])

		result = []

		if status:
			lines = output.splitlines()

			for line in lines:
				parts = line.split(':')

				# add the branch_name, commit, branch_description to the tuple.
				result.append((parts[0], parts[1], parts[2], ':'.join(parts[3:])))

		return result

	def isRepositoryClean(self):
		""" is Repository Clean

			This function will check the repo is clean. All files have been committed
			and there are no local changes and that the index is up to date with the
			file system.

			If the repo passes all the tests the function will return True, else False.
		"""

		(result, _) = self.__callGit(["diff-index", "--quiet", "--cached", "HEAD"])

		if result:
			(result, _) = self.__callGit(["diff-files", "--quiet"])

			if result:
				(result, _) = self.__callGit(["diff-index", "--quiet", "HEAD"])

		return result

	#---------------------------------------------------------------------------------
	# Functions that amend the state of the repository
	#---------------------------------------------------------------------------------
	def initialise(self, create_if_required=False, bare=False):
		""" Initialise

			This function will create a git repository.
		"""
		result = True

		# path must be local, so make it readable
#		if self.url[-5:] == '/.git':
#			url = self.url[:-5]
#		else:
#			url = self.url

		if self.server_url is not None:
			# clone the repository
			try:
				# directory is in a sound place, create the repo
				(result, _) = self.__callGit(["clone", self.server_url, self.working_dir], False)

			except IOError:
				result = False

		else:
			if bare:
				# create a bare repo
				(result, _) = self.__callGit(["init", "--bare", self.working_dir], False)
			else:
				# create a normal repo
				if not os.path.exists(self.working_dir):
					os.makedirs(self.working_dir)

				if os.path.isdir(self.working_dir):
					# directory is in a sound place,  create the repo
					(result, _) = self.__callGit(["init", self.working_dir], False)

					if result:
						(result, email) = self.__callGit(["config", "--get", "user.email"])

						if email == '':
							# have to create a mock email as newer git spits it's dummy on
							# windows if there is not email set.
							mock_email = getpass.getuser() + "@gitscm.beorn"
							self.__callGit(["config", "user.email", mock_email])
							(result, email) = self.__callGit(["config", "--get", "user.email"])

						(result, _) = self.__callGit(["commit", "--allow-empty", "-m", "initial commit"])
					else:
						pass
						# TODO: log message
				else:
					pass
					# TODO: this should cause a log message.
					# print "no dir" -- else could be a submodule -- this needs to be handled.

		return result

	def addBranch(self, branch_name, branch_point = None, switch_to_branch=False):
		""" Add Branch

			This function will add a new branch and switch to the branch.

			If it cannot make the branch then it will return an error.
		"""
		result = None

		if branch_point is not None:
			if type(branch_point) == scm.Commit:
				point = branch_point.commit_id
			else:
				point = branch_point

		if self.isRepositoryClean():
			command = []

			if switch_to_branch:
				command = ["checkout", '-b', branch_name]

				if branch_point is not None:
					command.append(point)
			else:
				command = ['branch', branch_name]

				if branch_point is not None:
					command.append(point)

			(status, output) = self.__callGit(command)

			# build the commit result
			if status:
				(status, output) = self.__callGit(['log', '--pretty=%h:%p', '-1'])

				if status:
					result = scm.Branch(output[0:7], branch_name, output[8:].split(), None)

		return result

	def addCommit(self, files = None, empty = False, message = None):
		""" Add Commit

			This function will add a commit.

			If no files are given and empty is false then all the current changes within
			the working repository are committed. If empty is True and no files are specified
			then an empty commit is added to the repository.

			Else, the files that are specified are committed to the repository.

			If message is None then an empty message will be used.
		"""
		result = None

		# my son's first use of vim. :) 8 weeks old!!! FTW!!
		#m
		# end historic moment. 17:05 11.12.2013

		if message is None:
			message = 'No Message'

		elif type(message) == list:
			message = '\n'.join(message)

		if files is None or len(files) == 0:
			if empty:
				# this is an empty commit
				(status, output) = self.__callGit(["commit", '--allow-empty', '-m', message])
			else:
				# no,  then commit all the things
				(status, output) = self.__callGit(["commit", ".", "-m", message])

		else:
			# TODO: this is really wrong!!!
			# it needs to fail and not do a commit if it failed to add any of the files.

			# add all the files that need committing
			for add_file in files:
				(status, output) = self.__callGit(["add", add_file])

			(status, output) = self.__callGit(["commit", "-m", message])

		# build the commit result
		if status:
			(status, output) = self.__callGit(['log', '--pretty=%h:%p#%s', '-1'])

			if status:
				parts = output.split('#')
				result = scm.Commit(parts[0][0:7], parts[0][8:].split(), parts[1])

		return result

	def switchBranch(self, branch=None, name=None):
		""" Switch Branch

			This function will change the branch of the current working repository. It will
			also change the current version of the repo to match this if the switch worked.

			The switch is only attempted if the repo is clean.
		"""
		result = False
		use = None

		if branch != None:
			use = branch.name
		elif name != None:
			use = name

		if use != None and self.isRepositoryClean():
			(result, _) = self.__callGit(["checkout", use])

			if result:
				self.setVersion(use)

		return result

	def merge(self, merge_from, merge_to = None):
		""" Merge

			This function will merge two branches together. It expects both of the branches
			to exist. If there are conflicts on the merge then this function will fail. The
			list of conflicted files can be retrieved by call getConflictedFiles which will
			return a list of the files in conflict.

			If merge_to is not specified, then the current branch will be merged to. Else
			it will switch the the merge_to branch and then do the merge. It will leave the
			repository pointing to the merge_to branch.
		"""
		result = None
		status = False

		if merge_to is None or self.switchBranch(merge_to):
			(status, _) = self.__callGit(["merge", merge_from.name])

		if status:
			(status, output) = self.__callGit(['log', '--pretty=%h:%p#%s', '-1'])

			if status:
				parts = output.split('#')
				result = scm.Commit(parts[0][0:7], parts[0][8:].split(), parts[1])

		return result

	def fixConflict(self, item, how = scmbase.SCM_BASE.MERGE_WORKING):
		""" Fix Conflict

			This function will mark a conflict as fixed. The fix will need to be committed
			after it has been fixed.

			The conflict 'how' parameter will do the following actions:

			how			   action
			-------------  -------------------------------------------------------------
			MERGE_WORKING  The will tell the repository to use the local working version
						   of the file as the file to commit.

			MERGE_THEIRS   This will discard the local changes and use the version from
						   the upstream repository.

			MERGE_OURS	   This will use the local version from the repository before the
						   merge attempt as the version to check into the repository.
		"""
		result = False

		if how == scm.MERGE_WORKING:
			# use local working copy. Just do git add on the item
			(result, _) = self.__callGit(["add", item])

		elif how == scm.MERGE_THEIRS:
			# use the version from the merged from branch
			(result, data) = self.__callGit(["cat-file", "blob", ":3:" + item])
			if result:
				result = self.writeFile(item, data)

				if result:
					(result, _) = self.__callGit(["add", item])

		elif how == scm.MERGE_OURS:
			# use the version from our branch
			(result, data) = self.__callGit(["cat-file", "blob", ":2:" + item])
			if result:
				result = self.writeFile(item, data)

				if result:
					(result, _) = self.__callGit(["add", item])

		return result

	def sync(self, pull = True, push = True):
		""" Sync Repository

			This function will synchronise the local repository with the upstream. It will
			only update the repository to the current tracked repo. If it does not have a
			upstream branch the command will fail.

			The order of sync'ing is the upstream is king, so that the sync will pull first
			and then push. If it does not apply cleanly, i.e. no upstream rebases and that
			there is no conflicts then it will do the push. Obviously if the pull equals
			false then it will not do the push.

			The push, is a simple push without force so that the repo again should be clean.

			So, don't break the repo, be nice and this will work. Else, you will have to
			fix conflicts or rollback to make this work.
		"""
		status = False

		if pull:
			(status, _) = self.__callGit(['pull'])

		if (not pull) or (status and push):
			(status, _) = self.__callGit(['push'])

		return status

	def cleanRepository(self, deep_clean=False):
		""" Clean Repository

			This will remove all local changes. Deepclean will remove all files even those
			that have been marked as non-tracking.
		"""
		(_, _) = self.__callGit(['reset','HEAD','--hard'])

		if deep_clean:
			(_, _) = self.__callGit(['clean','-fdx'])

# Register this type with SCM.
scm.supported_scms.append(scm.SupportedSCM('Git', checkForType, SCM_GIT))

# vim: ts=4 sw=4 noexpandtab nocin ai
