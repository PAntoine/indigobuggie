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
#    file: __init__
#    desc: The init for the Indigobuggie features.
#
#  author: peter
#    date: 13/10/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from scm_feature import SCMFeature
from notes_feature import NotesFeature
from settings_feature import SettingsFeature
from my_tasks_feature import MyTasksFeature
from timekeeper_feature import TimeKeeperFeature
from code_review_feature import CodeReviewFeature
from source_tree_feature import SourceTreeFeature

supported_features=['SCMFeature',
					'NotesFeature',
					'SettingsFeature',
					'MyTasksFeature',
					'TimeKeeperFeature',
					'CodeReviewFeature',
					'SourceTreeFeature']

# vim: ts=4 sw=4 noexpandtab nocin ai
