# Indigo Buggie #
## version 1.0.2 ###

This is an alpha release.

Yes it is being released as version 1, because why not. It is probably not really
fit for use yet, but I wan't to be able to install it from one place (still using
vundle) and will use it to see what features are missing and which I need to drop.

## Description ##

This is a set of development plugins.

They are all based on the BeornLib libraries.

## Installation ##

Using vundle so install in the usual way.

## Basic Configuration ##

Still being defined. See the docs for now - the default configuration will work.

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
	4.	Other SCM support (perforce next).
	5.	Real code review support (Swarm and Gerrit).
	6.	Allow conversion from the one true time to local times.
	7.	Developer documentation. How to write a new feature or an extension
		for one. I.e. code review or SCM.
	8.	Some bug fixing!!!
	9.	Notifications (for timers, code reviews, etc...)
	10. Multi-tab does not work. Probably due to cls/global variables causing problems.
		Also searching for windows/buffers are not limited correctly to the tab.
	11.	Project feature needs to be completed and the project loading.
	12.	Some of the features are not correctly handling cross machine user files but
	    this will be fixed later. Get the basic functions working first.

## Changes ##

	-	Bug: 		Crash when SCM updates.
	-	Bug: 		Crash in `scm_feature`.
	-	Bug: 		Fix mouse click line number.
	- 	Bug: 		Fixed one of the crashes in SCM
	-	Enhancement: Tidy up SourceTreeFeature code.
	-	Enhancement: Added the diff against HEAD in source tree feature.

## Licence and Copyright ##
                    Copyright (c) 2019 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
