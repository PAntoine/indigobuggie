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
"    desc: This is the syntax file for the history tree.
"
"  author: peter
"    date: 12/11/2018
"---------------------------------------------------------------------------------
"                     Copyright (c) 2022 Peter Antoine
"                           All rights Reserved.
"                      Released Under the MIT Licence
"---------------------------------------------------------------------------------

" Quit when a syntax file was already loaded
if exists("b:current_syntax")
	finish
endif

let b:current_syntax = "ib_history_tree"

" Source Tree Window
syn region	ibTreeHeader	start="\[" end="\]$"	keepend
hi link ibTreeHeader	Identifier


syn region	ibDirLine			start="^\s\{2,}[▸▾>v]" end="$"		keepend contains=ibMarker,ibDirName,ibStateLink,ibStateBadLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged,@NoSpell
syn match	ibMarker			"▸ "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"▾ "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"> "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"v "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibDirName			"[0-9A-Za-z\._#\-]\+"	contained containedin=ibDirLine nextgroup=ibStateLink,ibStateBadLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateLink			" [l]"					contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateBadLink		" [łB]"					contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibDirStateNew		" +"					contained containedin=ibDirLine
syn match 	ibDirStateDeleted	" [✗x]"					contained containedin=ibDirLine
syn match 	ibDirStateChanged	" [±~]"					contained containedin=ibDirLine

" Tree Line
" [open marker or space] 'file/object name' {special marker} {ASCII char + state marker + ' '}
" The status can epeat at the end for different SCMs.
syn region	ibTreeLine		start="^\s*[0-9 A-Za-z\._#\-:]" end="$"	keepend contains=ibMarker,ibFileName,ibStateNew,ibStateDeleted,ibStateChanged,@NoSpell
syn match	ibFileName		"^\s*[0-9A-Za-z\._#\-]\+"	contained nextgroup=ibStateNew,ibStateDeleted,ibStateChanged contains=@NoSpell
syn match 	ibStateNew		"\s[+]"				contained containedin=ibTreeLine
syn match 	ibStateDeleted	"\s[✗x]"			contained containedin=ibTreeLine
syn match 	ibStateChanged	"\s[±~]"			contained containedin=ibTreeLine

"Header lines
syn region	ibVersionLine	start="^V" end="$"	keepend
syn match	ibVersionDetails	"[0-9A-Za-z\._#\-]\+"	contains=@NoSpell
syn match	ibVersionHead		"Version:"				nextgroup=ibVersionDetails keepend

syn region	ibDateLine 			start="^D" end="$"	keepend
syn match	ibDateDetails		"\d\d\d\d-\d\d-\d\d"	contained containedin=ibDateLine
syn match	ibDateHead			"Date   : "			contained containedin=ibDateLine nextgroup=ibDateDetails keepend

syn region	ibAuthorLine 		start="^A" end="$"	keepend
syn match	ibAuthorDetails		"[0-9A-Za-z\._#\-]\+"		contained containedin=ibAuthorLine
syn match	ibAuthorHead		"Author : "					contained containedin=ibAuthorLine nextgroup=ibAuthorDetails

hi 		ibID		term=bold ctermfg=Green		guifg=Green
hi 		ibSpacer	term=bold ctermfg=White		guifg=White
hi 		ibDate		term=bold ctermfg=Yellow	guifg=Yellow
hi link ibDescription Comment

hi link ibDirLine			Normal
hi link ibTreeLine			Normal
hi link ibMarker			Normal
hi link	ibDirName			String
hi link	ibFileName			Normal
hi 		ibVersionHead		term=bold ctermfg=Grey		guifg=Grey
hi 		ibVersionDetails    term=bold ctermfg=LightBlue		guifg=LightBlue
hi 		ibDateHead		    term=bold ctermfg=Grey		guifg=Grey
hi 		ibDateDetails	    term=bold ctermfg=LightBlue		guifg=LightBlue
hi 		ibAuthorHead	    term=bold ctermfg=Grey		guifg=Grey
hi 		ibAuthorDetails     term=bold ctermfg=LightBlue	guifg=LightBlue
hi 		ibStateNew			term=bold ctermfg=Green		guifg=Green
hi 		ibStateDeleted		term=bold ctermfg=Red		guifg=Red
hi 		ibStateChanged		term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibDirStateNew		term=bold ctermfg=Green		guifg=Green
hi 		ibDirStateDeleted	term=bold ctermfg=Red		guifg=Red
hi 		ibDirStateChanged	term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibStateAdded		term=bold ctermfg=Green		guifg=Green
hi 		ibStateLink			term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibStateBadLink		term=bold ctermfg=Red		guifg=Red
hi link	ibStateSubRepo		Comment
hi link	ibStateSame			String

" vim: ts=4 tw=4 fdm=marker :
