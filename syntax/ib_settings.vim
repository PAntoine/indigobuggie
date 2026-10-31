" ---------------------------------------------------------------------------------
"      _____           _ _                ______                    _
"     (_____)         | (_)              (____  \                  (_)
"        _   ____   _ | |_  ____  ___     ____)  )_   _  ____  ____ _  ____
"       | | |  _ \ / || | |/ _  |/ _ \   |  __  (| | | |/ _  |/ _  | |/ _  )
"      _| |_| | | ( (_| | ( ( | | |_| |  | |__)  ) |_| ( ( | ( ( | | ( (/ /
"     (_____)_| |_|\____|_|\_|| |\___/   |______/ \____|\_|| |\_|| |_|\____)
"                         (_____|                      (_____(_____|
"
"  Name  : ib_settings.vim
"  Desc  : This file is the settings syntax.
"
"  Author: Peter Antoine
"  Date  : 2026-10-17
" ---------------------------------------------------------------------------------
"                      Copyright (c) 2026 Peter Antoine
"                             All rights Reserved.
"                       Released Under the MIT Licence
" ---------------------------------------------------------------------------------

" Quit when a syntax file was already loaded
if exists("b:current_syntax")
	finish
endif

let b:current_syntax = "ib_settings"

" Source Tree Window
syn region	ibTreeHeader	start="\[" end="\]$"		keepend contains=@NoSpell
hi link		ibTreeHeader	Identifier

syn region	ibDirLine			start="^\s\{2,}[▸▾>v]" end="$"		keepend contains=ibMarker,ibDirName
syn match	ibMarker			"▸ "								contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"▾ "								contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"> "								contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"v "								contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibDirName			"[0-9A-Za-z \._#\-]\+"				contained containedin=ibDirLine nextgroup=ibSettingType contains=@NoSpell
syn match	ibSettingType		"\[[pu]\]"								contained contains=@NoSpell

" Tree Line
" The status can repeat at the end for different SCMs.
syn region	ibTreeLine		start="^\s*[0-9 A-Za-z\._#\-:]" end="$"	keepend contains=ibMarker,ibFileName,ibStateNew,ibStateDeleted,ibStateChanged,@NoSpell
syn match	ibFileName		"^\s*[0-9A-Za-z \._#\-]\+"				contained nextgroup=ibSettingType contains=@NoSpell
syn match	ibSettingType	"\[[pu]\]"									contained contains=@NoSpell


hi link ibDirLine			Normal
hi link ibTreeLine			Normal
hi link ibMarker			Comment
hi link	ibFileName			String
hi link	ibDirName			String
hi link	ibSettingType		Type
