# Indigo Buggie #
## version 3.0.0 ###

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
with the plugin data and the configuration (might be sensible to create a git repo here
and back this up - should be shareable between computers).

To start it up, call `IBOpenTab` from within the working directory for the project or
`IBOpenProject <project_name>` from anywhere on the file system.

## Changes ##
    - Enhancement:  Embedded beorn\_lib directly in the code base. The original idea is
                    never going to happen, so make life easier for myself (and you).
    - Enhancement:  Remove unused features. So don't really work very well and others
                    are going to be joined together to make a better feature.
    - Enhancement:  Now opens the tree to file.
    - Enhancement:  Now shows what file is opened and selected by the user.
    - Fix:          The server was not loading correctly, due to moving around the
                    beorn\_lib code.

## Notes ##

It's probably got loads of bugs, the biggest problems I have had is the change of the
strings. byte is no longer compatible with str. This has causes all sorts of problems
the biggest is that str.encode() now produces a byte array. This is annoying. Expect
loads of bugs.

## Licence and Copyright ##
                  Copyright (c) 2019-2024 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
