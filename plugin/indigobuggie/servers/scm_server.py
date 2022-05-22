#!/usr/bin/env python3
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
	__slots__ = ('scm', 'primary', 'change_list')

	def __init__(self, scm, primary, change_list):
		self.scm = scm
		self.primary = primary
		self.change_list = change_list

def send_message(message):
	sys.stdout.write(json.dumps(message, ensure_ascii=False) + '\n')
	sys.stdout.flush()

def send_scm_list(ident, scm_list):
	""" Send the list of SCMs found to the client """
	for scm in scm_list:
		scm_data = {}
		scm_data['ident'] = ident
		scm_data['name']  = scm.scm.getName()
		scm_data['type']  = scm.scm.getType()
		scm_data['root']  = scm.scm.getRoot()
		scm_data['primary'] = scm.primary
		scm_data['url'] = scm.scm.getUrl()
		scm_data['user_name'] = scm.scm.getUserName()
		scm_data['password'] = scm.scm.getPassword()
		send_message(scm_data)

def create_scm(scm_list, scm_type, primary, working_dir, parameters):
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
		scm_list.append(SCMItem(result, primary, []))

def thread_function(parameters, ident):
	found_scms = beorn_lib.scm.findRepositories(None)

	poll_period = int(parameters['poll_period'])
	server_period = int(parameters['server_period'])

	scm_list = []

	for fscm in found_scms:
		if 'enabled_scms' not in parameters or fscm.type in parameters['enabled_scms']:
			# If we don't have a valid configuration turn them all on.
			for item in fscm.primary:
				create_scm(scm_list, fscm.type, True, item, parameters)

			for item in fscm.sub:
				create_scm(scm_list, fscm.type, False, item, parameters)

	send_scm_list(ident, scm_list)

	# Update first - before we hit the wait loop.
	for scm in scm_list:
		update_source_tree(ident, scm, True)

	now = int(time.time())
	next_local_check = now + poll_period
	next_server_check = now + server_period

	timeout_time = min(next_server_check, next_local_check)

	while closedown.wait(timeout_time - now) is False:
		check_server = False

		if int(time.time()) >= next_server_check:
			check_server = True

		for scm in scm_list:
			update_source_tree(ident, scm, check_server)

		# take the time again as updating may take a while
		now = int(time.time())
		if check_server is True:
			next_server_check = now + server_period
		else:
			next_local_check = now + poll_period

		timeout_time = min(next_server_check, next_local_check)

def update_source_tree(ident, scm, check_server):
	changes = scm.scm.getTreeChanges(check_server=check_server)

	if changes is not None and (len(changes) > 0 or len(scm.change_list) > 0):
		new_changes = set(changes) - set(scm.change_list)
		unchanged = set(scm.change_list) - set(changes)

		if len(new_changes) + len(unchanged) > 0:
			message = {}
			message['type'] = scm.scm.getType()
			message['root'] = scm.scm.getRoot()
			message['ident'] = ident
			message['changes'] = list(new_changes)
			message['unchanged'] = list(unchanged)
			send_message(message)

		scm.change_list = list(changes)



if __name__ == "__main__":
	closedown = Event()
	closedown.clear()

	if sys.argv[2] == 'test':
		parameters = json.loads('{"enabled_scms": ["Git"], "server_period": "6", "scm_config": {"Git": {"server": "", "repo_url": "None", "working_dir": ".", "user_name": "", "password": ""}}, "poll_period": "60"}')
	else:
		parameters = json.loads(base64.b64decode(sys.argv[2]))

	x = Thread(target=thread_function, args=(parameters, sys.argv[1]))
	x.start()

	# wait for the thread to finish
	x.join()

# vim: ts=4 sw=4 noexpandtab nocin ai
