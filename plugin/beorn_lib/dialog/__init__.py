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
#    file: __init__
#    desc: This is the init file for the dialog object.
#
#  author: Peter Antoine
#    date: 31/08/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from collections import namedtuple as namedtuple
from beorn_lib.dialog.base import ElementItem
from beorn_lib.dialog.base import BaseDialog
from beorn_lib.dialog.dialog import Dialog

#---------------------------------------------------------------------------------
# Dialog Type
#---------------------------------------------------------------------------------
DIALOG_TYPE_TEXT	= 1
DIALOG_TYPE_HTML	= 2

#---------------------------------------------------------------------------------
# Text Layout Objects
#---------------------------------------------------------------------------------
Element	= namedtuple('Element', ['element', 'parameters'])

# vim: ts=4 sw=4 noexpandtab nocin ai
