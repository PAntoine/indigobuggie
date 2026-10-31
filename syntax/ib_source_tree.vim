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
syn region	ibTreeHeader	start="\[" end="\]$"		keepend contains=@NoSpell
hi link		ibTreeHeader	Identifier

syn region	ibDirLine			start="^\s\{2,}[▸▾>v]" end="$"		keepend contains=ibMarker,ibDirName,ibStateSubRepo,ibStateSubGit,ibStateModule,ibStateLink,ibStateBadLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged,@NoSpell
syn match	ibMarker			"▸ "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"▾ "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"> "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibMarker			"v "					contained containedin=ibDirLine nextgroup=ibDirName
syn match	ibDirName			"[0-9A-Za-z\._#\-]\+"	contained containedin=ibDirLine nextgroup=ibStateModule,ibStateSubRepo,ibStateLink,ibStateBadLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateSubRepo		" \[\a\{1,2}\]"			contained containedin=ibDirLine nextgroup=ibStateLink,ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateLink			" [l]"					contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibStateBadLink		" [łB]"					contained containedin=ibDirLine nextgroup=ibDirStateNew,ibDirStateDeleted,ibDirStateChanged contains=@NoSpell
syn match 	ibDirStateNew		" +"					contained containedin=ibDirLine
syn match 	ibDirStateDeleted	" [✗x]"					contained containedin=ibDirLine
syn match 	ibDirStateChanged	" [±~]"					contained containedin=ibDirLine

" Tree Line
" The status can repeat at the end for different SCMs.
syn region	ibTreeLine		start="^\s*[0-9 A-Za-z\._#\-:]" end="$"	keepend contains=ibMarker,ibFileName,ibStateNew,ibStateDeleted,ibStateChanged,@NoSpell
syn match	ibFileName		"^\s*[0-9A-Za-z\._#\-]\+"	contained nextgroup=ibStateNew,ibStateDeleted,ibStateChanged contains=@NoSpell
syn match 	ibStateNew		"\s\a\{1,2}[+]"				contained containedin=ibTreeLine
syn match 	ibStateDeleted	"\s\a\{1,2}[✗x]"			contained containedin=ibTreeLine
syn match 	ibStateChanged	"\s\a\{1,2}[±~]"			contained containedin=ibTreeLine

" [open marker or space] 'file/object name' {special marker} {ASCII char + state marker + ' '}
syn region	ibShownTreeLine	start="^\s*\*[0-9 A-Za-z\._#\-:]" end="$"	keepend contains=ibMarker,ibShownMarker,ibShownFileName,ibStateNew,ibStateDeleted,ibStateChanged,@NoSpell
syn match   ibShownMarker   "^\s*\*"                    contained nextgroup=ibShownFileName
syn match	ibShownFileName	"[0-9A-Za-z\._#\-]\+"	    contained nextgroup=ibStateNew,ibStateDeleted,ibStateChanged contains=@NoSpell
syn match 	ibHideMarker    "\s\a\{1,2}[+]"				contained containedin=ibShownFileName
syn match 	ibStateNew		"\s\a\{1,2}[+]"				contained containedin=ibTreeLine
syn match 	ibStateDeleted	"\s\a\{1,2}[✗x]"			contained containedin=ibTreeLine
syn match 	ibStateChanged	"\s\a\{1,2}[±~]"			contained containedin=ibTreeLine

" History Line
" The format is simple:
" {spaces}[alpha]:DDDDDDDD [text]\+$
syn region	ibHistoryLine start="^\s\{2,}[0-9A-Za-z]\{6,}:\d\{8}\s[0-9A-Za-z].\+" end="$" keepend contains=ibID,ibSpacer,ibDate,ibDescription,@NoSpell
syn match ibID			"\s\{2,}[0-9A-Fa-f]\{6,}"	contained nextgroup=ibSpacer		contains=@NoSpell
syn match ibSpacer		":"							contained nextgroup=ibDate			contains=@NoSpell
syn match ibDate		"\d\{8}"					contained nextgroup=ibDescription	contains=@NoSpell
syn match ibDescription "\s[0-9A-Za-z].\+"			contained contains=@NoSpell

" Current Branches
" The first format is simple:
"   [alpha]\+: [alpha]\+  This is repo_name then current branch
syn region	ibBranches start="^\s\{2,}[▸▾>v]\s[0-9A-Za-z_-]\+:" end="$"		keepend contains=ibBMarker,ibBranchName,@NoSpell
syn match	ibBMarker			"▸ "					contained containedin=ibBranches nextgroup=ibRepoName
syn match	ibBMarker			"▾ "					contained containedin=ibBranches nextgroup=ibRepoName
syn match	ibBMarker			"> "					contained containedin=ibBranches nextgroup=ibRepoName
syn match	ibBMarker			"v "					contained containedin=ibBranches nextgroup=ibRepoName
syn match	ibRepoName			"[0-9A-Za-z\._#\-]\+"	contained containedin=ibBranches nextgroup=ibRepoSep contains=@NoSpell
syn match	ibRepoSep			": "					contained containedin=ibBranches nextgroup=ibBranchName
syn match	ibBranchName "[0-9A-Za-z\._#\-]\+"			contained containedin=ibBranches contains=@NoSpell

" Remotes Line
" The format is simple:
" {spaces}HHHHHHHH [ O] [text]\+$
syn region	ibRemoteLines start="^\s\{2,}[0-9A-Fa-f]\{6,} [ \-\*] [0-9A-Za-z\._#\-]\+" end="$" keepend contains=ibID,ibStatus,ibRemoteStatus,ibRemoteNone,ibRemoteChanged,ibRemoteName
syn match ibID				"\s\+[0-9A-Fa-f]\{6,}"	contained containedin=ibRemoteLines nextgroup=ibRemoteStatus,ibRemoteNone,ibRemoteChanged contains=@NoSpell
syn match ibRemoteStatus	"  "					contained containedin=ibRemoteLines nextgroup=ibRemoteName contains=@NoSpell
syn match ibRemoteChanged	" \*"					contained containedin=ibRemoteLines nextgroup=ibRemoteName contains=@NoSpell
syn match ibRemoteNone		" -"					contained containedin=ibRemoteLines nextgroup=ibRemoteName contains=@NoSpell
syn match ibRemoteName		"[0-9A-Za-z\._#\-]\+"	contained containedin=ibRemoteLines contains=@NoSpell

" Define the colours.
hi 		ibID				term=bold ctermfg=Green		guifg=Green
hi 		ibSpacer			term=bold ctermfg=White		guifg=White
hi 		ibDate				term=bold ctermfg=Yellow	guifg=Yellow
hi link ibDescription		Comment
hi link ibDirLine			Normal
hi link ibTreeLine			Normal
hi link ibMarker			Normal
hi link	ibDirName			String
hi link	ibFileName			Normal
hi      ibShownMarker       term=bold ctermfg=Black  	guifg=bg
hi      ibShownFileName	    term=bold ctermfg=Yellow	guifg=Red
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
hi link	ibHideMarker        String
hi link ibBranches			Normal
hi link	ibRepoName			Directory
hi link	ibRepoSep			Normal
hi link ibBMarker			Normal
hi      ibBranchName	    term=bold ctermfg=Yellow	guifg=Red
hi link ibRemoteNone		Comment
hi link ibRemoteChanged		Removed
hi link ibRemoteName		String

" vim: ts=4 tw=4 fdm=marker :
