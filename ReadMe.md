# Indigo Buggie #
## version 3.1.1 ###

## Description ##

This is a set of development plugins. It works for handling most of the tedious task that I have
to leave the VIM window for. I want all the things in VIM (without too much IDE stuff).

I mostly use SourceTree (and the new HistoryTree). The task manager (which is a bit too basic)
is quite useful for finding the TODO's and such that I leave in the code.

This is my daily driver of plugins that I use at work and play.

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
  - Fix:     Race condition with closing named windows. Added a work around for now.
  - Feature: Changed the way that branches and remotes work. Looks like the source tree
             and will do who tree diffs in the history window. Makes it a more useful tool.

## Licence and Copyright ##
                  Copyright (c) 2019-2026 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
