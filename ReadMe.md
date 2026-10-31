# Indigo Buggie #
## version 3.1.0 ###

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
    - Feature: Add Remotes to the SourceTree
    - Feature: Now calls the server close on exit
    - Feature: Tidyup the config loading
    - Feature: Added .ib_override.
    - Feature: Adding syntax file for settings menu
    - Fix:     There is a bug in `bwipe` when closing windows.  (HEAD -> fix_issues)
    - Fix:     Remotes should be returned when true.
    - Fix:     Fixed an issue with self.keylist not existing and not autosaves
    - Fix:     Fixed off by one and branch syntax
    - Fix:     Add unicode (and fix syntax)

## Licence and Copyright ##
                  Copyright (c) 2019-2026 Peter Antoine
                           All rights Reserved.
                     Released Under the MIT Licence
