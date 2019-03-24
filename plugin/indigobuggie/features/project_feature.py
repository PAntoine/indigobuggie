#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#     _____           _ _                ______                    _
#    (_____)         | (_)              (____  \                  (_)
#       _   ____   _ | |_  ____  ___     ____)  )_   _  ____  ____ _  ____
#      | | |  _ \ / || | |/ _  |/ _ \   |  __  (| | | |/ _  |/ _  | |/ _  )
#     _| |_| | | ( (_| | ( ( | | |_| |  | |__)  ) |_| ( ( | ( ( | | ( (/ /
#    (_____)_| |_|\____|_|\_|| |\___/   |______/ \____|\_|| |\_|| |_|\____)
#                        (_____|                      (_____(_____|
#
#    file: project_feature
#    desc: This class implements the Project Feature.
#
#    This feature controls settings for the underlying project.
#
#  author: peter
#    date: 17/11/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
import vim
import beorn_lib
from feature import Feature

class ProjectFeature(Feature):
	def __init__(self, configuration):
		result = super(ProjectFeature, self).__init__(configuration)
		self.project = beorn_lib.Project()

		if 'auto_create' in configuration:
			self.auto_create = configuration['auto_create']
		else:
			self.auto_create = False

		if 'specific_file' in configuration and configuration['specific_file'] != '':
			self.specific_file = configuration['specific_file']
		else:
			self.specific_file = None

	def initialise(self, tab_window):
		result = super(ProjectFeature, self).initialise(tab_window)

		if result:
			# Ok, do we have a specific project file to use?
			if self.specific_file is not None:
				project_file = self.specific_file
			else:
				ib_config_dir = self.tab_window.getSetting('Config_directory')
				project_file = os.path.join(ib_config_dir, 'project.pf')

			if os.path.exists(project_file):
				# open the project file
				self.loaded_ok = self.project.load(project_file)

			elif self.auto_create:
				# create the project file
				if self.project.create(ib_config_dir, 'project.pf'):
					self.autoConfig()
					self.project.save()
					result = True

	def autoConfig(self):
		pass

	def getProject(self):
		return self.project

	def close(self):
		if self.loaded_ok:
			self.project.save()

# vim: ts=4 sw=4 noexpandtab nocin ai
