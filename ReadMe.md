# Indigo Buggie #
## version 2.0.0 ###

Back to Alpha :)

Converted to python3 - why not - too many other things don't work with 2.7. :(

This conversion has really put me off python3, also it seems the language has
the same problems the my work language (C++) has that it won't stop moving with
pointless changes. I think one may go back to C (C99) where I can. But that
is a rant that has nothing to do with this.

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

    Requires beorn_lib 2.0.0

	- converted to python 3.

## Notes ##

It's probably got loads of bugs, the biggest problems I have had is the change of the
strings. byte is no longer compatible with str. This has causes all sorts of problems
the biggest is that str.encode() now produces a byte array. This is annoying. Expect
loads of bugs.

## Licence and Copyright ##
                  Copyright (c) 2019-2021 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
