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
#	 file: scm_server
#	 desc: The feature manages SCM integration.
#
#  author: peter
#	 date: 26/09/2020
#---------------------------------------------------------------------------------
#					  Copyright (c) 2020 Peter Antoine
#							All rights Reserved.
#					   Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import sys
import time
import json
import fcntl
import base64
from threading import Event, Thread

# Need to set the path up for boernlib
current = os.path.abspath(__file__)
parent,_ = os.path.split(current)
parent,_ = os.path.split(parent)
parent,_ = os.path.split(parent)

beorn_lib_path = os.path.join(parent, 'beorn_lib')

sys.path.insert(1, beorn_lib_path)

import beorn_lib

class SCMItem(object):
	__slots__ = ('scm', 'change_list')

	def __init__(self, scm, change_list):
		self.scm = scm
		self.change_list = change_list

def send_message(message):
	sys.stdout.write(json.dumps(message, ensure_ascii=False).encode('utf8') + '\n')
	sys.stdout.flush()

def create_scm(scm_list, scm_type, working_dir, parameters):
	result = None

	if 'scm_config' in parameters and scm_type in parameters['scm_config']:
		config = parameters['scm_config'][scm_type]
		result = beorn_lib.scm.create(  scm_type,
										working_dir = working_dir,
										server_url  = config['server'],
										user_name   = config['user_name'],
										password    = config['password'])
	else:
		result = beorn_lib.scm.create(scm_type, working_dir=working_dir);

	if result:
		scm_list.append(SCMItem(result, []))

def thread_function(parameters):
	found_scms = beorn_lib.scm.findRepositories(None)

	scm_list = []

	for fscm in found_scms:
		if 'enabled_scms' not in parameters or fscm.type in parameters['enabled_scms']:
			# If we don't have a valid configuration turn them all on.
			for item in fscm.primary:
				create_scm(scm_list, fscm.type, item, parameters)

			for item in fscm.sub:
				create_scm(scm_list, fscm.type, item, parameters)

	# Update first - before we hit the wait loop.
	for scm in scm_list:
		update_source_tree(scm)

	while closedown.wait(int(parameters['poll_period'])) is False:
		needs_pruning = False

		for scm in scm_list:
			update_source_tree(scm)

def update_source_tree(scm):
	result = False

	changes = scm.scm.getTreeChanges()

	if len(changes) > 0 or len(scm.change_list) > 0:
		new_changes = set(changes) - set(scm.change_list)
		unchanged = set(scm.change_list) - set(changes)

		if len(new_changes) + len(unchanged) > 0:
			message = {}
			message['type'] = scm.scm.getType()
			message['root'] = scm.scm.getRoot()
			message['changes'] = list(new_changes)
			message['unchanged'] = list(unchanged)
			send_message(message)

		scm.change_list = list(changes)

if __name__ == "__main__":
	closedown = Event()
	closedown.clear()

	parameters = json.loads(base64.b64decode(sys.argv[1]))

	x = Thread(target=thread_function, args=(parameters, ))
	x.start()

	# QUESTION:
	# Do I need to put a close handler in?

	# wait for the thread to finish
	x.join()

# vim: ts=4 sw=4 noexpandtab nocin ai
