#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#    file: bigraph_entry
#    desc: This python class is the bygraph entry class.
#
#  author: Peter Antoine
#    date: 14/12/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

class BiGraphEntry(object):
	""" An entry in the bi-graph """
	__slots__ = ('commit_id', 'parents', 'children', 'tags', 'branches', 'description')

	def __init__(self, commit_id, parents, children, tags, branches, description):
		self.tags			= tags
		self.parents		= parents
		self.children		= children
		self.branches		= branches
		self.commit_id		= commit_id
		self.description	= description

# vim: ts=4 sw=4 noexpandtab nocin ai
