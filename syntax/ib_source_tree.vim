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
"    desc: This is the syntax file for the source tree feature.
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

let b:current_syntax = "ib_source_tree"

" Source Tree Window
syn region	ibTreeHeader	start="^commit:" end="$"		keepend contains=ibHCommit,ibBranchName,ibLogHash
syn keyword	ibHCommit		contained commit

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

" vim: ts=4 tw=4 fdm=marker :
