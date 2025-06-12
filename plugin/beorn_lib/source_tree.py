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
#    file: source_tree
#    desc: Source Tree Item.
#
#  author: peter
#    date: 17/10/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import os
from beorn_lib.utilities import Utilities
from beorn_lib.nested_tree import NestedTreeNode

class SourceTree(NestedTreeNode):
	# class properties
	suffix_filter = []
	directory_filter = []

	@classmethod
	def setSuffixFilter(cls, suffix_filter):
		cls.suffix_filter = suffix_filter

	@classmethod
	def setDirectoryFilter(cls, directory_filter):
		cls.directory_filter = directory_filter

	@classmethod
	def getSuffixFilter(cls):
		return cls.suffix_filter

	@classmethod
	def getDirectoryFilter(cls):
		return cls.directory_filter

	def __init__(self, name, root=None):
		self.name = name
		if root is not None:
			self.root = os.path.abspath(root)
			self.is_dir = True
		else:
			self.root = None
			self.is_dir = False

		self.scm  = None
		self.on_filesystem = False
		self.flag = None
		self.submodule = False
		self.is_dir = False
		self.is_link = False
		self.is_virtual = False
		self.is_shown = False

		# state of the item.
		self.item_state = {}

		super(SourceTree, self).__init__(name, None)

	def copy(self, new_node):
		super(SourceTree, self).copy(new_node)

		self.name = new_node.name
		self.root = new_node.root
		self.scm = new_node.scm
		self.is_dir = new_node.is_dir
		self.on_filesystem = new_node.on_filesystem
		self.flag = new_node.flag
		self.submodule = new_node.submodule
		self.item_state = new_node.item_state
		self.is_virtual = new_node.is_virtual

	def __lt__(self, other):
		if type(other) is SourceTree:
			return self.name < other.name
		return NotImplemented

	def __contains__(self, other):
		""" Contains

			Will return True if 'other' is the name of one of the children.
		"""
		if type(other) == str or type(other) == str:
			find_name = other
		elif isinstance(other, SourceTree):
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
		if type(other) == str or type(other) == str:
			find_name = other
		elif isinstance(other, SourceTree):
			find_name = other.name
		else:
			return None

		for child in self.getChildren():
			if find_name == child.name:
				return child
		else:
			return None

	def isDir(self):
		return self.is_dir

	def isLink(self):
		return self.is_link

	def isOnFilesystem(self):
		return self.on_filesystem

	def isShown(self):
		return self.is_shown

	def setShown(self):
		self.is_shown = True

	def clearShown(self):
		self.is_shown = False

	def updateItemState(self, name, state):
		self.item_state[name] = state

		# We have been changed, so all parents have to be modified.
		self.setFlag('M')

	def removeItemState(self, name):
		if name in self.item_state:
			del self.item_state[name]

			parent = self.getParent()

			if parent is not None:
				self.clearFlag()

	def hasState(self):
		return self.item_state != {}

	def state(self):
		for scm_type in self.item_state:
			yield (scm_type, self.item_state[scm_type])

	def getState(self, scm_name=None):
		result = None

		if scm_name is not None:
			if scm_name in self.item_state:
				result = self.item_state[scm_name]
		else:
			result = self.item_state

		return result

	def setFlag(self, flag):
		self.flag = flag

		current = self.getParent()

		while current is not None:
			if current.flag is None or current.flag < flag:
				current.flag = flag

				current = current.getParent()
			else:
				break

	def clearFlag(self, recursive=True):
		# walk up the tree removing the state of items that don't
		# have any children with states.
		current = self

		while current is not None:
			found_state = False

			for item in current.getChilden():
				if item.hasState() or item.getFlag() is not None:
					found_state = True
					break

			if found_state is True:
				# if we have found a state stop clearing the
				# parents states, and exit now.
				break
			else:
				current.flag = None
				current = current.getParent()

	def getFlag(self):
		return self.flag

	def setSCM(self, scm, submodule=False):
		""" Set SCM

			If this item in the tree points to an SCM then this
			function should be called with a reference to the
			scm. The reference is application specific.
		"""
		self.scm = scm
		self.submodule = submodule

	def isSCM(self):
		""" IsSCM is this item an scm reference """
		return self.scm is not None

	def isSubmodule(self):
		""" If the submodule flag is set """
		return self.scm is not None and self.submodule

	def getSCM(self):
		""" return the scm that has (or has not) been set on the item """
		return self.scm

	def findSCM(self, scm_type=None):
		if self.scm is not None and (scm_type is None or self.scm.getType() == scm_type):
			return self.scm
		else:
			parent = self.getParent()

			while parent is not None:
				if parent.getSCM() is not None and (scm_type is None or parent.getSCM().getType() == scm_type):
					return parent.getSCM()
				else:
					parent = parent.getParent()
			return None

	def getChilden(self):
		""" TODO """
		current = self.child_node

		while current is not None:
			yield current
			current = current.next_node

	def getPath(self, full=False):
		""" Get Path

			Returns the path of the specific item.
		"""
		if self.root is not None:
			result = self.root
		else:
			result = self.name

			current = self.parent_node

			while current is not None:
				if current.root is not None:
					if full:
						result = os.path.join(current.root, result)
					else:
						result = os.path.join(current.name, result)
					break
				else:
					result = os.path.join(current.name, result)
					current = current.parent_node

		return result

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
				new_item = SourceTree(dir_list[index])
				new_item.on_filesystem = True
				current.addNodeBefore(new_item)
				index += 1

			elif dir_list[index] > current.name:
				# Item does not exist on file system
				current.on_filesystem = False
				current = current.next_node

			else:
				# the same
				current = current.next_node
				index += 1


	def prune(self, recursive=True):
		""" Prune

			This function will prune the tree. It will remove any item from the tree
			that does not belong to either and SCM or is in the file system. It will
			not prune itself.
		"""
		remove_list = []

		# Ok, prune the children first (if recursive), else remember the items
		# that need to be removed as we can't delete them without breaking the
		# linked list walk.
		for item in self.getChilden():
			if not item.is_virtual and not item.on_filesystem and not item.hasState():
				remove_list.append(item)

			if recursive:
				item.prune(recursive)

		# now remove the item(s) while not referencing it.
		for item in remove_list:
			item.deleteNode(False)


	def splitPath(self, path):
		result = []

		(drive, p_copy) = os.path.splitdrive(path)

		while p_copy != os.path.sep and p_copy != '':
			(p_copy, tail) = os.path.split(p_copy)
			result.insert(0, tail)

		return result

	def rebaseTree(self, path, existing_node):
		""" Rebase the SourceTree node.

			This will change the directory that the SourceTree object points
			to and make the current root a child of it.
		"""
		# duplicate self.
		old_path = os.path.abspath(self.getPath())
		self.root = path

		# get the old children.
		old_children = []
		for child in self.getChilden():
			old_children.append(child)

		self.child_node = None
		self.last_child_node = None

		parts = self.splitPath(os.path.relpath(old_path, path))

		self.name = os.path.basename(path)
		new_base = self.addPathBitToTree(parts, path, existing_node)

		if len(old_children) > 0:
			new_base.is_dir = True
			path = new_base.getPath()
			new_base.is_exist = os.path.exists(path)

			if new_base.is_exist:
				new_base.is_link = os.path.islink(path)

		# append the hold children to the end.
		for item in old_children:
			item.parent_node = None
			new_base.addChildNode(item, mode=NestedTreeNode.INSERT_ASCENDING)

	def addPathBitToTree(self, path_bits, path_root, existing_node):
		result = self
		found = True

		for part in path_bits:
			path_root = os.path.join(path_root, part)
			if found:
				next_item = result.findChild(part)
				if next_item is None:
					found = False
				else:
					result = next_item

			if not found:
				if self.isDirectoryFiltered(part):
					result = None
					break
				else:
					if existing_node is None:
						is_exist = os.path.exists(path_root)
						is_link = False
						is_dir  = False

						if is_exist:
							is_link = os.path.islink(path_root)

						if part != path_bits[-1]:
							is_dir = True

						new_node = SourceTree(part)
						new_node.on_filesystem	= is_exist
						new_node.is_link  		= is_link
						new_node.is_dir			= is_dir
					else:
						new_node = existing_node

					result.addChildNode(new_node, mode=NestedTreeNode.INSERT_ASCENDING)
					result = new_node

		return result

	def addTreeNodeByPath(self, path, existing_node=None, rebase_tree=False):
		""" Add an Item to the Tree by Path

			It will find the place that the item belongs
			and if the item does not exist, create add the new
			item. If the item exists already, then return the
			old one.

			@param	path			The path of the object to add to the tree.
			@param	existing_node	And existing node to tree.
			@param	rebase_tree		If True, if the path is a parent of the current
									tree root, then make the new node the new root
									and then fill in the gap between the two. It
									will not create any other branch nodes.
		"""
		result = None

		if not self.isSuffixFiltered(path):
			path_root = os.path.abspath(self.getPath())
			path_bits = []
			new_path = self.getPath()

			if path_root.startswith(path):
				if rebase_tree:
					self.rebaseTree(os.path.commonprefix([path_root, path]), existing_node)
			else:
				path_bits = self.splitPath(path)

			result = self.addPathBitToTree(path_bits, new_path, existing_node)

		return result

	def findItemNode(self, path):
		""" Find Item Node

		This function will find a node in the tree from a path. If the
		node exists then it will return the Node, else None.
		"""
		if self.root == path:
			result = self
		else:
			if type(path) == bytes:
				path = path.decode("utf-8")

			if self.root and path.startswith(self.root):
				path = os.path.relpath(path, self.root)

			path_bits = self.splitPath(path)
			result = self

			for part in path_bits:
				result = result.findChild(part)

				if result is None:
					break

		return result

	def isOnFileSystem(self):
		return self.on_filesystem

	def checkOnFileSystem(self):
		""" Check Item On File System

			Check to see if the item is still on the file system.
		"""
		self.on_filesystem = os.path.exists(self.getPath(True))
		return self.on_filesystem

	def isSuffixFiltered(self, name):
		result = False

		if self.suffix_filter != []:
			(path, suffix) = os.path.splitext(name)
			result = suffix[1:] in self.suffix_filter

		return result

	def isDirectoryFiltered(self, name):
		result = False

		if self.directory_filter != []:
			if name in self.directory_filter:
				result = True

		return result

	def update(self, path='', recursive=True):
		""" Update

			This function will refresh the directory files that are on
			the filesystem. It will not actually remove any items from
			the tree, that should be done by calling prune().
		"""
		result = False

		if path == '':
			path = self.getPath()

		if (self.is_dir or self.root is not None) and os.path.isdir(path):

			# Ok, we are in a directory
			dir_list = os.listdir(path)

			# Ok, no children need to add some
			for item in dir_list:
				if item not in self:
					child_path = os.path.join(path, item)

					is_dir = os.path.isdir(child_path)
					is_link = os.path.islink(child_path)

					if (is_dir and not self.isDirectoryFiltered(item)) or (not is_dir and not self.isSuffixFiltered(item)):
						new_item = SourceTree(item)
						new_item.is_dir = is_dir
						new_item.is_link = is_link
						new_item.on_filesystem = True
						self.addChildNode(new_item, mode=NestedTreeNode.INSERT_ASCENDING)
						result = True

		# We need to walk down all the children
		for child in self.getChilden():
			child_path = os.path.join(path, child.getName())

			child.on_filesystem = os.path.exists(child_path)

			if recursive and child.on_filesystem:
				result = child.update(child_path) or result

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
