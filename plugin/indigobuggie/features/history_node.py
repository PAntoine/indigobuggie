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
#    file: history_node
#    desc: History Tree Node.
#
#    	As you may guess this is a history node that represents a history item.
#
#  author: peter
#    date: 05/11/2018
#---------------------------------------------------------------------------------h
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import time
from beorn_lib.source_tree import SourceTree

class HistoryNode(SourceTree):
	def __init__(self, history_item, scm):
		super(HistoryNode, self).__init__(history_item.version, None)

		self.history_item = history_item
		self.scm = scm

	def getSummary(self):
		return self.history_item.summary[0:50]

	def getSCM(self):
		return self.scm

	def getVersion(self):
		return self.history_item.version

	def getTime(self):
		return time.strftime("%Y%m%d",time.gmtime(int(self.history_item.timestamp)))
		return self.history_item.timestamp

# vim: ts=4 sw=4 noexpandtab nocin ai
