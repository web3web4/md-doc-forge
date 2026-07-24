--- docx-table-autofit.lua
--- Pandoc Lua filter: ensure tables span full page width.
---
--- For Typst (PDF): assign equal fractional widths (1/n per column).
---   Typst uses these percentages relative to the container width.
---
--- For DOCX: reset widths to ColWidthDefault so pandoc emits tblW=auto
---   without tblLayout=fixed. A Python post-processor then patches
---   tblW to 100% in the XML.

function Table(tbl)
  local ncols = #tbl.colspecs
  if ncols == 0 then return tbl end

  if FORMAT == "typst" then
    local w = 1.0 / ncols
    for i = 1, ncols do
      tbl.colspecs[i] = { tbl.colspecs[i][1], w }
    end
  else
    for i = 1, ncols do
      tbl.colspecs[i] = { tbl.colspecs[i][1], pandoc.ColWidthDefault }
    end
  end
  return tbl
end
