#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#    file: bigraph_search_element
#    desc: This class is the search element for the bi-graph search.
#
#  author: Peter Antoine
#    date: 21/12/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

class BiGraphSearchElement(object):
	""" A Search Element """
	__slots__ = ('colour', 'index', 'streams')

	def __init__(self, colour, index, streams):
		self.colour		= colour
		self.index		= index
		self.streams	= streams

# vim: ts=4 sw=4 noexpandtab nocin ai
