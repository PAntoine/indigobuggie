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

let b:current_syntax = "ib_my_task"
syn region	ibTreeHeader	start="\[" end="\]$"		keepend
hi link ibTreeHeader	Identifier

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
