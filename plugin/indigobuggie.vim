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
if !exists("g:IB_project_config")
	let g:IB_project_config = { 'specific_file': '',
							\	'auto_create': 0 }
endif

if !exists("g:IB_code_review_config")
	let g:IB_code_review_config = {	'default': 'LocalCodeReviews',
								\	'engines': {'LocalCodeReviews': { 'root_directory' : '.' }}
								\ }
endif

if !exists("g:IB_my_tasks_config")
	let g:IB_my_tasks_config = { 'auto_tasks': 1, 'markers': ['TODO', 'FIXME', 'TECH_DEBT', 'HACK'] }
endif

if !exists("g:IB_timekeeper_config")
	let g:IB_timekeeper_config = { 'tracking': 1, 'use_repo': 1, 'default_project': 'default' }
endif

if !exists("g:IB_source_tree_config")
	let g:IB_source_tree_config = { 'ignore_suffixes': ['swp', 'swo', 'swn', 'pyc', 'o'],
								\	'ignore_directories': ['.indigobuggie', '.git' ],
								\	'active_scm': '' }
endif

if !exists("g:IB_scm_config")
	let g:IB_scm_config = { 'number_history_items': 10,
						\	'active_scm': '' }
endif


if !exists("g:IB_enabled_features")
	" But default we will turn on all the features.
	let g:IB_enabled_features = [ {'name': 'ProjectFeature', 	'loadable': s:LOAD_AUTOMATICALLY, 	'selectable': 0,	'config': g:IB_project_config },
								\ {'name': 'SourceTreeFeature', 'loadable': s:LOAD_ON_TAB_OPEN, 	'selectable': 1,	'config': g:IB_source_tree_config },
								\ {'name': 'NotesFeature', 		'loadable': s:LOAD_ON_TAB_OPEN, 	'selectable': 1,	'config': {} },
								\ {'name': 'SCMFeature', 		'loadable': s:LOAD_ON_TAB_OPEN,		'selectable': 0,	'config': g:IB_scm_config},
								\ {'name': 'CodeReviewFeature',	'loadable': s:LOAD_ON_TAB_OPEN, 	'selectable': 1, 	'config': g:IB_code_review_config},
								\ {'name': 'TimeKeeperFeature',	'loadable': s:LOAD_ON_TAB_OPEN, 	'selectable': 1,	'config': g:IB_timekeeper_config},
								\ {'name': 'MyTasksFeature',	'loadable': s:LOAD_ON_TAB_OPEN, 	'selectable': 1,	'config': g:IB_my_tasks_config }]
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
" FUNCTION: IB_Initialise 														{{{
"
" This function will initialise the plugin. This is called once and will call
" the initialise for the different features.
"
" vars:
"	none
"
" returns:
"	nothing.
"
function IB_Initialise()

	for item in g:IB_enabled_features
		if item.loadable == s:LOAD_AUTOMATICALLY
			" 2 = auto initialise.
			call IB_InitialiseFeature(item, 0)
		endif
	endfor
endfunction																		"}}}
" FUNCTION: IB_InitialiseFeature												{{{
"
" This function will initialise the plugin. This is called once and will call
" the initialise for the different features.
"
" vars:
"	item	The item for the feature that to be initialised.
"
" returns:
"	nothing.
"
function IB_InitialiseFeature(item, tab_number)
	if a:item.loadable > s:LOAD_DO_NOT
		if a:tab_number == 0
			py indigobuggie.Initialise(vim.eval('a:item.name'), None, vim.eval('a:item.config'))
		else
			let tab_id = gettabvar(a:tab_number, "__tab_id__")
			py indigobuggie.Initialise(vim.eval('a:item.name'), tab_control.getTab(int(vim.eval('tab_id'))), vim.bindeval('a:item.config'))
		endif
	endif
endfunction																		"}}}	
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

	py tab_control.addTab(vim.eval('path'))

	for item in g:IB_enabled_features
		if item.loadable == s:LOAD_ON_TAB_OPEN
			" 2 = auto initialise.
			call IB_InitialiseFeature(item, tabpagenr())
		endif
	endfor

	for item in g:IB_enabled_features
		if item.selectable == 1
			" select the first (and default) feature.
			call IB_SelectFeature(item, tabpagenr())
			break
		endif
	endfor

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

" vim: ts=4 tw=4 nocin fdm=marker :
