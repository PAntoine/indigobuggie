"---------------------------------------------------------------------------------
"     _____           _ _                ______                    _
"    (_____)         | (_)              (____  \                  (_)
"       _   ____   _ | |_  ____  ___     ____)  )_   _  ____  ____ _  ____
"      | | |  _ \ / || | |/ _  |/ _ \   |  __  (| | | |/ _  |/ _  | |/ _  )
"     _| |_| | | ( (_| | ( ( | | |_| |  | |__)  ) |_| ( ( | ( ( | | ( (/ /
"    (_____)_| |_|\____|_|\_|| |\___/   |______/ \____|\_|| |\_|| |_|\____)
"                        (_____|                      (_____(_____|
"
"    file: indigobuggie
"    desc: This is the syntax file for the indigobuggie files.
"
"  author: peter
"    date: 12/11/2018
"---------------------------------------------------------------------------------
"                     Copyright (c) 2018 Peter Antoine
"                           All rights Reserved.
"                      Released Under the MIT Licence
"---------------------------------------------------------------------------------

" Quit when a syntax file was already loaded
if exists("b:current_syntax")
	finish
endif

let b:current_syntax = "ib_timekeeper"
syn region	ibTreeHeader	start="\[" end="\]$"		keepend
hi link ibTreeHeader	Identifier

" TimeKeeper Line
" The format is simple:
" {spaces}[alpha]:DDDDDDDD [text]\+$
syn region	ibTimeKeeperLine		start="^\s*[0-9A-Za-z]\+ \d\{4}:\d\{2}:\d\{2}$" end="$"	keepend contains=ibTitle,ibDays,ibHours,ibMinutes,@NoSpell
syn match ibTitle		"[0-9A-Za-z]\+"			contained nextgroup=ibDays
syn match ibDays		"\d\{8}"				contained nextgroup=ibHours
syn match ibHours		"\d\{2}"				contained nextgroup=ibMinutes
syn match ibMinutes		"\d\{2}"				contained nextgroup=ibDescription

hi 		ibTitle		term=bold ctermfg=Green		guifg=Green
hi 		ibDays		term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibHours		term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibMinutes	term=bold ctermfg=Yellow	guifg=Yellow

" vim: ts=4 tw=4 fdm=marker :
