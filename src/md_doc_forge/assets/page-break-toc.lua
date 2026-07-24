--- page-break-toc.lua
--- Pandoc Lua filter:
---   1. Convert horizontal rules (---) to page breaks.
---      The FIRST --- also inserts a Table of Contents, then another page break.
---   2. Resolve image paths to absolute for Typst output.
---      Typst can't use pandoc's --resource-path, so we resolve paths here.

local hr_count = 0
local cwd = pandoc.system.get_working_directory()

--- Resolve relative image paths to absolute for Typst output.
--- Typst runs from a temp directory so it can't use pandoc's --resource-path.
--- We resolve paths against resource_path dirs, prefixed with cwd if relative.
function Image(img)
  if not FORMAT:match 'typst' then return nil end
  -- Skip already-absolute paths and URLs
  if img.src:sub(1, 1) == '/' then return nil end
  if img.src:match('^https?://') then return nil end

  for _, dir in ipairs(PANDOC_STATE.resource_path) do
    -- Make dir absolute if it isn't already
    local abs_dir = dir
    if dir:sub(1, 1) ~= '/' then
      abs_dir = cwd .. '/' .. dir
    end
    local candidate = abs_dir .. '/' .. img.src
    local f = io.open(candidate, 'r')
    if f then
      f:close()
      img.src = candidate
      return img
    end
  end
  return nil
end

function HorizontalRule()
  hr_count = hr_count + 1
  local blocks = {}

  if FORMAT:match 'typst' then
    table.insert(blocks, pandoc.RawBlock('typst', '#pagebreak()'))
    if hr_count == 1 then
      table.insert(blocks, pandoc.RawBlock('typst',
        '#outline(title: "Table of Contents", indent: auto, depth: 2)'))
      table.insert(blocks, pandoc.RawBlock('typst', '#pagebreak()'))
    end

  elseif FORMAT:match 'docx' then
    table.insert(blocks, pandoc.RawBlock('openxml',
      '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'))
    if hr_count == 1 then
      table.insert(blocks, pandoc.RawBlock('openxml', table.concat({
        '<w:sdt>',
        '  <w:sdtPr>',
        '    <w:docPartObj>',
        '      <w:docPartGallery w:val="Table of Contents"/>',
        '      <w:docPartUnique/>',
        '    </w:docPartObj>',
        '  </w:sdtPr>',
        '  <w:sdtContent>',
        '    <w:p>',
        '      <w:pPr><w:pStyle w:val="TOCHeading"/></w:pPr>',
        '      <w:r><w:t xml:space="preserve">Table of Contents</w:t></w:r>',
        '    </w:p>',
        '    <w:p>',
        '      <w:r>',
        '        <w:fldChar w:fldCharType="begin" w:dirty="true"/>',
        '        <w:instrText xml:space="preserve">TOC \\o "1-2" \\h \\z \\u</w:instrText>',
        '        <w:fldChar w:fldCharType="separate"/>',
        '        <w:fldChar w:fldCharType="end"/>',
        '      </w:r>',
        '    </w:p>',
        '  </w:sdtContent>',
        '</w:sdt>',
      }, '\n')))
      table.insert(blocks, pandoc.RawBlock('openxml',
        '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'))
    end

  elseif FORMAT:match 'odt' or FORMAT:match 'opendocument' then
    table.insert(blocks, pandoc.RawBlock('opendocument',
      '<text:p text:style-name="Horizontal_20_Line"/>'))

  else
    -- Unknown format: keep the original rule
    return nil
  end

  return blocks
end
