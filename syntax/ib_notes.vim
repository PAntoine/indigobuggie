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

let b:current_syntax = "ib_notes"
syn region	ibTreeHeader	start="\[" end="\]$"		keepend
hi link ibTreeHeader	Identifier

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

" vim: ts=4 tw=4 fdm=marker :
