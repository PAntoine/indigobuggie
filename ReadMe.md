# Indigo Buggie #
## version 2.1.0 ###

## Description ##

This is a set of development plugins. It works for handling most of the tedious task that I have
to leave the VIM window for. I want all the things in VIM (without too much IDE stuff).

I mostly use SourceTree (and the new HistoryTree). The task manager (which is a bit too basic)
is quite useful for finding the TODO's and such that I leave in the code.

This is my daily driver of plugins that I use at work and play.

They are all based on the BeornLib libraries.

## Installation ##

Using vundle so install in the usual way.

add to your vimrc (I assume Plugin will also work).
Bundle 'pantoine/indigobuggie'

Then do:
:BundleInstall


## Basic Configuration ##

The default configuration works, but what is the best one, don't really know yet
as still getting used to using it myself.

## Starting/Stopping ##

On first use call either `:IBOpenProject <project_name>` or `IBOpenTab` from the project
directory. This will set up the config in the default location `~\.config\indigobuggie\<dirname>`
with the plugin data and the configuration (might be sensible to create a gir repo here
and back this up - should be shareable between computers).

To start it up, call `IBOpenTab` from within the working directory for the project or
`IBOpenProject <project_name>` from anywhere on the file system.

## TODO ##
    1.  Add Redmine support.
        This is a given as was always the goal for this to intergrated with servers
        so I did not have to have multiple browers open for no reason.

    2.  Write documentation for plugin writing.
        This is a framework for writing plugin, so it should be easy to do that but
        there is not docuemtation to document framework and how it works.

    3.  Write test cases.
        Need to write a version of tab_window and tab_control mocks so that development
        is easier to test. Also can set up CI for this. The BeornLib has unit tests but
		the "the buggie" does not. I need to tidy up the window/tab_control split and
		fix the naming, them make sure that the vim commands are only in the Window.
		This will aid in porting, on the sad day that I might have to leave VIM behind.

    4.  Git server check.
        There is place holder code for this, but need to do a fetch and check to see if
        the server version of the code has changed compared to the unmodified version
        in the local repo. This can be done with a ref-tree check. That needs adding.

    5.  Fix bugs.

    6.  CodeReview needs fixing.
	    Also needs extending to GitHub Actions/Pull Requests. This is stuff I have to
		deal with now, so should fix the plugin to handle this. I would like updates on
		Actions that have been run - so I don't have to login to find them.

    7.  Get rid of submodules on release. They are annoying, change the release to
        copy the current version into the release code tree and release it in one
        lump. Might as well trim the test stuff as well for completeness.

    8.  DocGen
        Lets intergrate that as a tool. Would be nice to see the docementation that is
        generated in the editor and to be able to see the changes reflected. This should
        intergrate with the Wiki (Redmine) but that would be a build change elsewhere.

	9.	Structual should be integrated to, might have to convert the Javascript to C
		or Python. I ma thinking C, as it would be generally more useful.

## Changes ##

    Requires beorn_lib 2.1.1

	- Enhancement:	New feature HistoryTree.

## Notes ##

It's probably got loads of bugs, the biggest problems I have had is the change of the
strings. byte is no longer compatible with str. This has causes all sorts of problems
the biggest is that str.encode() now produces a byte array. This is annoying. Expect
loads of bugs.

## Licence and Copyright ##
                  Copyright (c) 2019-2022 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
