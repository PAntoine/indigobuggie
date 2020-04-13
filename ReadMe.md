# Indigo Buggie #
## version 1.4.0 ###

This is an alpha (almost Beta) release.

## Description ##

This is a set of development plugins.

They are all based on the BeornLib libraries.

## Installation ##

Using vundle so install in the usual way.

## Basic Configuration ##

The default configuration works, but what is the best one, don't really know yet
as still getting used to using it myself.

If you are not using P4 make sure you turn it off (and that goes double for Swarm)
these applications are the slowest that I have ever used. It makes using this a
tad slow.

## Starting/Stopping ##

Type `:call IB_OpenTab()` and it will start.
Type `:call IB_ToggleHelp()` and this will give you the list of features installed.

## TODO ##

	1.	No error messages are being reported.
		Serious oversight, need to be fixed.
	2.	No logging is being kept.
		Even though the user won't see this it is worth putting in place and
		will make the rest of this eaiser.
	3.	Fix the BUGS!!!
	4.  Add LOG as a feature.
	5.  Add ProjectPlan as a feature.
	6.  Add Gerrit as a code review feature.
	7.	Fix all the Bugs.

## Changes ##

	Requires beorn_lib 1.2.0

	- Add some navigation changes to SourceTree
		- Includes fixing some issues with history
	- De-coupled the SCM and SourceTree hopefully makes it faster.
	- Moved some code from the vim callback. This might have been causing the stutters.
	- Added a vim function for opening the tree to the current file. It needs the
	  tab to be already opened.

## Notes ##

As mentioned, the swarm review engine does not allow for amendments and updates.

The control window needs to handle the case when it is changed to another buffer
and needs to handle this. It can cause the plugin to get into a weird state where
all the windows it has (and the tab) need to be closed and opened again.

Probably need to merge Notes and Tasks as one thing. Seems a bit silly to have them
as different features. Most tasks are just notes in the code. May need to add a
log-book / diary feature as this maybe more useful. But for now just get the current
features working and released.

## Licence and Copyright ##
                  Copyright (c) 2019-2020 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
