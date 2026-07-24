// Custom Typst overrides for pandoc-generated documents.
// Included via pandoc --include-in-header.
// Mirrors the DOCX reference.docx styling.

// ── Colors (from reference.docx) ────────────────────────────────────────────
#let heading-color = rgb("#0F4761")
#let table-header-bg = rgb("#D6E4F0")
#let table-header-fg = rgb("#1F3864")
#let table-border = rgb("#BFBFBF")

// ── Headings ────────────────────────────────────────────────────────────────
#show heading.where(level: 1): set text(size: 20pt, fill: heading-color)
#show heading.where(level: 1): set align(center)
#show heading.where(level: 2): set text(size: 16pt, fill: heading-color)
#show heading.where(level: 2): set align(center)
#show heading.where(level: 3): set text(size: 14pt, fill: heading-color)
#show heading.where(level: 4): set text(size: 12pt, fill: heading-color, style: "italic")
#set heading(bookmarked: true)

// ── Tables: full width, compact text, styled header row ─────────────────────
#show figure.where(kind: table): set align(left)
#show figure.where(kind: table): set text(size: 9pt)
#show figure.where(kind: table): set block(breakable: true, width: 100%)
#set table(
  inset: (x: 6pt, y: 4pt),
  stroke: 0.5pt + table-border,
)
#show table.cell.where(y: 0): set text(weight: "bold", fill: table-header-fg)
#show table.cell.where(y: 0): it => {
  set text(weight: "bold", fill: table-header-fg)
  rect(fill: table-header-bg, inset: (x: 6pt, y: 4pt), width: 100%, it.body)
}

// ── Links ───────────────────────────────────────────────────────────────────
#show link: set text(fill: rgb("#4F81BD"))
