# Indigo Buggie #
## version 1.6.1 ###

This is now Beta, I think this is (finally) starting to look good. (Famous Last Words :) )

## Description ##

This is a set of development plugins.

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
        is easier to test. Also can set up CI for this.

    4.  Git server check.
        There is place holder code for this, but need to do a fetch and check to see if
        the server version of the code has changed compared to the unmodified version
        in the local repo. This can be done with a ref-tree check. That needs adding.

    5.  Fix bugs.

    6.  CodeReview needs fixing.

## Changes ##

	Requires beorn_lib 1.4.1

    - Updated the documentation that I did not do when pushing 1.6.0.
    - SCM Server fixed would crash after startup.
    - SCM detection moved to server.
    - Fixed issue with git repo in symlink not being walked.
    - Fixed Timekeeper so that stoptime is properly added.
    - Add the vim COMmmands (IBOpenTab and IBOpenProject),
    - Fixed features and added an empty message.
    - Fixed resource directory settings
    - Fixed crash in history node for new item (without history)
	- Added that open project will not do the CD for the editor.

## Notes ##

As mentioned, the swarm review engine does not allow for amendments and updates. It
is also probably broken at the moment, can be bothered fixing it, won't need it to
the new year - so will leave it till then.

The control window needs to handle the case when it is changed to another buffer
and needs to handle this. It can cause the plugin to get into a weird state where
all the windows it has (and the tab) need to be closed and opened again. Need to
handle the unload and load for the window/buffer.

Probably need to merge Notes and Tasks as one thing. Seems a bit silly to have them
as different features. Most tasks are just notes in the code. May need to add a
log-book / diary feature as this maybe more useful. But for now just get the current
features working and released.

## Licence and Copyright ##
                  Copyright (c) 2019-2020 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
