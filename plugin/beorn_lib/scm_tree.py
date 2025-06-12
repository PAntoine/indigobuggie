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
#    file: scm_tree
#    desc: This manages a source tree for the scm.
#
#  author: peter
#    date: 17/10/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from beorn_lib.nested_tree import NestedTreeNode

class SCMTree(NestedTreeNode):
	SCM_STATE_UNKNOWN	= 0
	SCM_STATE_UNCHANGED = 1
	SCM_STATE_ADDED 	= 2
	SCM_STATE_MODIFIED 	= 3
	SCM_STATE_DELETED	= 4

	def __init__(self, name, scm=None, state=SCM_STATE_UNKNOWN, payload=None):
		self.name = name
		self.open = True
		self.scm = scm
		self.state = state

		super(SCMTree, self).__init__(name, payload)

	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str:
			find_name = other
		elif isinstance(other, SCMTree):
			find_name = other.name
		else:
			return False

		for child in self.getChildren():
			if find_name == child.name:
				return True
		else:
			return False

	def getName(self):
		return self.name

	def findChild(self, other):
		if type(other) == str:
			find_name = other
		elif isinstance(other, SCMTree):
			find_name = other.name
		else:
			return None

		for child in self.getChildren():
			if find_name == child.name:
				return child
		else:
			return None

	def isSCMRoot(self):
		""" Is SCM Root

			If the current item is an scm root (or sub root) then return true
			else false.
		"""
		return self.scm is not None

	def getChilden(self):
		""" TODO """
		current = self.child_node

		while current is not None:
			yield current
			current = current.next_node

	def getPath(self):
		""" Get SCM Path

			Returns the path of the specific item.
		"""
		result = self.name
		current = self.parent_node

		while current is not None and not current.isSCMRoot():
			result = os.path.join(current.name, result)
			current = current.parent_node

		# scm path is only valid if it ends in an root item.
		if current.isSCMRoot():
			return result
		else:
			return None

	def replace(self, new_node):
		""" Copy the Node to the new object.

			This function will replace the node. Be careful as it is
			essentially doing a shallow copy so all the child nodes will
			not be duplicated and be will shared by the old node.

			The children of this item need to be re-parented. So this
			will make the tree inconsistent if both nodes are used. So
			the node that is being replaced should be discarded.

			The point of this function is too allow for a nodes class
			type to be changed without breaking the tree.
		"""
		# replace in the list
		if self.next_node is not None:
			self.next_node.prev_node = new_node

		if self.prev_node is not None:
			self.prev_node.next_node = new_node

		# Copy the values
		new_node.next_node		= self.next_node
		new_node.prev_node		= self.prev_node
		new_node.parent_node	= self.parent_node
		new_node.is_sub_node	= self.is_sub_node
		new_node.child_node		= self.child_node
		new_node.payload		= self.payload

		# Update the children to their new parent
		current = self.child_node

		while current is not None:
			current.parent_node = new_node
			current = current.getSibling()

	def __mergeChildren(self, dir_list):
		""" TODO """
		current = self.child_node
		index = 0

		while current is not None and index < len(dir_list):
			if dir_list[index] < current.name:
				current.addNodeBefore(SCMTree(dir_list[index], is_in_filesystem=True))
				index += 1

			elif dir_list[index] > current.name:
				# Item does not exist on file system
				current.is_in_filesystem = False
				current = current.next_node

			else:
				# the same
				current = current.next_node
				index += 1

	def clearFlags(self, recursive=True):
		""" TODO """

		self.is_in_scm = False
		self.is_modified = False

		if recursive:
			for item in self.getChilden():
				item.clearSCMFlags()

	def getSCM(self):
		""" """

		if self.isSCMRoot():
			return self.scm

		current = self.parent_node
		while current is not None:
			if current.isSCMRoot():
				return current.scm

			current = current.parent_node

		return None

	def setModifiedFlag(self):
		""" Set the Modified Flag

			For the SCM tree to work, if child item is marked
			as modified then all the parents need to be modified
			as well.

			The modified flag is reference counted
		"""
		self.state = SCMTree.SCM_STATE_UNCHANGED

	def resetModifiedFlag(self, recursive=False):
		""" Reset the Modified Flag

			This function will clear the modified flag that is
			set when the SCM things the file is different from
			the one on the server.
		"""
		if self.state != SCMTree.SCM_STATE_UNCHANGED and recursive and self.hasChild():
			for child in self.getChilden():
				child.resetModifiedFlag(True)

		self.state = SCMTree.SCM_STATE_UNCHANGED

	def update(self, path=None, recursive=True):
		""" Update the tree to reflect the current state of the tree compared to the
			SCM.
		"""
		scm = self.getSCM()

		# clear the modified flag from the tree.
		self.resetModifiedFlag(recursive)

		if scm is not None:
			for item in scm.getTreeListingGenerator():
				node = self.addTreeNodeByPath(item.name)

			for item in scm.getTreeChangesGenerator():
				node = self.findItemNode(item.path)
				if node is not None:
					if item.status == 'M':
						node.modified = 1
				else:
					node = self.addTreeNodeByPath(item.path)

	def splitPath(self, path):
		result = []

		(drive, p_copy) = os.path.splitdrive(path)

		while p_copy != os.path.sep and p_copy != '':
			(p_copy, tail) = os.path.split(p_copy)
			result.insert(0, tail)

		return result

	def addTreeNodeByPath(self, path, state=SCM_STATE_UNKNOWN):
		""" Add an Item to the Tree by Path

			It will find the place that the item belongs
			and if the item does not exist, create add the new
			item. If the item exists already, then return the
			old one.
		"""
		path_bits = self.splitPath(path)

		result = self
		finding = True

		for part in path_bits:
			if finding:
				next = result.findChild(part)
				if next is None:
					finding = False
				else:
					result = next

			if not finding:
				new_node = SCMTree(part)
				result.addChildNode(new_node)
				result = new_node

		return result

	def findItemNode(self, path):
		""" Find Item Node

		This function will find a node in the tree from a path. If the
		node exists then it will return the Node, else None.
		"""
		path_bits = self.splitPath(path)

		result = self

		for part in path_bits:
			result = result.findChild(part)

			if result is None:
				break

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
