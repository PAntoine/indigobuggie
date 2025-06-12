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
#    file: bigraph
#    desc: This class holds the bi-directional graph of the repository.
#          This structure is designed to hold a map of the commits in the
#          repository. It is designed to stitch the list of commits,tags and
#          branches together and build a searchable bigraph of the tree.
#
#  author: Peter Antoine
#    date: 25/11/2013
#---------------------------------------------------------------------------------
#                     Copyright (c) 2013 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from . import scm
import collections
from .bigraph_entry import BiGraphEntry as BiGraphEntry
from .bigraph_search_element import BiGraphSearchElement as BiGraphSearchElement

#---------------------------------------------------------------------------------
# Module functions.
#---------------------------------------------------------------------------------

class BIGRAPH(object):
	""" Bi-Directional Class """
	def __init__(self, nodes = None, branches = None, tags = None):
		if nodes is None:
			self.nodes = {}
		else:
			self.nodes = nodes

		if branches is None:
			self.branches = {}
		else:
			self.branches = branches

		if tags is None:
			self.tags = {}
		else:
			self.tags = tags

		self.head = None		# the root commit of the graph
		self.index = []			# the ordered list of the graph entries

	# class worker functions
	def addEntry(self, commit_id):
		new_entry = BiGraphEntry(commit_id, [], [], [], [], '')

		# add the node the node dictionary
		self.nodes[commit_id] = new_entry
		self.index.append(new_entry)

		return new_entry

	def updateEntry(self, entry, commit):
		result = True

		if commit.parents == []:
			self.head = commit.commit_id

		entry.description = commit.description

		for pid in commit.parents:
			parent = self.nodes.get(pid)

			if parent is None:
				parent = self.addEntry(pid)

			# connect the node to parents
			entry.parents.append(parent)
			parent.children.append(entry)

		return result

	@classmethod
	def buildGraph(cls, scm_instance):
		""" Build Graph

			This method will take in the list of commits, tags and branches and it
			will create a bi-directional graph that models the repository. This allows
			for the repository to be walked and displayed in the way the user requires.
		"""
		commit_list = scm_instance.getCommitList()

		# NOTE: can speed this up be using a specific command that returns a dictionary (same with tags)
		branches = {}
		(_, branch_list) = scm_instance.getBranches()
		for branch in branch_list:
			branches[branch[1]] = branch[0]

		# build the tags dictionary
		tags = {}
		(_, tag_list) = scm_instance.getTags()
		for tag in tag_list:
			tags[tag[0]] = tag[1]

		# create the object
		result = BIGRAPH(None, branches, tags)

		# build the graph
		for commit in commit_list:
			if commit.commit_id in list(result.nodes.keys()):
				entry = result.nodes[commit.commit_id]
			else:
				entry = result.addEntry(commit.commit_id)

			result.updateEntry(entry, commit)

		# now attach the tags to the entries in the graph
		for tag in tags:
			if tag in result.nodes:
				result.nodes[tag].tags.append(tag)

		# now attach the branches
		for branch in branches:
			if branch in result.nodes:
				result.nodes[branch].branches.append(branch)

		return result

	def searchByTags(self, tag_list):
		""" Search By Tags

			This function will return all the commits that are common to the
			list of tags.
		"""
		result = []
		commit_list = []

		for tag in tag_list:
			for item in self.tags.keys:
				if tag == self.tags[item]:
					commit_list.append(item)
					break
			else:
				failed = True

		if not failed:
			result = self.searchByCommits(commit_list)

		return result

	def searchByBranch(self, branch_list):
		""" Search By Branch

			This function will return all the commits that are common to the
			list of branches.
		"""
		is_ok = True
		result = []
		commit_list = []

		for branch in branch_list:
			for item in list(self.branches.keys()):
				if branch == item:
					commit_list.append(self.branches[item])
					break
			else:
				is_ok = False

		if is_ok:
			result = self.searchByCommits(commit_list)

		return result

	def searchByCommits(self, commit_list):
		""" Search Commits

			This function will return a partial graph of the commits that
			are UNIQUE for the given commits and there children. These
			commits will be return in reverse chronological order.

			The function will only return the commits that are common to
			all the commits. Commits are common if the branch they are on
			merges with another branch then eventually ends with the common
			commit.
		"""
		result = []

		# validate the search
		for item in commit_list:
			if item not in self.nodes:
				result = True

		if len(commit_list) == 1:
			# this is a straight branch retrieval - simple walk function
			result = self.retrieveBranch(commit_list[0])
		else:
			# lets do the complex search
			result = self.searchTree(commit_list)

		return result

	def retrieveBranch(self, start_commit, stop_at_merge = False, stop_at_branch = False):
		""" Retrieve Branch

			This function will return all the commits that are connected to the
			start commit. So if any commit in this chain is a merge, both sides
			of the merge will be return.

			If only commits that are accessible from a single commit is required
			then set both stop flags. The stop flags will reduce the amount of
			commits that are returned.

			This function expects the start_commit to have been validated before
			the function is called.

			This function will return a list of HistoryItem tuples.
		"""
		result = []

		search_set = set(start_commit)

		index_num = self.index[start_commit]

		# search the index, from after the start commit
		# do the search in reverse chronological order.
		for item in self.index[index_num::-1]:
			if len(search_set) > 0:
				if item.commit_id in search_set:
					# add to the found search results
					result.append(self.exportCommit(item))

					# update the search, looking for the current parents. Only adding
					# items that are not already in the list. The commit_id's of the
					# parents have been made a list by the export function.
					search_set.remove(item.commit_id)
					search_set.union(result[-1].parents)
				else:
					# search ended
					break

		return result

	def exportCommit(self, commit):
		""" Export Commit

			This function export a commit graph node to an external self contained
			item.
		"""
		# Ok, add to the result
		children = []
		for child in commit.children:
			children.append(child.commit_id)

		parents = []
		for parent in commit.parents:
			parents.append(parent.commit_id)

		return scm.HistoryItem(commit.commit_id, 'no desc', parents, children)

	def searchTree(self, commit_list, all_commits = False):
		#pylint: disable=e1103
		""" Search Tree

			This function will search the tree for all the commits that
			are common to the list of commits in the commit_list. If the
			all_commits flag is set to True then it will also dump any
			commit that is connected to the commits before the last common
			commit is found for the commit list.

			This function returns, list of commit_id's in branch order. For the
			places that the list overlap, i.e. where a branch starts and ends,
			the same commit will appear in both lists.

			i.e.
				[[id_1,id_2,id_3,id_4],[id_2,id_5,id_3],[id_6,id_4]]

			This would render as:

			   o - id_1
			   o - id_2
			   |\
			   | o - id_5
			   |/
               o - id_3
			   | o - id_6
			   |/
			   o - id_4

		"""
		index = 0
		found = None
		found_id = None
		streams = []
		all_found = 0
		found_dict = collections.OrderedDict()
		search_queue = collections.OrderedDict()

		# build the search queue
		for index, commit in enumerate(commit_list):
			# generate the colour for the search
			colour = 1 << index
			all_found |= 1 << index

			# now add to the search queue - add the set of branches that make up
			# this branch.
			search_queue[commit] = BiGraphSearchElement(colour, index, (1 << index))
			streams.append([])

		# now do the search
		while len(search_queue) > 0 and found is None:
			# take the top item off the queue
			(current_commit, current_item) = search_queue.popitem(last=False)
			current_stream = streams[current_item.index]
			joined = False

			while current_commit not in search_queue and found is None:
				commit = self.nodes[current_commit]

				if len(commit.parents) == 0:
					# Ok, we have no more parents
					break

				else:
					if commit.commit_id in found_dict:
						if found_dict[commit.commit_id].colour == all_found:
							found = found_dict[commit.commit_id]
							found_id = commit
							break

						else:
							if not joined:
								current_stream.append(commit)
								joined = True

							found_dict[commit.commit_id].colour  |= current_item.colour
							found_dict[commit.commit_id].streams |= current_item.streams

					else:
						# needs to be added to a stream - and the found dictionary
						if not joined:
							current_stream.append(commit)

						found_dict[commit.commit_id] = BiGraphSearchElement(current_item.colour, index, current_item.streams)

					# Search all parents:
					# 1. All parents that are joins, need to do the join
					# 2. The first non-joined parent is the next commit.
					# 3. Any parent, after the first needs to be pushed to
					#    to the search_list.
					got_first = False
					next_first = None

					for parent in commit.parents:
						if parent.commit_id in found_dict:
							# It joins with a commit that has been visited before
							found_dict[parent.commit_id].colour  |= current_item.colour
							found_dict[parent.commit_id].streams |= current_item.streams

							current_item.colour = found_dict[parent.commit_id].colour
							current_item.streams = found_dict[parent.commit_id].streams

							# check to see if we have completed the search
							if found_dict[parent.commit_id].colour == all_found:
								found = found_dict[parent.commit_id]
								found_id = parent
								break

						elif parent.commit_id in search_queue:
							# Ok, we have a join with commit that is waiting to be visited
							search_queue[parent.commit_id].colour  |= current_item.colour
							search_queue[parent.commit_id].streams |= current_item.streams

							streams[search_queue[parent.commit_id].index].append(commit)

							# check to see if we have completed the search
							if search_queue[parent.commit_id].colour == all_found:
								found = search_queue[parent.commit_id]
								found_id = parent
								break

						elif got_first:
							# Ok, add to the search list - add the current
							index += 1
							streams.append([commit])
							current_streams = (current_item.streams | (1 << index))
							search_queue[parent.commit_id] = BiGraphSearchElement(current_item.colour, index, current_streams)

						if not got_first:
							# Ok, we now have the next commit.
							got_first = True
							next_first = parent.commit_id

					current_commit = next_first

		# Did the search succeed?
		result = []

		if found is not None:
			found_streams = found.streams
			index = 0

			while found_streams != 0:
				if found_streams & 0x01:
					if found_id in streams[index]:
						# trim the list down to the common commit
						result.append(streams[index][0:streams[index].index(found_id)+1])
					else:
						result.append(streams[index])

				index += 1
				found_streams = found_streams >> 1

		return result

	def lineariseSearch(self, search_results):
		""" Linearise Search

			This simple function will linearise the search results into a single list.
			It will make the list end at the last item in the list. If the commits exist
			in any other of the lists then it will start at the same line.

			This function will output a list of tuples for each of the commits in the
			search list. Thus tuple is the commit and a list of the streams that the
			commit is in.
		"""
		pointers = [0] * len(search_results)
		wait_count = {}
		stream_len = []
		result = []

		# count the lengths, to know when to stop
		for stream in search_results:
			stream_len.append(len(stream))

		while stream_len != pointers:
			for index, stream in enumerate(search_results):

				# have a look if we have not reached the end.
				if pointers[index] < stream_len[index]:

					# is this element one of which we are waiting for?
					if stream[pointers[index]] in wait_count:

						found_all = True
						for wait in wait_count[stream[pointers[index]]]:
							if search_results[wait][pointers[wait]] != stream[pointers[index]]:
								found_all = False
								break

						# have all the items that we are waiting for been found?
						if found_all:
							# add the element to the results
							result.append((stream[pointers[index]], wait_count[stream[pointers[index]]]))

							# move all the waiting queues forward.
							for wait in wait_count[stream[pointers[index]]]:
								pointers[wait] += 1

					elif self.addToWaitList(index, search_results, pointers, wait_count):
						# If got here then it was added to the wait list, need to
						# do nothing now.
						pass

					else:
						# Ok, no need to wait, can output the result now.
						result.append((stream[pointers[index]], [index]))

						# increment the pointer
						pointers[index] += 1
		return result

	def addToWaitList(self, item, lists, start_points, wait_list):
		""" Add To Wait List

			 This function is used in the search and it used to build the wait list.
			 It should not be called from outside the search.
		"""
		result = False

		for index, stream in enumerate(lists):
			if index != item:
				if lists[item][start_points[item]] in stream[start_points[index]:]:
					# Ok, we have a match
					if lists[item][start_points[item]] in wait_list:
						if index not in wait_list[lists[item][start_points[item]]]:
							wait_list[lists[item][start_points[item]]].append(index)
					else:
						wait_list[lists[item][start_points[item]]] = [item, index]

					result = True

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
