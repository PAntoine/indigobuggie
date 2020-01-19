# Indigo Buggie #
## version 1.3.2 ###

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
	4.  Add LOG as a feature.
	5.  Add ProjectPlan as a feature.
	6.  Add Gerrit as a code review feature.
	7.	Fix all the Bugs.

## Changes ##

	Requires beorn_lib 1.1.3

	- Bug fixes - mostly fixing swarm and timekeeper issues.
		TimeKeeper may actually work correctly now - should haved read the old code
		properly. I like to re-invent the wheel to often.

		Swarm is now reading the reviews and loading them into he browser. Will have
		to add time windows as swarm is Sooooooooooo Slllllooooooowww! There is still
		an outstanding bug that causes the global key not to work. But if you add
		the key manually it works. Probably a one-liner somewhere.

## Notes ##

Yes, I have implemented a ridiculous version of a python P4 front end. Why did I not use
the one provided by perforce? The headline reason is that I want to reduce the dependences
in the application and framework as much as possible. Secondary, I don't like the P4 one
but I am not really that into P4 just have to use it for work.

## Licence and Copyright ##
                  Copyright (c) 2019-2020 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
