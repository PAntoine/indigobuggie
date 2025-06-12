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
#    file: utilities
#    desc: This is a collection of utilities that are useful.
#
#  author: peter
#    date: 22/12/2019
#---------------------------------------------------------------------------------
#                     Copyright (c) 2019 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os.path

class Utilities(object):
	@staticmethod
	def findFileInParentTree(path, name):
		""" This will check that the file exists in the tree. """
		result = None
		working_path = os.path.abspath(path)
		while working_path != '':
			if name in os.listdir(working_path):
				# found it.
				result = working_path
				break

			(new_path, _) = os.path.split(working_path)
			if working_path == new_path:
				break
			working_path = new_path

		return result

	@staticmethod
	def isChildDirectory(child, parent):
		""" This will check that the parent is in child and is an actual
			path part. i.e. it does not match "/a/a/bb_a/a" with "/a/a/bb"
			so that it has to walk the path to make sure it is correct with
			the correct delimiter.
		"""
		result = False
		real_parent = os.path.abspath(parent)
		(working_path, _) = os.path.split(os.path.abspath(child))

		if parent in child:
			while working_path != '':
				if real_parent == working_path:
					result = True
					break

				(new_path, _) = os.path.split(working_path)
				if working_path == new_path:
					break
				working_path = new_path

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
