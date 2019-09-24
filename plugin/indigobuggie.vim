" ---------------------------------------------------------------------------------
"      _____           _ _                ______                    _
"     (_____)         | (_)              (____  \                  (_)
"        _   ____   _ | |_  ____  ___     ____)  )_   _  ____  ____ _  ____
"       | | |  _ \ / || | |/ _  |/ _ \   |  __  (| | | |/ _  |/ _  | |/ _  )
"      _| |_| | | ( (_| | ( ( | | |_| |  | |__)  ) |_| ( ( | ( ( | | ( (/ /
"     (_____)_| |_|\____|_|\_|| |\___/   |______/ \____|\_|| |\_|| |_|\____)
"                         (_____|                      (_____(_____|
"
"     file: indigobuggie
"     desc: This is base vim plugin for the indigoBuggie toolset.
"
"   author: peter
"     date: 23/09/2018
" ---------------------------------------------------------------------------------
"                      Copyright (c) 2018 Peter Antoine
"                            All rights Reserved.
"                       Released Under the MIT Licence
" ---------------------------------------------------------------------------------

" GLOBAL INITIALISERS															{{{
if exists("s:indigo_buggie")
	finish
else
	let s:indigo_buggie = 1
endif

function s:ErrorMessage(string)
	echohl ErrorMsg
	echomsg a:string
	echohl Normal
endfunction

" Some Constant
:let s:LOAD_DO_NOT			= 0
:let s:LOAD_ON_TAB_OPEN		= 1
:let s:LOAD_AUTOMATICALLY	= 2

:let s:initialised = 0

" Sanity check
if !has("python")
	call s:ErrorMessage("Beorn requires vim is compiled with python - sorry.")
	fini
endif

if v:version < 801
	call s:ErrorMessage("Needs version 8.0.1 or greater. Use vimgitlog and/or Timekeeper if you can't update.")
	fini
endif

" Start up the python backend - so I can find the rest of the files
let s:plugin_path=expand("<sfile>:p:h")
py import os
py import vim
py import sys
py sys.path.insert(1, vim.eval('s:plugin_path'))
py sys.path.insert(1, os.path.join(vim.eval('s:plugin_path'),'features'))
py sys.path.insert(1, os.path.join(vim.eval('s:plugin_path'),'beorn_lib'))
py import indigobuggie
py global tab_control
py tab_control = indigobuggie.TabControl()

" Auto commands
"autocmd INDEGOBUGGIE TabEnter py TabControl.onEnterTab()<cr>
"autocmd INDEGOBUGGIE TabLeave py TabLeave.onLeaveTab()<cr>

"-------------------------------------------------------------------------------}}}
" Feature Configuration															{{{
if !exists("g:IB_use_project_config")
	" Use project config. --- How else you going to work? Other wise use defaults?
	" This will just stop it pooping config files, which might be worth it.
	" Should probably do this for the save directory - I do this below.`
	let g:IB_use_project_config = 1
endif

if !exists("g:IB_specific_file")
	" User has specific configuration file.
	let g:IB_specific_file = ''
endif

if !exists("g:IB_auto_create")
	" We want to create the project file if it does not exist.
	let g:IB_auto_create = 1
endif

if !exists("g:IB_enabled_features")
	" Turn on all the features
	let g:IB_enabled_features = ["SCMFeature", "SourceTreeFeature", "NotesFeature", "TimeKeeperFeature", "MyTasksFeature","CodeReviewFeature"]
endif

if !exists("g:IB_set_tab_line")
	" But default we will turn on all the features.
	let g:IB_set_tab_line = 1
endif

if !exists("g:IB_tab_name_function")
	" We default to our tabline function.
	let g:IB_tab_name_function="IB_TabName"
endif

if !exists("g:IB_Config_directory")
	" Default to a local config.
	let g:IB_Config_directory = ".indigobuggie"
endif

if !exists("g:IB_UseUnicode")
	if has('multi_byte')
		set encoding=utf-8
		let g:IB_UseUnicode=1
	else
		let g:IB_UseUnicode=0
	endif
endif


"-------------------------------------------------------------------------------}}}
" Public Functions																{{{
" FUNCTION: IB_SelectFeature													{{{
"
" This function will select the feature.
"
" vars:
"	item	The item for the feature that to be selected.
"
" returns:
"	nothing.
"
function IB_SelectFeature(item, tab_number)
	if a:item.loadable > s:LOAD_DO_NOT
		let tab_id = gettabvar(a:tab_number, "__tab_id__")
		py tab_control.getTab(int(vim.eval('tab_id'))).selectFeature(vim.eval('a:item.name'))
	endif
endfunction																		"}}}
"-------------------------------------------------------------------------------}}}
" FUNCTION: IB_OpenTab															{{{
"
" This function will open a IB tab.
"
" vars:
"	none
"
" returns:
"	nothing.
"
function IB_OpenTab(...)
	if a:0 == 0
		let path = '.'
	else
		let path = a:0
	endif


	let new_tab_id = pyeval("tab_control.addTab(vim.eval('path'), vim.eval('g:IB_enabled_features'))")
endfunction																		"}}}
" FUNCTION: IB_CloseWindow														{{{
"
" This function will close the feature and the side window.
"
" vars:
"	none
"
" returns:
"	nothing.
"
function IB_CloseWindow()
	py tab_control.unselectCurrentFeature()
endfunction																		"}}}
" FUNCTION: IB_ReOpenWindow														{{{
"
" This function will re-open the current window.
"
" vars:
"	none
"
" returns:
"	nothing.
"
function IB_ReOpenWindow()
	py tab_control.selectCurrentFeature()
endfunction																		"}}}
" FUNCTION: IB_ToggleHelp														{{{
"
" The features have a basic help system built-in. This function will toggle it.
" vars:
"	none
"
" returns:
"	nothing.
"
function IB_ToggleHelp()
	py tab_control.toggleHelp()
endfunction																	   "}}}
" FUNCTION: IB_OpenProject	 													{{{
"
" This function will a open project directory.
"
" This function will create a new tab and then initialise the project in the
" new tab.
"
" vars:
"	directory	The directory that is too be opened as a project.
"
" returns:
"	nothing.
"
function IB_OpenProject(directory)
	py tab_control.addTab(vim.eval('a:directory'))
endfunction																	   "}}}
" FUNCTION: IB_TabName	 														{{{
"
" This function will return the tabname.
"
" The tabline
"
" vars:
"	tab_number	The tab number for the tab name to return.
"
" returns:
"	nothing.
"
function IB_TabName(tab_number)
	let label = ''
	let bufnrlist = tabpagebuflist(a:tab_number)

	" Add '+' if one of the buffers in the tab page is modified
	for bufnr in bufnrlist
	  if getbufvar(bufnr, "&modified")
	    let label = '+'
	    break
	  endif
	endfor

	" Append the number of windows in the tab page if more than one
	let wincount = tabpagewinnr(a:tab_number, '$')
	if wincount > 1
	  let label .= wincount
	endif
	if label != ''
	  let label .= ' '
	endif

	" Append the buffer name
	if bufname(bufnrlist[tabpagewinnr(a:tab_number) - 1]) == ""
		return label . " [None] "
	else
		return label . bufname(bufnrlist[tabpagewinnr(a:tab_number) - 1])
endfunction																	   "}}}
" FUNCTION: IB_GuiTabName														{{{
"
" This function will return the tabname for the gui tab.
"
" returns:
"	nothing.
"
function IB_GuiTabName()
	if gettabvar(v:lnum, "__tab_name__") != ''
		let s .= '[ ' . gettabvar(i, "__tab_name__") . ' ]'
	else
		return call(g:IB_tab_name_function,[v:lnum])
	endif
endfunction																	   "}}}
" FUNCTION: IB_TabLine	 														{{{
"
" This function will handle a tabline.
"
" The tabline
"
" vars:
"	none
"
" returns:
"	nothing.
"
function! IB_TabLine()
	let tab_line = ''

	for i in range(tabpagenr('$'))
		" select the highlighting
		if i + 1 == tabpagenr()
			let tab_line .= '%#TabLineSel#'
		else
			let tab_line .= '%#TabLine#'
		endif

		if gettabvar(i+1, "__tab_id__") != ''
			let tab_line .= '[ ' . gettabvar(i+1, "__tab_name__") . ' ]'
		else
			" set the tab page number (for mouse clicks)
			let tab_line .= '%' . (i + 1) . 'T'

			" the label is made by the value of the function in gui tab name
			let tab_line .= ' %{call(g:IB_tab_name_function,[' . (i + 1) . '])} '
		endif

	endfor

	" after the last tab fill with TabLineFill and reset tab page nr
	let tab_line .= '%#TabLineFill#%T'

	" right-align the label to close the current tab page
	if tabpagenr('$') > 1
		let tab_line .= '%=%#TabLine#%999Xclose'
	endif

	return tab_line
endfunction																		"}}}
" FUNCTION: IB_TimerCallBack													{{{
"
" This function is the callback for the window timers.
" It will pass the timer id the tab control and it can pass it to the correct
" timer.
" vars:
"	none
"
" returns:
"	nothing.
"
function! IB_TimerCallBack(timer_id)
	py tab_control.getTimerHandler(vim.eval('a:timer_id'))
endfunction
"-------------------------------------------------------------------------------}}}
" Private Functions																{{{
" FUNCTION: AddFeature															{{{
"
" This function will initialise the plugin. This is called once and will call
" the initialise for the different features.
"
" vars:
"	name		The named of the feature.
"	load_mode	The mode to load the feature in.
"
" returns:
"	nothing.
"
function s:AddFeature(name, load_mode)
	for item in g:IB_enabled_features
		if item == a:name
			call s:ErrorMessage("Already Enabled")
			return
		endif
	endfor

	call add(g:IB_enabled_features, {'name': a:name, 'loadable': a:load_mode})
endfunction																		"}}}
"-------------------------------------------------------------------------------}}}
" Auto functions and other vim settings.										{{{
if g:IB_set_tab_line
	set tabline=%!IB_TabLine()
	set guitablabel=%!IB_GuiTabName()
endif

augroup IB
	au!
	au TabClosed * py tab_control.closeTab(vim.bindeval("tabpagenr()"))
"	au TabEnter * py tab_control.onTabEntered(vim.bindeval("tabpagenr()"))
"	au TabLeave * py tab_control.onTabLeave(vim.bindeval("tabpagenr()"))
	au VimLeavePre * py tab_control.closeAllTabs()
augroup END

sign define ib_line text=>> linehl=Comment
sign define ib_item text=-> texthl=Error

"-------------------------------------------------------------------------------}}}

" HACK: Holy hack batman.
" FUNCTION:	Beorn_waitForKeypress()											{{{
"
" This function will wait for a keypress and return the key.
"
" If the key is invalid or the 'ESC' had been pressed then the
" function will return 0.
" vars:
"	none
"
" returns:
"   the key value or '0' for an invalid key.
"
function! Beorn_waitForKeypress()
	let result = 0

	try
		let char = getchar()

	catch /^Vim:Interrupt$/
		return "KEY_VALUE_EXIT"
	endtry

	if type(char) == type("")
		" Special chars
		if char == "\<Up>"
			let result = "KEY_VALUE_UP"
		elseif char == "\<Down>"
			let result = "KEY_VALUE_DOWN"
		elseif char == "\<Left>"
			let result = "KEY_VALUE_LEFT"
		elseif char == "\<Right>"
			let result = "KEY_VALUE_RIGHT"
		elseif char == "\<Del>"
			let result = "KEY_VALUE_DELETE"
		elseif char == "\<BS>"
			let result = "KEY_VALUE_BACKSPACE"
		else
			let result = "UNKNOWN"
		endif

	elseif char == 9
		let result = "KEY_VALUE_TAB"
	elseif char == 13
		let result = "KEY_VALUE_SELECT"
	elseif char == 27
		let result = "KEY_VALUE_EXIT"
	else
		" convert to a string.
		let result = nr2char(char)
	endif

	return result
endfunction																		"}}}


" vim: ts=4 tw=4 nocin fdm=marker :
