# Indigo Buggie #
## version 1.6.5 ###

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
    1.  Byte the bullet and move to Python 3.
        I don't really wanna, but it will make life eaiser. But what version to pick
        and what version is not going to bit rot. Seriously contemplating moving the
        code to C or something stable (GO and Rust are just as bad - if not worse
        than Python for breaking changes). Meh. (yes I know bite ged'it).

    2.  Add Redmine support.
        This is a given as was always the goal for this to intergrated with servers
        so I did not have to have multiple browers open for no reason.

    3.  Write documentation for plugin writing.
        This is a framework for writing plugin, so it should be easy to do that but
        there is not docuemtation to document framework and how it works.

    4.  Write test cases.
        Need to write a version of tab_window and tab_control mocks so that development
        is easier to test. Also can set up CI for this.

    5.  Git server check.
        There is place holder code for this, but need to do a fetch and check to see if
        the server version of the code has changed compared to the unmodified version
        in the local repo. This can be done with a ref-tree check. That needs adding.

    6.  Fix bugs.

    7.  CodeReview needs fixing.

    8.  Get ride of submodules on release. They are annoying, change the release to
        copy the current version into the release code tree and release it in one
        lump. Might as well trim the test stuff as well for completeness.

    9.  Notes
        These are pretty usless and I don't use them. Change this to a log/diary and
        it might be more useful.

        I want notes to be tied to code, like TODO's but as annotations they stay in
        the note system and don't add to code. Should this generate tickets in the
        redmine (or shudder JIRA?) so my TODO's are a bit more formal?

    10. DocGen
        Lets intergrate that as a tool. Would be nice to see the docementation that is
        generated in the editor and to be able to see the changes reflected. This should
        intergrate with the Wiki (Redmine) but that would be a build change elsewhere.


## Changes ##

    Requires beorn_lib 1.5.1

    - Stop updating when the editor is in command mode, it's annoying whrn
      the command window closes or an ls disappears.

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
                  Copyright (c) 2019-2021 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
