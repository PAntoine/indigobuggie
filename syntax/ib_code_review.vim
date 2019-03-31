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

let b:current_syntax = "ib_codereview"
syn region	ibTreeHeader	start="\[" end="\]$"		keepend
hi link ibTreeHeader	Identifier


" review type
syn region	ibReviewType	start="^\s\s[▸▾>v]\s" end="[0-9A-Za-z]\+\n"		keepend contains=ibReviewTypeName,ibMarker
syn match	ibMarker		"\s*[▸▾>v] "			contained nextgroup=ibReviewTypeName
syn match	ibReviewTypeName	"[0-9A-Za-z ]\+"	contained

syn region	ibReviewTitle	start="^    [▸▾>v]\s" end="\]\n"		keepend contains=ibReviewTitle,ibReviewMarker,ibStateChanged,ibStateDeleted,ibStateNew,ibReviewVoteCount containedin=ibReviewTitle
syn match	ibReviewMarker		"\s*[▸▾>v] "		contained nextgroup=ibReviewTypeName
syn match	ibReviewTitleName	"[0-9A-Za-z ]\+"	contained nextgroup=ibStateChanged,ibStateDeleted,ibStateNew
syn match 	ibStateNew			"[+]\s"				contained nextgroup=ibReviewVoteCount
syn match 	ibStateDeleted		"[✗x]\s"			contained nextgroup=ibReviewVoteCount
syn match 	ibStateChanged		"[±~]\s"			contained nextgroup=ibReviewVoteCount
syn match	ibReviewVoteCount 	"\[[0-9]\+\]"		contained

syn region	ibReviewChange	start="^      [▸▾>v]\s" end="\d \[[0-9]\+\]\n"		keepend contains=ibReviewChangeMarker,ibReviewChangeTitle,ibReviewUpVotes,ibReviewDownVotes,ibReviewBar,ibReviewChangeVoteCount
syn match	ibReviewChangeMarker	"\s*[▸▾>v] "			contained nextgroup=ibReviewChangeTitle
syn match	ibReviewChangeTitle		"[0-9A-Za-z_\-:]\+ "	contained nextgroup=ibReviewUpVotes
syn match	ibReviewUpVotes			"[0-9]\+"				contained nextgroup=inReviewBar
syn match	ibReviewBar				"/"						contained nextgroup=inReviewDownVotes
syn match	ibReviewDownVotes		"[0-9]\+"				contained nextgroup=ibReviewChangeVoteCount
syn match	ibReviewChangeVoteCount	" \[[0-9]\+\]"			contained

syn region	ibReviewFile	start="^        [▸▾>v]\s" end="\[[0-9]\+\]\n"		keepend contains=ibReviewFileMarker,ibReviewFileName,ibReviewFileVoteCount
syn match	ibReviewFileMarker		"^        [▸▾>v] "				contained nextgroup=ibReviewFileName
syn match	ibReviewFileName		"[A-Za-z][0-9A-Za-z\\//:._ ]\+"	contained nextgroup=ibReviewFileVoteCount
syn match	ibReviewFileVoteCount	"\[[0-9]\+\]"					contained

syn region	ibReviewHunk	start="^          [▸▾>v]\s" end="\[[0-9]\+\]\n"		keepend contains=ibReviewHunkMarker,ibReviewFileName
syn match	ibReviewHunkMarker		"^          [▸▾>v] "	contained nextgroup=ibReviewHunkLine
syn match	ibReviewHunkLine		"line:\s\+\d\+ "		contained nextgroup=ibReviewHunkDelete,ibReviewHunkAdd
syn match	ibReviewHunkAdd			"+"						contained nextgroup=ibReviewHunkDelete,ibReviewHunkAdd,ibReviewHunkVoteCount
syn match	ibReviewHunkDelete		"-"						contained nextgroup=ibReviewHunkDelete,ibReviewHunkVoteCount
syn match	ibReviewHunkVoteCount	" \[[0-9]\+\]"			contained

syn region	ibReviewComment	start="^            c:" end="\n"		keepend contains=ibReviewCommentMarker,ibReviewCommentTitle
syn match	ibReviewCommentMarker	"^            c:"			contained nextgroup=ibReviewCommentTitle
syn match	ibReviewCommentTitle	" [0-9A-Za-z.]\+"			contained

" colours
hi link ibMarker				String
hi link ibReviewMarker			String
hi link ibReviewChangeMarker	String
hi link ibReviewFileMarker		String
hi link ibReviewHunkMarker		String
hi link ibReviewCommentMarker	String
hi link	ibReviewHunkLine		Comment
hi link	ibReviewTypeName		Comment
hi link	ibReviewChangeTitle		Comment
hi link	ibReviewFileName		Comment
hi		ibReviewCommentTitle	term=bold ctermfg=Grey		guifg=Grey
hi 		ibReviewHunkDelete		term=bold ctermfg=Red		guifg=Red
hi 		ibReviewHunkAdd			term=bold ctermfg=Green		guifg=Green
hi 		ibReviewHunkVoteCount	term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibReviewVoteCount		term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibStateNew				term=bold ctermfg=Green		guifg=Green
hi 		ibStateDeleted			term=bold ctermfg=Red		guifg=Red
hi 		ibStateChanged			term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibReviewUpVotes			term=bold ctermfg=Green		guifg=Green
hi 		ibReviewDownVotes		term=bold ctermfg=Red		guifg=Red
hi 		ibReviewChangeVoteCount	term=bold ctermfg=Yellow	guifg=Yellow
hi 		ibReviewFileVoteCount	term=bold ctermfg=Yellow	guifg=Yellow

" vim: ts=4 tw=4 fdm=marker :
