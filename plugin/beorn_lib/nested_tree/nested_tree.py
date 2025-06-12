#!/usr/bin/env python
#---------------------------------------------------------------------------------
#    file: nested_tree
#    desc: This file holds the root class for the nested_tree.
#
#  author: Peter Antoine
#    date: 20/07/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from .nested_tree_node import NestedTreeNode

class NestedTree (NestedTreeNode):
	""" The nested tree class

		The tree is a nested tree, it means that a node can have many items
		as children, and are walked this way.

		The tree is nested, that is each node is allowed to have a sub-tree that
		is independent of the rest of the tree.
	"""
	def __init__(self):
		super(NestedTree, self).__init__()

# vim: ts=4 sw=4 noexpandtab nocin ai
