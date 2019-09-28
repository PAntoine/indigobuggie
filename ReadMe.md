# Indigo Buggie #
## version 1.1.1 ###

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

The default configuration works, but what is the best one, don't really know yet
as still getting used to using it myself.

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
	4.	Real code review support (Swarm and Gerrit).
	5.	Allow conversion from the one true time to local times.
	6.	Developer documentation. How to write a new feature or an extension
		for one. I.e. code review or SCM.
	7.	Some bug fixing!!!
	8.	Notifications (for timers, code reviews, etc...)
	9.  Multi-tab does not work. Probably due to cls/global variables causing problems.
		Also searching for windows/buffers are not limited correctly to the tab.
	10.	Project feature needs to be completed and the project loading.
	11.	Some of the features are not correctly handling cross machine user files but
	    this will be fixed later. Get the basic functions working first.
	12. Proper code review engines integration.

## Changes ##

	Requires beorn_lib 1.0.6

	- Bug: Fixed so that it works on Linux (and with a real loaded SCM).
	- Anti-Feature: Turned off timekeeper as it causes a stutter with P4.

## Notes ##

Yes, I have implemented a ridiculous version of a python P4 front end. Why did I not use
the one provided by perforce? The headline reason is that I want to reduce the dependences
in the application and framework as much as possible. Secondary, I don't like the P4 one
but I am not really that into P4 just have to use it for work.

## Licence and Copyright ##
                    Copyright (c) 2019 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
