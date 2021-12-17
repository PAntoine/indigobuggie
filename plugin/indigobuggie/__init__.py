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
#    file: __init__
#    desc: The indigo buggie python package.
#
#  author: peter
#    date: 23/09/2018
#---------------------------------------------------------------------------------
#                     Copyright (c) 2018 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------
import vim
from . import features
from .tab_window import TabWindow
from .tab_control import TabControl

global_features = []

def CreateFeature(name, tab_inst, configuration):
	""" Initialise the Feature """
	if hasattr(features, name):
		config = dict(configuration)
		new_feature = getattr(features, name)(configuration)

		if tab_inst is not None:
			tab_inst.attachFeature(new_feature)

def Initialise(name, tab_inst, configuration):
	""" Initialise the Feature """
	if hasattr(features, name):
		config = dict(configuration)
		new_feature = getattr(features, name)(configuration)

		if tab_inst is not None:
			tab_inst.attachFeature(new_feature)
		else:
			# todo: park the shared global features
			global_features.append(new_feature)
			new_feature.initialise(None)

# vim: ts=4 sw=4 noexpandtab nocin ai
