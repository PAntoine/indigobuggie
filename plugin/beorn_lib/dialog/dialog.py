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
#    file: dialog
#    desc: The is the root class for the dialogs.
#          All the sub-dialog types are based on this.
#
#  author: Peter Antoine
#    date: 26/08/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

import beorn_lib.dialog
from .html_dialog import HTMLDialog
from .text_dialog import TextDialog

#---------------------------------------------------------------------------------
# Dialog Factory.
# The different back-end engines of the dialogs should not be  explicitly
# referenced in the code. This defeats the point of a generic framework.
#---------------------------------------------------------------------------------
def Dialog(engine, layout):
	if engine == beorn_lib.dialog.DIALOG_TYPE_TEXT:
		new_dialog = TextDialog()
	else:
		new_dialog = HTMLDialog()

	new_dialog.initialise(layout)

	return new_dialog

# vim: ts=4 sw=4 noexpandtab nocin ai
