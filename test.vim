function! GuiTabLabel()
	  let label = ''
	  let bufnrlist = tabpagebuflist(v:lnum)

	  " Add '+' if one of the buffers in the tab page is modified
	  for bufnr in bufnrlist
	    if getbufvar(bufnr, "&modified")
	      let label = '+'
	      break
	    endif
	  endfor

	  " Append the number of windows in the tab page if more than one
	  let wincount = tabpagewinnr(v:lnum, '$')
	  if wincount > 1
	    let label .= wincount
	  endif
	  if label != ''
	    let label .= ' '
	  endif

	  " Append the buffer name
	  return label . bufname(bufnrlist[tabpagewinnr(v:lnum) - 1])
	endfunction

	function! MyTabLine()
	  let s = ''
	  for i in range(tabpagenr('$'))
	    " select the highlighting
	    if i + 1 == tabpagenr()
	      let s .= '%#TabLineSel#'
	    else
	      let s .= '%#TabLine#'
	    endif

		if gettabvar(i, "__tab_id__") != '' 
			let s .= '[ ' . gettabvar(i, "__tab_id__") . ' ]'
		else
			" set the tab page number (for mouse clicks)
			let s .= '%' . (i + 1) . 'T'

			" the label is made by MyTabLabel()
			let s .= ' %{MyTabLabel(' . (i + 1) . ')} '
		endif

		endfor

	  " after the last tab fill with TabLineFill and reset tab page nr
	  let s .= '%#TabLineFill#%T'

	  " right-align the label to close the current tab page
	  if tabpagenr('$') > 1
	    let s .= '%=%#TabLine#%999Xclose'
	  endif

	  return s
	endfunction

let g:weee = "GuiTabLabel"	

echo  call(g:weee, [])

let g:fred="GuiTabLabel"
set guitablabel=%{call(g:fred,[])}

echo call(function(g:fred),[])
