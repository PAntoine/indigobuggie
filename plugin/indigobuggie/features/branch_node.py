#!/usr/bin/env python
#--------------------------------------------------------------------------------
#     _____           _ _                ______                    _
#    (_____)         | (_)              (____  \                  (_)
#       _   ____   _ | |_  ____  ___     ____)  )_   _  ____  ____ _  ____
#      | | |  _ \ / || | |/ _  |/ _ \   |  __  (| | | |/ _  |/ _  | |/ _  )
#     _| |_| | | ( (_| | ( ( | | |_| |  | |__)  ) |_| ( ( | ( ( | | ( (/ /
#    (_____)_| |_|\____|_|\_|| |\___/   |______/ \____|\_|| |\_|| |_|\____)
#                        (_____|                      (_____(_____|
#
# Name  : branch_node.py
# Desc  : This class holds the branch nodes for the SCM Tree.
#
# Author: Peter Antoine
# Date  : 2026-11-01
#--------------------------------------------------------------------------------
#                     Copyright (c) 2026 Peter Antoine
#                            All rights Reserved.
#                      Released Under the MIT Licence
#--------------------------------------------------------------------------------

import time
from beorn_lib.source_tree import SourceTree

class BranchNode(SourceTree):
	def __init__(self, scm, name, commit_id, summary, version):
		super(BranchNode, self).__init__(name, None)
		self.setSCM(scm)
		self.summary = summary
		self.version = version
		self.commit_id = commit_id

	def __eq__(self, other: object) -> bool:
		if isinstance(other, BranchNode) and self.name == other.name and self.version == other.version:
			return True
		else:
			return False

	def getSummary(self):
		return self.summary[0:50]

	def getVersion(self):
		return self.version

	def getCommitId(self):
		return self.commit_id

	def getBranchName(self):
		if self.version is None:
			return self.name
		else:
			return 'remotes/' + self.version + '/' + self.name

# vim: ts=4 sw=4 noexpandtab nocin ai
