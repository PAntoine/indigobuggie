#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#
#                    ,--.
#                    |  |-.  , ---. ,---. ,--.--.,--,--,
#                    | .-. '| .-. :| .-. ||  .--'|      \
#                    | `-' |\   --.' '-' '|  |   |  ||  |
#                     `---'  `----' `---' `--'   `--''--'
#
#    file: scmp4
#    desc: P4 SCM Integration.
#
#       This brings P4 trees into the beorn echo-system.
#       It does not use P4Python only because it want to reduce the external
#       dependencies and most of the API I require is available from the
#       command line functions. There maybe a performance hit, but P4 is soooo
#       sloooooowww it is a drop in the bucket and the dependency issue is
#       more important.
#
#  author: Peter Antoine
#    date: 05/01/2014
#---------------------------------------------------------------------------------
#                     Copyright (c) 2014 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from . import scm
import sys
import time
import datetime
import getpass
from . import scmbase
import marshal
import subprocess
import multiprocessing

from beorn_lib.utilities import Utilities
from collections import OrderedDict

#---------------------------------------------------------------------------------
# Local Classes
#---------------------------------------------------------------------------------
class DecodeState(object):
	__slots__ = ('change_list', 'client', 'current_file', 'result', 'lines', 'files', 'in_hunk', 'start_line', 'start_len', 'end_line', 'end_len')

	def __init__(self):
		self.result = []
		self.lines = []
		self.files = []
		self.change_list = []
		self.in_hunk = False
		self.current_file = None
		self.start_line = 0
		self.start_len  = 0
		self.end_line = 0
		self.end_len  = 0
		self.client = None

class ClientDetails(object):
    def __init__(self):
        self.update = None
        self.access = None
        self.owner  = None
        self.host   = None
        self.root   = None
        self.options = None
        self.line_end = None
        self.submit_options = None

        self.view = []
        self.description = ''

#---------------------------------------------------------------------------------
# Global Functions
#---------------------------------------------------------------------------------
def checkForType(repository, password_function=None):
	""" Check For Type

		Ok, Perforce is not like any common SCM, you can't see by the repo tree
		if it is a perforce directory (no .svn, .git, .CVS, etc...) you have to
		talk to the P4 server get the list of "workspaces/clients" and then see
		if the directory is one of those.
	"""
	result = False
	logged_on = False

	path = os.path.abspath(repository)

	if os.path.exists(path):
		if SCM_P4.p4IsLoggedIn():
			logged_on = True

		elif password_function is not None:
			retries = 0

			while retries < 3 and not logged_on:
				password = password_function()

				logged_on = SCM_P4.p4Login(getpass.getpass(), password) is not None
				retries += 1

		if logged_on:
			client_list = SCM_P4.p4GetClientList()

			for client in client_list:
				if os.path.abspath(client[1]) == path:
					result = True
					break

	return result

CREATE_NO_WINDOW = 0x08000000

def serverProcess(local_source_path):
	if not os.path.exists(local_source_path):
		os.makedirs(local_source_path)

	if sys.platform == 'win32':
		subprocess.check_output(['p4d', '-d', '-r', local_source_path], stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
	else:
		subprocess.check_output(['p4d', '-d', '-r', local_source_path], stderr=subprocess.STDOUT)

#---------------------------------------------------------------------------------
# base class (and default) SCM class
#---------------------------------------------------------------------------------


class SCM_P4(scmbase.SCM_BASE):
	server_process = None

	#---------------------------------------------------------------------------------
	# Class Functions.
	#---------------------------------------------------------------------------------
	@classmethod
	def startLocalServer(cls, local_source_path):
		""" This function will start a local server for the SCMs that require srvers.
			It will crate the server in the directory provided.
		"""
		if cls.server_process is not None:
			if cls.server_process.is_alive():
				cls.server_process.terminate()
				cls.server_process.join(10)

		cls.server_process = multiprocessing.Process(target=serverProcess, args=(local_source_path,))
		cls.server_process.start()

		# wait for upto 30 seconds for the server to start
		counter = 0
		while counter < 30 and 0 != subprocess.call(['p4','info']):
			print("waiting for server to start...")
			counter += 1
			time.sleep(1)

		# default P4 server path
		return 'localhost:1666'

	@classmethod
	def stopLocalServer(cls):
		""" This function will stop the local server """
		subprocess.call(['p4','admin','stop'])

		counter = 0
		while counter < 30 and 0 == subprocess.call(['p4','info']):
			print("waiting for server to start...")
			counter += 1
			time.sleep(1)

		return True

	@classmethod
	def p4Command(cls, command_list):
		""" This is the CLS version that is needed outside the rest of the code
			there is a similar version that is used in the class.
		"""
		logged_in = cls.p4IsLoggedIn()

		if logged_in:
			try:
				if sys.platform == 'win32':
					return subprocess.check_output(['p4'] + command_list, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
				else:
					return subprocess.check_output(['p4'] + command_list, stderr=subprocess.STDOUT)

			except subprocess.CalledProcessError as e:
				return None
		else:
			# TODO: log this "not logged in"
			return None

	@classmethod
	def p4IsLoggedIn(cls):
		""" Test if we are logged in """
		try:
			if sys.platform == 'win32':
				subprocess.check_output(['p4', 'login', '-s'], stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
			else:
				subprocess.check_output(['p4', 'login', '-s'], stderr=subprocess.STDOUT)

			return True
		except subprocess.CalledProcessError as e:
			return False
		except OSError:
			# P4 is not installed
			return False

	@classmethod
	def p4Login(cls, user_name, password):
		""" P4 Login

			Login to P4 and return an access key. The access key is required for
			applications that are connected to P4. For example "swarm".
		"""
		result = None

		# TODO: need to call password function if password is None and user_name is not.
		if user_name is not None and password is not None:
			try:
				if sys.platform == 'win32':
					proc = subprocess.Popen(['p4', 'login', '-pa'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
				else:
					proc = subprocess.Popen(['p4', 'login', '-pa'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

				value = proc.communicate(input=password.encode())

				if proc.returncode == 0:
					if value[0] == "'login' not necessary, no password set for this user.":
						result = ''
					else:
						lines = value[0].splitlines()

						if len(lines) > 1:
							result = value[0].splitlines()[1].strip()
						else:
							result = ''

			except subprocess.CalledProcessError as e:
				return None
			except OSError:
				# P4 is not installed
				return None

		return result

	@classmethod
	def p4GetClientList(cls):
		""" Get Client List

			This function will return the list of Clients for the current
			user. You can't get a list of other users clients without
			admin privileges.
		"""
		result = []

		if 'P4USER' in os.environ:
			clients = SCM_P4.p4Command(['clients', '-u', os.environ['P4USER']])
		else:
			clients = SCM_P4.p4Command(['clients', '-u', getpass.getuser()])

		if clients is None:
			clients = SCM_P4.p4Command(['clients'])

		if clients is not None:
			for client in clients.split('\n'):
				bit = client.split(' ', 5)

				if len(bit) > 4 and not bit[1].startswith('swarm'):
					# I have so much hate for P4 - it sometimes returns windows paths with a lowercase c:
					# and sometimes upper. It's because it returns what is set in the client and that
					# can be anything.
					name = bit[4][0].upper() + bit[4][1:]
					result.append((bit[1], name))

		return result

	@staticmethod
	def findAllReposInTree(path):
		""" Find All Repos in Tree

			This is P4, so we are looking for workspaces in this case.
			So we want to find the workspaces that are in this tree. But
			for the first go we will only find the lowest root workspace.
		"""
		p4_repos = []

		clients = SCM_P4.p4GetClientList()
		real_path = os.path.abspath(path)

		for client in clients:
			# Paths can be complicated - pwd() and abspath(pwd()) can return different strings.
			client_path = os.path.abspath(client[1])
			if real_path == client_path or Utilities.isChildDirectory(real_path, client_path):
				p4_repos.append(client[1])

		return (p4_repos, [])

	#---------------------------------------------------------------------------------
	# Structural functions.
	#---------------------------------------------------------------------------------
	def __init__(self, repo_url=None, working_dir=None, user_name=None, password=None, server_url=None):
		""" Init the P4 SCM Object.

			repo_url	is the server and port number for the perforce server.
			working_dir	This should be the workspace directory that is to be
						used. If this is None and the P4CLIENT is used then we
						will set the working directory to the path of that.
		"""
		super(SCM_P4, self).__init__(repo_url, working_dir, user_name, password, server_url)

		self.version = ''
		self.branch = 'HEAD'
		self.environ = os.environ.copy()
		self.clients = {}
		self.logged_in = True			# HACK: TODO: remove!!!!
		self.quick_updates = False		# "quick" and "p4" should not really be used.
		self.current_client = None
		self.current_branch = None

		# Ok, lets see if the caller has set up the P4 environment variables so
		# we will use those as the defaults.
		if self.user_name is None or self.user_name == '':
			if "P4USER" in os.environ:
				self.user_name = os.environ["P4USER"]
			else:
				self.user_name = ''

		if self.password is None:
			self.password = ''

		if len(self.clients) == 0:
			self.__getClientList()

		if self.working_dir is None:
			if "P4CLIENT" in os.environ:

				if os.environ["P4CLIENT"] in self.clients:
					self.current_client = self.clients[os.environ["P4CLIENT"]]
				else:
					# I F**king hate exceptions. I need to re-write this to
					# fail if this does not exist. Means writing a __new__
					# function to be able to return NULL if this does not
					# happen. Or better have an connect() function to be
					# able to this without problems anything but exceptions.
					raise Exception("I can't write code and you don't have that client")

				self.working_dir = self.getClientDirectory(self.current_client.name)
			else:
				self.working_dir = os.path.abspath(".")
				self.current_client = self.getClientFromDirectory(self.working_dir)

				if self.current_client is not None:
					self.environ['P4CLIENT'] = self.current_client.name
		else:
			self.current_client = self.getClientFromDirectory(working_dir)
			self.working_dir = working_dir

			if self.current_client is not None:
				self.environ['P4CLIENT'] = self.current_client.name

	@classmethod
	def getConfiguration(cls):
		result = OrderedDict()
		result['server'] = ''
		result['user_name'] = ''
		result['password'] = ''
		result['start_server'] = False
		return result

	@classmethod
	def getDialogLayout(cls):
		button_list = [	('start_server', 'Start a local server') ]

		return [('TextField', 'text', 'server', "Server URL and Port ($P4PORT)"),
				('TextField', 'text', 'user_name', "User Name"),
				('TextField', 'secret', 'password', "The users password"),
				('ButtonList', 'multiple', 'options', "Options", button_list)]

	#---------------------------------------------------------------------------------
	# Functions that query the state of the repository
	#---------------------------------------------------------------------------------
	def p4CommandDiff(self, command_list):
		""" P4 how I hate you.

			It does not add the diff contents as manifest objects but dumps the
			diff content raw in the output stream. Sooooo, I have to decode the
			marshal object.

			So need to get the whole output string (who gives a monkey about all
			the memory that is used, meh!) then search for the NEXT string 's{'
			as this is the start of the  marshal object, parse that, see if the
			text item is followed by a "s{" or something else.

			It does not help that the marshal code gives no information on how
			far though the string it has got, or how much data it parsed so the
			following stupidness will occur.

			I apologise (for this stupidness and not the rest of the code base as
			that is just how I roll. :))

			I am old and the painters algorithm is a thing. But luckily processors
			are faster than they used to be so we can throw away all those cycles
			for reasons.
		"""
		try:
			if sys.platform == 'win32':
				return subprocess.check_output(['p4', '-d', self.working_dir, '-G'] + command_list, env=self.environ, creationflags=CREATE_NO_WINDOW)
			else:
				return subprocess.check_output(['p4', '-d', self.working_dir, '-G'] + command_list, env=self.environ)

		except subprocess.CalledProcessError as e:
			result = []

			if e.output[0] == '{':
				# Ok, we have an object.
				start_pos = 1

				while start_pos < len(e.output):
					obj = marshal.loads(e.output[start_pos-1:])

					# Ok, we have a valid object lest find the next one so we
					# can use it to cut out the text that is there for the diff
					# content.
					pos = e.output[start_pos:].find('{s')

					if obj['code'] == 'stat':
						if e.output[start_pos:][pos-1] != '0':
							# Ok, we have a dump following after the marshalled
							# object. So lets read that data from the file.
							start = e.output[start_pos:].find('text0')
							diff_content = ['diff a b']

							for line in e.output[start_pos+start+5:start_pos+pos].splitlines():
								diff_content.append(line)

							diff = scm.parseUnifiedDiff(obj['rev'], '',  diff_content)

							if diff is not None:
								result.append(diff)

					if pos == -1:
						break
					else:
						start_pos = start_pos + pos + 1

			return result

	def __p4Login(self):
		result = SCM_P4.p4IsLoggedIn()

		if not result:
			if self.password is None or self.password == '':
				self.password = self.getPassword(self.user_name)

		return result or SCM_P4.p4Login(self.user_name, self.password) is not None

	def getUserKey(self, user_name):
		if self.password is None or self.password == '':
			self.password = self.getPassword(user_name)

		return SCM_P4.p4Login(user_name, self.password)

	def buildCommand(self, use_client, marshalled=False):
		if marshalled:
			result = ['p4', '-G']
		else:
			result = ['p4']

		if self.working_dir is not None:
			result += ['-d', self.working_dir]

		if use_client and self.current_client is not None:
			result += ['-c', self.current_client.name]

		if self.server_url is not None and self.server_url != '':
			result += ['-p', self.server_url]

		if self.user_name is not None and self.user_name != '':
			result += ['-u', self.user_name]

		if self.password is not None and self.password != '':
			result += ['-P', self.password]

		return result

	def __p4Command(self, command_list, use_client=True):
		""" This is the CLS version that is needed outside the rest of the code
			there is a similar version that is used in the class.
		"""
		if self.__p4Login():
			try:
				if sys.platform == 'win32':
					return subprocess.check_output(self.buildCommand(use_client) + command_list, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
				else:
					return subprocess.check_output(self.buildCommand(use_client) + command_list, stderr=subprocess.STDOUT)

			except subprocess.CalledProcessError as e:
				return None
		else:
			# TODO: Add logging - print "not logged in"
			return None

	def __p4ObjectCommand(self, command_list, callback, use_client=True):
		""" P4 is a bit of a pain.

			Some objects are easier to decode if you use the scripting interface
			and some are better with a direct command. The scripting interface is
			good for large slow queries as it can be used in a callback fashion
			by still with a be wait for end.

			This commands manages these calls and converts the returned data into
			readable python object.
		"""
		result = True

		if self.__p4Login():
			try:
				if sys.platform == 'win32':
					proc = subprocess.Popen(self.buildCommand(use_client, True) + command_list,
											stdout=subprocess.PIPE,
											env=self.environ,
											creationflags=CREATE_NO_WINDOW)
				else:
					proc = subprocess.Popen(self.buildCommand(use_client, True) + command_list,
											stdout=subprocess.PIPE,
											env=self.environ)

				i = 0
				while True:
					i = i + 1
					try:
						obj = marshal.load(proc.stdout)
					except(subprocess.CalledProcessError, ValueError, TypeError) as e:
						continue

					if type(obj) == dict:
						if obj['code'] == 'error':
							result = False
						else:
							callback(obj)

			except (subprocess.CalledProcessError, EOFError) as e:
				# I really hate having to use exceptions as loop bounds!!
				if type(e) == EOFError:
					return result
				else:
					return False
			except TypeError as e:
				# P4 is not installed
				return False
			except OSError:
				# P4 is not installed
				return False

		else:
			return False

	def __p4CommandWithInput(self, command_list, command_input, use_client=True):
		""" P4 is a bit of a pain (again).

			Need to be able to pipe stuff into P4 commands (could write - nuh!) for some of
			the actions. So more annoying code to do this. At least I get to learn more
			python.
		"""
		result = True
		stdout = None

		if self.__p4Login():
			try:
				if sys.platform == 'win32':
					proc = subprocess.Popen(self.buildCommand(use_client) + command_list,
											stdin=subprocess.PIPE,
											stdout=subprocess.PIPE,
											stderr=subprocess.PIPE,
											env=self.environ,
											creationflags=CREATE_NO_WINDOW)
				else:
					proc = subprocess.Popen(self.buildCommand(use_client) + command_list,
											stdin=subprocess.PIPE,
											stdout=subprocess.PIPE,
											stderr=subprocess.PIPE,
											env=self.environ)

				stdout, stderr = proc.communicate('\n'.join(command_input) + '\n')
				result = proc.returncode == 0

			except subprocess.CalledProcessError:
				# I really hate having to use exceptions as loop bounds!!
				result = False
		else:
			# TODO: log this "not logged in"
			pass

		return (result, stdout)

	def __addClient(self, obj):
		new_client = ClientDetails()

		new_client.name = obj['client']
		new_client.update = int(obj['Update'])
		new_client.access = int(obj['Access'])
		new_client.root   = obj['Root'][0].upper() + obj['Root'][1:]
		new_client.owner  = obj['Owner']
		new_client.options = obj['Options'].split(' ')
		new_client.description = obj['Description'].splitlines()

		self.clients[obj['client']] = new_client

	def __getClientList(self):
		if self.user_name is None or self.user_name == '':
			self.__p4ObjectCommand(['clients'], self.__addClient, use_client=True)
		else:
			self.__p4ObjectCommand(['clients', '-u', self.user_name], self.__addClient, use_client=True)

	def getClientViews(self, client):
		result = []
		got_object = []

		if self.__p4ObjectCommand(['client', '-o'], lambda obj: got_object.append(obj)):
			for item in got_object[0]:
				if item[:4] == 'View':
					parts = got_object[0][item].split()
					result.append((parts[0], parts[1]))

		return result

	def getClientDirectory(self, client_name):
		result = None

		if len(self.clients) == 0:
			self.__getClientList()

		if client_name in self.clients:
			result = self.clients[client_name].root

		return result

	def findClient(self, name=None, directory=None):
		result = None

		if name is not None:
			if name in self.clients:
				result = self.clients[name]
		else:
			for client in self.clients:
				if self.clients[client].root == directory:
					result = self.clients[client]
					break

		return result

	def getClientFromDirectory(self, directory):
		result = None

		if len(self.clients) == 0:
			self.__getClientList()

		result = self.findClient(directory = directory)

		return result

	def getSCMVersion(self):
		value = subprocess.check_output(['p4', '-V'])

		for line in value.split('\n'):
			if line[0:4] == "Rev.":
				return line

		return None

	def getType(self):
		return 'P4'

	def getUrl(self):
		return self.url

	def getRoot(self):
		if self.current_client is not None:
			return self.current_client.root
		else:
			return self.working_dir

	def getFile(self, file_name, specific_commit = None):
		if specific_commit is not None:
			path = file_name + '@' + specific_commit
		else:
			path = file_name

		contents = self.__p4Command(['print', self.makeP4RelativeName(path)])

		if contents is None or contents == '':
			return []
		else:
			return contents.splitlines()[1:]

	def getPatch(self, specific_commit = None):
		if specific_commit is not None:
			commit = specific_commit
		else:
			if self.version != '':
				commit = self.version
			else:
				commit = self.__p4Command(['changes', '-m', '1']).split(' ')[1]

		output = self.__p4Command(['describe', '-a', commit])

		return output.splitlines()

	def hasFileChanged(self, file_name, specific_commit = None):
		if specific_commit is not None:
			path = file_name + '@' + specific_commit
		else:
			path = file_name

		result = self.__p4Command(['diff', '-f', '-sl', self.makeP4RelativeName(path)])

		if result[0:4] == 'same':
			return False
		else:
			return True

	def makeP4RelativeName(self, path):
		if path.startswith(self.current_client.root):
			use_path = path[len(self.current_client.root):].replace('\\', '/')
		elif path.startswith(os.path.abspath(self.current_client.root)):
			use_path = path[len(os.path.abspath(self.current_client.root)):].replace('\\', '/')
		else:
			use_path = path.replace('\\', '/')

		if use_path[0]  == '/':
			use_path = use_path[1:]

		if self.current_branch is not None:
			return"//" + self.current_client.name + '/' + self.current_branch.name +'/' + use_path
		else:
			return "//" + self.current_client.name + '/' + use_path

	def getDirectoryListing(self, directory_name):
		result = []

		call_back = lambda obj : result.append(('file', obj['depotFile']))
		self.__p4ObjectCommand(['files', os.path.join(self.makeP4RelativeName(directory_name), "*")], call_back)

		call_back = lambda obj : result.append(('dir', obj['dir']))
		self.__p4ObjectCommand(['dirs', os.path.join(self.makeP4RelativeName(directory_name), "*")], call_back)

		return []

	def generateFileName(self, name, branch=None):
		if branch is None and self.current_branch is None:
			return os.path.join(self.working_dir, name)
		elif branch is not None:
			return os.path.join(self.working_dir, branch.name, name)
		else:
			return  os.path.join(self.working_dir, self.current_branch.name, name)

	def getBranch(self):
		if self.current_client is None:
			return "unknown"
		else:
			return self.current_client.name

	def getCurrentVersion(self):
		""" This should return the reference for the current instance.
			With P4 this is kind of difficult as the model does not lend itself to
			to specifying a version. So we should go with the current workspace as
			this is mostly used to identify that you are doing now.
		"""
		if self.current_client is not None:
			return self.current_client.name
		else:
			return 'default'

	def getHistory(self, filename=None, version=None, max_entries=None):
		result = []
		changes = ['changes', '-l']

		call_back = lambda obj : result.append(scm.HistoryItem(obj['change'], obj['desc'], obj['time'], None, None))

		if filename is None:
			changes.append(self.makeP4RelativeName('...'))
		else:
			changes.append(self.makeP4RelativeName(filename))

		if version is not None:
			changes.append('@' + version)

		if max_entries is not None:
			changes += ['-m', str(max_entries)]

		if self.__p4ObjectCommand(changes, call_back):
			return result
		else:
			return None

	def setVersion(self, version):
		return False

	def getVersion(self):
		return self.getCurrentVersion()

	def getCommitList(self):
		return self.getHistory()

	status_lookup = {	'deleted':'D',
						'updated':'U',
						'add'	 :'A',
						'edit'	 :'M'}

	def treeChangeFunction(self, result, obj):
		if 'action' in obj:
			if obj['action'] in SCM_P4.status_lookup:
				action = SCM_P4.status_lookup[obj['action']]
			else:
				action = '?'

			length = len(self.working_dir) + 1
			result.append(scm.SCMStatus(action, obj['clientFile'][length:]))

		elif 'clientFile' in obj:
			length = len(self.working_dir) + 1
			result.append(scm.SCMStatus('M', obj['clientFile'][length:]))

	def getTreeChanges(self, from_version = None, to_version = None, path = None, check_server=False):
		result = None

		if check_server is True:
			result = []

			call_back = lambda obj : self.treeChangeFunction(result, obj)

			# TODO: might be better to so, the following then do a reconcile add.
			# p4 diff -f -sl
			# follow this with a "status -a" to find the new files.
			if self.quick_updates:
				self.__p4ObjectCommand(['sync', '-n', '-m'], call_back)
			else:
				self.__p4ObjectCommand(['reconcile', '-n','-m'], call_back)

			# and now the opened files - does P4 suck... Question left for the audience.
			self.__p4ObjectCommand(['diff', '-sa'], call_back)

		return result

	def getDiffDetails(self, from_version = None, to_version = None, path = None):
		if path is None:
			file_path = self.makeP4RelativeName('...')
		else:
			file_path = self.makeP4RelativeName(path)

		if from_version is not None:
			from_path = file_path + '@' + from_version
		else:
			from_path = file_path

		if to_version is not None:
			to_path = file_path + '@' + to_version
		else:
			to_path = file_path

		if from_version is None and to_version is None:
			from_path = from_path + '#head'
			return self.p4CommandDiff(['diff', '-du', from_path, to_path])
		else:
			return self.p4CommandDiff(['diff2', '-du', from_path, to_path])

	def getChangeList(self, specific_commit):
		""" This function will return a change list for the specified change """
		contents = []
		call_back = lambda obj: contents.append(obj)

		# TODO: remove "-a" as it not longer works :(
		contents = self.__p4Command(['describe', '-S', '-du', str(specific_commit)])
		if contents is not None:
			parts = contents.split("\n")

			if len(parts) > 1:
				(author, timestamp, comment, changes) = self.parsePerforceUnifiedDiff(specific_commit, contents.split('\n'))
			else:
				return None
		else:
			return None

		return scm.ChangeList(specific_commit, timestamp, author, comment, changes)

	def changeListFunction(self, result, obj):
		if 'oldChange' not in obj:
			result.append((obj['change'], '0'))
		else:
			result.append((obj['change'], obj['oldChange']))

	def getTreeChangeDetails(self, from_version = None, to_version = None, path = None):
		result = []

		change_range = ''

		if from_version is not None and to_version is not None:
			change_range = '@{:d},{:d}'.format(from_version, to_version)

		elif from_version is not None:
			change_range = '@{:d},#head'.format(from_version)

		elif to_version is not None:
			change_range = '@0,{:d}'.format(to_version)

		# set the path
		if path is None:
			changes_path = self.makeP4RelativeName('...' + change_range)
		else:
			changes_path = self.makeP4RelativeName(path + change_range)

		# first lets get the change list.
		change_list = []

		call_back = lambda obj : self.changeListFunction(result, obj)

		self.__p4ObjectCommand(['changes', changes_path], call_back)

		for change in change_list:
			result.append(self.getDiffDetails(change[1], change[0], path))

		return result

	def getTags(self):
		return []

	def getBranches(self):
		branch_list = []
		call_back = lambda obj: branch_list.append(scm.Branch(None, obj['branch'], None, None))
		result = self.__p4ObjectCommand(['branches'], call_back)

		return (result, branch_list)

	def searchCommits(self, search_string, selected_commits = []):
		return []

	def checkObjectExists(self, object_name, specific_commit = None):
		if specific_commit is not None:
			path = object_name + '@' + specific_commit
		else:
			path = object_name

		name = self.makeP4RelativeName(path)

		branch_list = []
		call_back = lambda obj: branch_list.append(obj)
		result = self.__p4ObjectCommand(['files', name], call_back)

		return result and len(branch_list) > 0

	def isRepositoryClean(self):
		return False

	#---------------------------------------------------------------------------------
	# Functions that amend the state of the repository
	#---------------------------------------------------------------------------------

	def initialise(self, create_if_required=False, bare=False):
		client = None

		result = self.getClientFromDirectory(self.working_dir)

		if result is None:
			result = self.createClient(self.working_dir, 'initial_client')
			self.current_client = self.clients['initial_client']
			self.__p4ObjectCommand(['clients', '-o', 'initial_client'], self.__addClient, use_client=False)
		else:
			self.current_client = result

		return result is not None

	def amendClient(self, directory, name, description, options, view_spec):
		client_spec = [ 'Client: ' + name,
						'Owner: ' + self.user_name,
						'Description: ' + description,
						'Root: ' + os.path.abspath(directory),
						'Options: ' + options,
						'View:' ]

		for view in view_spec:
			client_spec.append(view)

		(result, _) = self.__p4CommandWithInput(['client'], client_spec, False)

		return result

	def createClient(self, directory, name, description=None, view_spec=None):
		if not os.path.exists(directory):
			os.makedirs(directory)

		if description is None:
			client_desc = "created by beorn_lib"
		else:
			client_desc = description

		client_spec = [ 'Client: ' + name,
						'Owner: ' + self.user_name,
						'Description: ' + client_desc,
						'Root: ' + os.path.abspath(directory),
						'Options: allwrite',
						'View:' ]

		if view_spec is not None:
			client_spec += view_spec
		else:
			client_spec.append('\t//depot/... //' + name + '/...')

		(result, _) = self.__p4CommandWithInput(['client'], client_spec, False)

		if result:
			self.__getClientList()

		return result

	def addBranch(self, branch_name, branch_point = None, switch_to_branch=False):
		result = None

		branch_spec = [ 'Branch: ' + branch_name,
						'Owner: ' + self.user_name,
						'Options: unlocked',
						'Description: branch created by boern_lib',
						'View:']

		if type(branch_point) in [scm.Commit, scm.Branch]:
			point = branch_point.commit_id

		# TODO: do this properly -- need to do stuff -- good for testing.
		if branch_point is None:
			branch_spec.append('\t//depot/... //depot/' + branch_name + '/...')
		else:
			branch_spec.append('\t//depot/' + point + '/... //depot/' + branch_name + '/...')

		(status, value) = self.__p4CommandWithInput(['branch'], branch_spec)
		if status:
			split = value.split()
			result = scm.Branch(split[1], branch_name, None, None)

			# it's P4 it's always complicated.
			self.switchBranch(result)

		return result

	def addCommit(self, files = None, empty = False, message = None):
		result = None
		if message is None:
			desc = "branch created by boern_lib"
		elif type(message) == str or type(message) == str:
			desc = message
		else:
			desc = '\n'.join(message)

		change_spec = [ 'Change: new',
						'Client: ' + self.current_client.name,
						'User: ' + self.user_name,
						'Description: ' + desc ]

		(status, value) = self.__p4CommandWithInput(['change'], change_spec)

		if status:
			split = value.split()

			if files is not None:
				self.__p4Command(['rec', '-c', split[1]] + files)

			if self.__p4Command(['submit', '-c', split[1]]) is not None:
				result = scm.Commit(split[1], [], desc)

		return result

	def switchBranch(self, branch=None, name=None):
		result = []

		if branch is not None:
			use_name = branch.name
		elif name is not None:
			use_name = name
		else:
			return False

		call_back = lambda obj : result.append(obj)
		if self.__p4ObjectCommand(['client', '-o'], call_back, True):
			index = 0
			dir_name = None

			view_spec = []
			while True:
				name_view = 'View' + str(index)
				if name_view in result[0]:
					if dir_name is None:
						split = result[0][name_view].split()

						if split[1] == '//' + self.current_client.name + '/' + use_name + "/...":
							dir_name = split[1].lstrip('//' + self.current_client.name + '/')

					view_spec.append('\t' + result[0][name_view])
				else:
					self.current_branch = branch
					break
				index += 1

			if dir_name is None:
				#view_spec.append('\t//' + use_name +'/... //' + self.current_client.name + '/' +  use_name + "/...")
				view_spec.append('\t//depot/' + use_name +'/... //' + self.current_client.name + '/' +  use_name + "/...")

				name = result[0]['Client']
				root = result[0]['Root'][0].upper() + result[0]['Root'][1:]
				options = result[0]['Options']
				description = result[0]['Description']

				if self.amendClient(root, name, description, options, view_spec):
					self.__p4ObjectCommand(['sync', '-q', os.path.join(self.working_dir, use_name, '...')], call_back)
					self.current_branch = branch

			try:
				os.chdir(os.path.join(self.working_dir, use_name))
				result = True
			except:
				result = False

		return result

	def merge(self, merge_from, merge_to = None):
		result = False

		command = ['integrate']

		if type(merge_to) in [scm.Commit, scm.Branch]:
			command.append(merge_to.name)

		if type(merge_from) in [scm.Commit, scm.Branch]:
			command.append(merge_from.name)

		result = self.__p4Command(command)
		#p4 integrate //depot/yourcode/dev/...@MYCODE_DEV.1.0 //depot/yourcode/rel/...

		return scm.Commit('1', [], 'test')

	def getFileList(self, roots, decode_state, line):
		result = 0

		if line[0:3] == '...':
			[name, action] = line[4:].split(None, 1)

			# remove the depot part from the name, easier to read in the review tree.
			for item in roots:
				if name.startswith(item):
					name = name[len(item):]
					break

			decode_state.files.insert(0, (name, action))

		elif line[0:15] == 'Differences ...':
			result = 1

		return result

	def getDifferences(self, decode_state, line):
		if line[0:5] == "==== ":
			if len(decode_state.lines) > 0:
				decode_state.change_list.append(scm.Change(	decode_state.start_line,
															decode_state.start_len,
															decode_state.end_line,
															decode_state.end_len,
															decode_state.lines))

				decode_state.lines = []

			if decode_state.current_file is not None:
				# trusting P4 to not be stupid and list the files in the same order
				# as the patches.
				if decode_state.current_file[1] == 'add':
					change = [scm.Change(0, 0, 0, len(decode_state.lines), decode_state.lines)]
					parts = decode_state.current_file[0].split('#')
					decode_state.result.append(scm.ChangeItem(parts[1], None, decode_state.current_file[1], parts[0], parts[0], change))
					decode_state.lines = []

				elif len(decode_state.change_list) > 0:
					# Add the file if only they have changes. P4 lists files without changes.
					parts = decode_state.current_file[0].split('#')
					decode_state.result.append(scm.ChangeItem(	parts[1],
																None,
																decode_state.current_file[1],
																parts[0],
																parts[0],
																decode_state.change_list))

			decode_state.change_list = []
			decode_state.in_hunk = False
			decode_state.current_file = decode_state.files.pop()

		elif line[0:2] == "@@":
			if len(decode_state.lines) > 0:
				decode_state.change_list.append(scm.Change(	decode_state.start_line,
															decode_state.start_len,
															decode_state.end_line,
															decode_state.end_len,
															decode_state.lines))

			decode_state.in_hunk = True
			decode_state.lines = []
			parts = line.split()
			decode_state.start_line = int(parts[1].split(',')[0][1:])
			decode_state.start_len  = int(parts[1].split(',')[1])
			decode_state.end_line = int(parts[2].split(',')[0][1:])
			decode_state.end_len  = int(parts[2].split(',')[1])

		elif decode_state.in_hunk or (decode_state.current_file is not None and decode_state.current_file[1] == 'add'):
			decode_state.lines.append(line)

	def parsePerforceUnifiedDiff(self, version, diff_array):
		""" Parse Perforce Unified Diff

			It pretty much goes without saying at this point but I will
			just day for completeness: P4 Sucks.

			Okedokie. P4's diff format starts with the files that have
			changed and the type of change. Then followed by the diffrences.
		"""
		state = 0
		roots = []
		decode_state = DecodeState()

		parts = diff_array[0].split()
		sks = parts[3].split('@')
		author = sks[0]

		if len(sks) > 1:
			client = sks[1]
		else:
			client = ''

		if client not in self.clients:
			# the client was not found, lets update and see what's happening.
			self.__getClientList()

		# do we know the client?
		if client in self.clients:
			decode_state.client = self.clients[client]

			# We need the roots to normalise the reviews.
			for item in self.getClientViews(client):
				roots.append(item[0][:-3])

		comment = []
		# get the comment for the commit.
		for line in diff_array[1:]:
			if len(line) >= 1 and (line[0] == '\t' or line[0] == '\r'):
				comment.append(line[1:])
			else:
				break

		# Get the date time for the commit.
		if len(parts) < 6:
			# TODO: This needs fixing.
			patch_time = 6
		else:
			# Get the date time for the commit.
			date = datetime.datetime.strptime(parts[5] + "_" + parts[6], "%Y/%m/%d_%H:%M:%S")
			patch_time = int(time.mktime(date.timetuple()))

		for line in diff_array:
			# TODO: handle file renames - "moved from"
			if state == 0:
				state = self.getFileList(roots, decode_state, line)
			else:
				self.getDifferences(decode_state, line)

		if len(decode_state.lines) > 0:
			decode_state.change_list.append(scm.Change(	decode_state.start_line,
														decode_state.start_len,
														decode_state.end_line,
														decode_state.end_len,
														decode_state.lines))

		return (author, patch_time, comment, decode_state.result)

#	def fixConflict(self, item, how = MERGE_WORKING):
#		return False

	def sync(self, pull = True, push = False):
		return False

# Register this type with SCM.
scm.supported_scms.append(scm.SupportedSCM('P4', checkForType, SCM_P4))
# vim: ts=4 sw=4 noexpandtab nocin ai
