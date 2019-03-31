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

let b:current_syntax = "ib"

" Source Tree Window
syn region	ibTreeHeader	start="\[" end="\]$"		keepend
hi link ibTreeHeader	Identifier

hi link ibHCommit			Identifier

syn region	ibDirLine			start="^\s\{2,}[▸▾>v]" end="$"		keepend contains=ibMarker,ibDirName,ibStateSubRepo,ibStateSubGit,ibStateModule,ibStateLink,ibStateBadLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged,@NoSpell
syn match	ibMarker			"▸ "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"▾ "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"> "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"v "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibDirName			"[0-9A-Za-z\._#\-]\+"	contained containedin=ibDirLine nextgroup=ibStateModule,ibStateSubGit,ibStateSubRepo,ibStateLink,ibStateBadLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateSubRepo		" \[\a\{1,2}\]"			contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateLink			" [l]"					contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateBadLink		" [łB]"					contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibDirStateNew		" +"					contained containedin=ibDirLine
syn match 	ibDirStateDeleted	" [✗x]"					contained containedin=ibDirLine
syn match 	ibDirStateChanged	" [±~]"					contained containedin=ibDirLine

" Tree Line
" [open marker or space] 'file/object name' {special marker} {ASCII char + state marker + ' '}
" The status can epeat at the end for different SCMs.
syn region	ibTreeLine		start="^\s*[0-9 A-Za-z\._#\-:]" end="$"	keepend contains=ibMarker,ibFileName,@NoSpell
syn match 	ibStateNew		" \a\{1,2}[+]"			contained containedin=ibTreeLine,ibDirLine nextgroup=ibFileName
syn match 	ibStateDeleted	" \a\{1,2}[✗x]"			contained containedin=ibTreeLine,ibDirLine nextgroup=ibFileName
syn match 	ibStateChanged	" \a\{1,2}[±~]"			contained containedin=ibTreeLine,ibDirLine nextgroup=ibFileName
syn match	ibFileName		"[0-9A-Za-z\._#\-]\+"	contained containedin=ibTreeLine contains=@NoSpell

hi link ibDirLine			Normal
hi link ibTreeLine			Normal
hi link ibMarker			Normal
hi link	ibDirName			String
hi link	ibFileName			Normal
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

" History Line
" The format is simple:
" {spaces}[alpha]:DDDDDDDD [text]\+$
syn region	ibHistoryLine		start="^\s*[0-9A-Za-z]\+:\d\{8} .\+$" end="$"	keepend contains=ibID,ibSpacer,ibDate,ibDescription,@NoSpell
syn match ibID			"\s\{2,}[0-9A-Za-z]\+"	contained nextgroup=ibSpacer
syn match ibSpacer		":"						contained nextgroup=ibDate
syn match ibDate		"\d\{8}"				contained nextgroup=ibDescription
syn match ibDescription "\s[0-9A-Za-z].\+"		contained

hi 		ibID		term=bold ctermfg=Green		guifg=Green
hi 		ibSpacer	term=bold ctermfg=White		guifg=White
hi 		ibDate		term=bold ctermfg=Yellow	guifg=Yellow
hi link ibDescription Comment

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

" Note line
" This is a hack - the dir line above matches but it does not want to take a space
" but this will take a string so, it works enough. I don't want to have to load a
" different syntax file for each feature.
syn region	ibNoteLine	start="^\s*[▸▾>v]" end="$"	keepend contains=ibNoteMarker,ibNoteName
syn match	ibNoteMarker	"▸ "				contained containedin=ibNoteLine nextgroup=ibNoteName
syn match	ibNoteMarker	"▾ "				contained containedin=ibNoteLine nextgroup=ibNoteName
syn match	ibNoteMarker	"> "				contained containedin=ibNoteLine nextgroup=ibNoteName
syn match	ibNoteMarker	"v "				contained containedin=ibNoteLine nextgroup=ibNoteName
syn match	ibNoteName		"[0-9A-Za-z\s]\+"	contained containedin=ibNoteLine

hi 			ibNoteMarker	term=bold ctermfg=Green		guifg=Green
hi link		ibNoteName		String

" My Task Feature
syn region	ibTaskLine	start="^\s*[▸▾>v] [☐☑☒+x ]" end="$"	keepend contains=ibTaskMarker,ibTaskName,ibGoing,ibComplete,ibAbandoned
syn match	ibGoing				"☐" contained containedin=ibTaskLine nextgroup=ibTaskName
syn match	ibComplete			"☑" contained containedin=ibTaskLine nextgroup=ibTaskName
syn match	ibAbandoned			"☒" contained containedin=ibTaskLine nextgroup=ibTaskName
syn match	ibComplete			"+" contained containedin=ibTaskLine nextgroup=ibTaskName
syn match	ibAbandoned			"x" contained containedin=ibTaskLine nextgroup=ibTaskName

syn region	ibTaskItemLine	start="^\s*[☐☑☒+x-]" end="$"	keepend contains=ibTaskMarker,ibTaskName,ibGoing,ibComplete,ibAbandoned

hi 			ibGoing		term=bold ctermfg=Green		guifg=Yellow
hi 			ibComplete	term=bold ctermfg=Green		guifg=Green
hi 			ibAbandoned	term=bold ctermfg=Green		guifg=Red
hi link		ibTaskItemLine String

" vim: ts=4 tw=4 fdm=marker :
