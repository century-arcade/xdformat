# How JPZ, ipuz and Across Lite .puz map to .xd

This document goes through three other crossword formats field by field and
says what each field becomes in .xd v4.  It is meant to help decide what
belongs in the xd spec and what should be left to a converter.

> **Status, 2026-11-18.**  xd v4.0 is a draft ([xd-format-v4.md](xd-format-v4.md),
> tracked in [#24]).  Three parts of what is described here are not settled:
>
> - **Rebus, Schrödinger and linked cells** are described as draft
>   [PR #28] has them (`1=O|A`, `12345=CIGAR|PENIS`).  That PR is still in
>   review.  The text on `master` today has the older repeated-key form
>   (`1=O 1=A`) and no linked cells.
> - **`Byline`** is in open [PR #32], not yet merged.
> - **The reference parser and converters** still implement v3; the work is
>   listed in [#30].

## What each format is for

| Format | Form | Made for | Solve state in the file |
|---|---|---|---|
| **.xd** | UTF-8 text, one clue per line with its answer | A corpus: reading, grep, diff and version control across many puzzles ([spec intro](xd-format-v4.md)) | No |
| **ipuz** | JSON | Interchange between apps, for many kinds of puzzle.  Its spec lists "Facilitate editing data by hand" as a non-goal | Yes (`saved`) |
| **JPZ** | XML, usually zipped | Crossword Compiler's export for its web solving applet; the file carries the applet's settings as well as the puzzle | Yes (`solve-state`) |
| **.puz** | Binary | Across Lite's file for one puzzle and one solver's progress on it | Yes (`fill`) |

The line `A1. Sadness. ~ HEARTACHE` is the reason xd exists beside the others:
a clue and its answer can be found, compared and counted without parsing a
grid.  None of the other three stores an answer next to its clue in a form a
text tool can read.

### Sources

- **xd**: [xd-format-v4.md](xd-format-v4.md), with [PR #28] for rebus.  Section
  names below ("Grid", "Design", "xdown Formatting") are headings in that file.
- **ipuz**: specification version 2.0.2, <https://libipuz.org/ipuz-spec.html>
  (a mirror of the ipuz.org page).
- **JPZ**: the XML schema for the `rectangular-puzzle` element,
  <https://crossword.info/xml/rectangular-puzzle.xsd>, and the schema for the
  `crossword-compiler-applet` element that wraps it in a .jpz file,
  <https://crossword.info/xml/crossword-compiler-applet.xsd>, both as fetched
  on 2026-11-18.  The schemas are the only source used; how applications use
  JPZ beyond what the schema says is not covered.
- **.puz**: there is no official specification.  The description here is
  derived from the [puz.py](https://github.com/alexdej/puzpy) implementation
  (`puz.py` at commit `e0c4744`), including its extension sections.  Where
  puz.py does not interpret something, this document says so.

Unmodified copies of the ipuz specification and the JPZ puzzle schema are
being added to this repo under `doc/references/` (branch
`ipuz-spec-reference`, not yet merged).

### Categories

Each row is sorted into one of these:

| Category | Meaning |
|---|---|
| **1 Clean** | xd v4 holds it with nothing lost |
| **2 Lossy** | xd v4 can hold it, but something is lost or approximated, or it needs a convention the spec does not define |
| **3 Later** | Not in the v4 draft; an open issue proposes it |
| **3 Out** | Not in the v4 draft, and no issue proposes it |

"3 Out" is a recorded decision only for solve state and for puzzle kinds other
than crosswords, which follow from what xd is for.  For the other rows it is
this document's reading of the draft, and a row can move to "Later" by someone
opening an issue.  The rule in [#24] applies to all of them: only a change
that breaks existing files, or that a v4 parser has to understand, blocks
v4.0.  Everything additive can come after.

## The points that came up in the v4 discussion

A summary across all three formats.  The per-format tables below give the
field names and the detail.

| Topic | xd v4 | ipuz | JPZ | .puz |
|---|---|---|---|---|
| Solution | The grid ("Grid") | `solution` | `cell/@solution` | `solution` |
| Solver's progress | None.  The grid is the solution | `saved` | `cell/@solve-state`, `@solve-status` | `fill`, and `GEXT`, `RUSR`, `LTIM` |
| Solution not known | `?` in the grid, per cell | The `empty` value in `solution`, or no `solution` (unclear, see below) | `@solution` absent | `solution_state` 0x0002, whole puzzle |
| Block | `#` or `.` | `"#"`, or the `block` value | `type="block"` | `.` (`:` in a diagramless) |
| Non-existent cell | `_` | `null` | `type="void"`, or the cell omitted | None |
| Empty cell | No such thing in a solution; `?` is "not known" | `0`, or the `empty` value | A cell with no `solve-state` | `-` in `fill` |
| Rebus | Key in the grid, `Rebus: 1=HEART` | A string longer than one character | `@solution` longer than one character | `GRBS` + `RTBL` |
| Several accepted answers in a cell | `1=O\|A` ([PR #28]) | Array or per-direction value (unclear) | Not in the schema | None |
| Cells that change together | `12345=CIGAR\|PENIS` ([PR #28]) | Only as whole-grid hashes in `checksum` | None | None |
| Circle | `background: circle` | `shapebg: "circle"` | `background-shape="circle"` | `GEXT` 0x80 |
| Shading | `background: shaded` | `highlight` | A colour | None |
| Colour | Not yet ([#5]) | `color`, `colortext`, `colorborder`, `colorbar` | `background-color`, `foreground-color`, and grid-wide colours | None |
| Bars | `bar-top`, `bar-left` | `barred`, `dotted`, `dashed` on any side | `top-bar`, `left-bar` | None |
| Image in a cell | `background-image`, `background-size` | `imagebg`, `image`, `slice` | `background-picture` | None |
| Markup in clues | xdown | A subset of HTML | A subset of HTML | None |
| Notes | Undefined in a file with headings ([#26], [#4]) | `notes`, `intro` | `instructions`, `description` | `notes` |
| After-solve text | Not yet ([#18]) | `explanation` | `completion` (applet) | None |
| Other puzzle kinds | Crosswords only | Sudoku, fill, acrostic, block, answer, word search | Sudoku, coded, word search | Diagramless |
| Hidden solution | None | `checksum` | None | Scrambling |

## ipuz

Only the fields that apply to the crossword kind (`http://ipuz.org/crossword`)
are listed.

### Puzzle kinds

| ipuz | xd v4 | Category | Notes |
|---|---|---|---|
| `kind` `http://ipuz.org/crossword` | A .xd file | 1 Clean | |
| `…/crossword/crypticcrossword` | A .xd file | 2 Lossy | The grid and clues convert.  Enumerations have no field; see `enumeration` below |
| `…/crossword/arrowword`, `clueplacement: "blocks"`, `Clue.location` | None | 3 Out | Clues printed inside blocks |
| `…/crossword/logiccrossword`, `…/crossword/diagramless` | None | 2 Lossy | The solved grid can be written, but nothing in xd says the grid is meant to be hidden or unnumbered |
| `sudoku`, `fill`, `acrostic`, `block`, `answer`, `wordsearch` and their fields | None | 3 Out | xd is for crosswords ("It supports 99.99% of published crosswords") |
| `version` | None | 1 Clean | Nothing to carry |

### Metadata

xd's standard fields are Title, Author, Editor, Copyright and Date
("Metadata").  "Additional fields are allowed but will be ignored", so any
other value can be carried under a name of the converter's choosing; those
rows are "2 Lossy" because the name is a convention, not part of the spec.

| ipuz | xd v4 | Category | Notes |
|---|---|---|---|
| `title` | `Title` | 1 Clean | HTML converts to xdown; see "Markup" below |
| `author` | `Author` | 1 Clean | A credit that is more than a name ("Puzzle by X, clues by Y") belongs in `Byline` ([#11], [PR #32]); ipuz makes no such distinction |
| `editor` | `Editor` | 1 Clean | |
| `copyright` | `Copyright` | 1 Clean | |
| `date` | `Date` | 2 Lossy | ipuz writes `mm/dd/yyyy`.  The xd spec does not state a date format; its examples and the corpus use `yyyy-mm-dd`.  `ipuz2xd` ignores this field and takes the date from the filename |
| `publisher`, `publication`, `url`, `uniqueid`, `difficulty`, `origin`, `annotation` | An additional metadata field | 2 Lossy | No standard name.  `ipuz2xd` drops all of them |
| `notes` | Notes | 2 Lossy | A headingless file keeps notes as the text after the clues ("Implicit sections").  A file with headings has no notes section ([#26]), and the formatting of such a section is open ([#4]).  `ipuz2xd` writes a `Notes:` metadata field |
| `intro` (text shown above the puzzle) | None | 3 Later | xd has one undifferentiated notes area and does not separate instructions from notes ([#4]) |
| `explanation` (text shown after a successful solve) | None | 3 Later | [#18] |
| `charset` | None | 3 Out | Input method for a solving app |
| Extension fields (`com.example:name`), `volatile` | An additional metadata field, a clue metadata key, or an unrecognized section | 2 Lossy | xd ignores unknown fields, keys and sections, which gives the same room to extend, without namespaces.  Whether a tool that rewrites a file keeps unknown sections is asked in [#26] |

### Grid and cells

| ipuz | xd v4 | Category | Notes |
|---|---|---|---|
| `dimensions` | The number and length of the grid lines | 1 Clean | |
| `solution`, a letter | A-Z in the grid ("Grid") | 1 Clean | |
| `solution`, the block value (`"#"` or `block`) | `#` or `.` | 1 Clean | |
| `solution`, `null` (an omitted cell) | `_` | 1 Clean | `ipuz2xd` has no branch that writes `_` for `null` |
| `solution`, the `empty` value, or no `solution` field | `?` | 2 Lossy | `?` means the cell takes a letter and its solution is not known.  ipuz does not say what an empty value in `solution` means, so this mapping is a reading, not a rule |
| `solution`, a string longer than one character | A rebus key and `Rebus: 1=HEART` ("Rebus") | 1 Clean | |
| `solution`, an array (several values, applying in every direction) | `Rebus: 1=A\|B` ([PR #28], "Options") | 2 Lossy | Unclear in ipuz whether the values are alternatives or are all in the cell at once.  A converter that cannot tell follows PR #28's "Converted puzzles": the cells stay unlinked, the source's first value first |
| `solution`, `{"Across": …, "Down": …}` | `Rebus: 1=PH\|F`, with the direction carried by the answers on the clue lines ([PR #28], "Readings that differ by direction") | 2 Lossy | The Rebus field lists what the cell accepts but not which direction reads which |
| Lower-case or mixed-case solution (ipuz solutions are case-sensitive) | A rebus | 2 Lossy | Only upper-case A-Z is a letter in an xd grid; any other character is a rebus key |
| `puzzle`, a ClueNum in a cell | None; numbers appear only in clue references | 2 Lossy | xd does not store cell numbers and its spec does not state how they are assigned; conventional numbering is implied.  A puzzle numbered any other way cannot say so |
| `puzzle`, `"value"` (a cell's initial value), a given | None | 3 Out | No open issue.  Puzzmo keeps these in a non-standard `## Start` section (mentioned in [#4]) |
| `saved` | None | 3 Out | Solve state.  xd's grid is the solution |
| `zones` | None | 3 Out | Entries of arbitrary shape |
| `checksum` | None | 3 Out | See "Solution scrambling and checksums" |

### Cell styles (StyleSpec)

| ipuz | xd v4 | Category | Notes |
|---|---|---|---|
| `styles` (named styles) | A style character and its rule ("Design") | 1 Clean | |
| `shapebg: "circle"` | `background: circle` | 1 Clean | `ipuz2xd` does not read cell styles at all, so circles are dropped today ([#30]) |
| `shapebg`, other shapes (arrows, diamond, star, …) | None | 3 Later | The baseline list of decorations is part of [#5] |
| `highlight` (its look is left to the app) | `background: shaded` ("the renderer chooses the color") | 1 Clean | |
| `color` (background) | None | 3 Later | [#5].  ipuz allows a hex value or a number meaning "some colour, the same wherever this number is used"; the second has no counterpart in the proposals so far |
| `colortext` | None | 3 Later | A letter colour is asked for in [#5] |
| `colorborder`, `colorbar`, `border` | None | 3 Out | |
| `barred`, top or left | `bar-top`, `bar-left` | 1 Clean | |
| `barred`, right or bottom | `bar-left` on the cell to the right, `bar-top` on the cell below | 2 Lossy | A bar on the right or bottom edge of the grid has no cell to carry it |
| `dotted`, `dashed` | None | 3 Out | |
| `imagebg` | `background-image` | 1 Clean | ipuz image URLs may be relative to a site or package, so a converter has to resolve or embed them.  The draft says "Prefer a data URI" |
| `slice` (part of an image per cell) | One image with `background-size` | 2 Lossy | Slices that form a rectangle become one spanned image; other arrangements do not convert ([#25]) |
| `image` (shown in place of the cell's text) | None | 3 Out | xd has no image that stands in for a cell's letter |
| A style on a `solution` cell (shown once solved) | None | 3 Later | When an image or style is shown, from the start or after the solve: [#25], [#5] |
| `mark`, `label`, `divided`, `named` | None | 3 Out | |
| `lessthan`, `greaterthan`, `equal` | None | 3 Out | Sudoku constraints |

### Clues

| ipuz | xd v4 | Category | Notes |
|---|---|---|---|
| `clues`, `Across` and `Down` | `A` and `D` clue lines ("Clues") | 1 Clean | |
| A direction label (`"Across:Horizontales"`) | None | 3 Out | v3's `Cluegroup` field could name a group; v4 drops it |
| `Diagonal` and the other diagonal directions, `Zones` | None | 3 Out | v4 has Across, Down and uniclue only |
| `Clues` (clues in a preset order) | Uniclue lines, with no letter | 2 Lossy | Uniclue is a numbered clue for both entries at a square, which is not the same thing |
| `Clue.number` | The clue reference | 1 Clean | A lettered ClueNum also fits: "The reference runs to the first '.'" |
| `Clue.clue` | The clue body | 1 Clean | |
| `Clue.answer` | The answer after ` ~ ` | 2 Lossy | xd is stronger here: every clue line states its answer, where ipuz gives one only when it differs from the grid.  But an xd answer "ends at the first whitespace", so `GO FOR IT` is written `GOFORIT` |
| `Clue.enumeration`, `showenumerations` | Text in the clue body, or a clue metadata key ("Clue Metadata") | 2 Lossy | No field.  "The xd spec does not reserve any keys" |
| `Clue.references`, `Clue.continued` | A clue metadata key such as `^Refs:` | 2 Lossy | The spec's own example uses `^Refs: A2 D4`, but the key is not reserved |
| `Clue.numbers` (one clue for several entries) | A clue line at each position | 2 Lossy | Nothing marks the lines as one clue |
| `Clue.label` | The clue reference | 2 Lossy | The reference is both identity and display in xd |
| `Clue.type`, `Clue.explanation`, `Clue.tags` | Clue metadata keys | 2 Lossy | No standard names |
| `Clue.image` (the clue text serves as its alt text) | `{!alt text \| src: …!}` ("xdown Formatting") | 1 Clean | Audio and video in a clue are open in [#6]; ipuz has neither |
| `Clue.hints` | None | 3 Out | |
| `Clue.cells` | None | 3 Out | Entries of arbitrary shape; an xd entry is a run of cells across or down |
| `Clue.highlight` | None | 3 Out | |
| `answer`, `answers`, `enumeration`, `enumerations` (the puzzle's final answer) | An additional metadata field | 2 Lossy | |
| `misses` | None | 3 Out | Hints for a solving app |

### Markup

ipuz allows a subset of HTML in `title`, `author`, `editor`, `publisher`,
`publication`, `intro`, `explanation`, `notes`, `difficulty`, in clues, and in
a clue's `hints` and `explanation`.  xd allows xdown in clue bodies and in
metadata values ("xdown Formatting"); [PR #28] excepts the `Rebus` field.
Notes sections have no defined format ([#4]).

| ipuz | xd v4 | Category | Notes |
|---|---|---|---|
| `<b>`, `<strong>` | `{*bold*}` | 1 Clean | |
| `<i>`, `<em>` | `{/italic/}` | 1 Clean | |
| `<u>` | `{_underscore_}` | 1 Clean | |
| `<s>` | `{-strike-through-}` | 1 Clean | |
| `<sup>`, `<sub>` | `{^superscript^}`, `{~subscript~}` | 1 Clean | |
| `<br>` | `{\\}` | 1 Clean | |
| `&amp;`, `&lt;`, other entities | The character itself | 1 Clean | xd is UTF-8 and needs no entities |
| `<big>`, `<small>` | None | 3 Out | `{=small caps=}` is a different thing |
| `<ipuz:fill/>`, `<ipuz:color1/>`, `<ipuz:highlight/>` | None | 3 Out | Text filled in by the app |

`ipuz2xd` unescapes entities but does not convert tags, so `<i>` reaches the
.xd file as literal text ([#30] does not list this yet).

### What xd v4 can say that ipuz cannot

- **Cells that change together.**  With [PR #28], `12345=CIGAR|PENIS` accepts
  CIGAR or PENIS and nothing in between.  ipuz can only list a hash for each
  whole correct grid in `checksum`, which does not say which cells vary.
- **Several answers for one clue.**  `A1. Sugar ___ ~ CONE ~ CANE`.  An ipuz
  clue has one `answer`.
- **A cell that is correct when empty**, and an entry whose answer is empty
  ([PR #28], [#13]).  ipuz uses its empty value to mean "no value".
- **A link in a clue**, `{@text | href: …@}`.  ipuz's HTML subset has no `<a>`.
- **Small caps**, `{=small caps=}`.
- **The credit as printed**, apart from the author's name: `Byline` ([PR #32]).

## JPZ

A .jpz file is a `crossword-compiler-applet` element holding
`applet-settings` and a `rectangular-puzzle`.  Element and attribute names
below are from the two schemas.

### Puzzle kinds

| JPZ | xd v4 | Category | Notes |
|---|---|---|---|
| `crossword` | A .xd file | 1 Clean | |
| `sudoku`, `coded`, `word-search` | None | 3 Out | xd is for crosswords |
| `rectangular-puzzle/@alphabet` | None | 3 Out | Input method |

### Metadata and text

| JPZ | xd v4 | Category | Notes |
|---|---|---|---|
| `metadata/title` | `Title` | 1 Clean | The applet settings have a second `title` element; the schema does not say which wins |
| `metadata/creator` | `Author` | 1 Clean | `Byline` ([PR #32]) has no JPZ counterpart |
| `metadata/editor` | `Editor` | 1 Clean | |
| `metadata/copyright`, `metadata/rights` | `Copyright` | 2 Lossy | JPZ has both and the schema documents neither, so how they differ is unclear.  xd has one field |
| `metadata/created` | `Date` | 2 Lossy | An undocumented string in JPZ.  By its name it is when the file was made, which need not be the publication date |
| `metadata/publisher`, `metadata/identifier` | An additional metadata field | 2 Lossy | No standard name |
| `metadata/description` | Notes | 2 Lossy | Plain text.  Same gap as ipuz `notes`: [#26], [#4] |
| `instructions` (shown with the puzzle on screen and in print) | None | 3 Later | Formatted text (see "Markup").  xd does not separate instructions from notes ([#4]) |
| `applet-settings/completion` (message or picture shown when done) | None | 3 Later | [#18] |
| `applet-settings`: `timer`, `actions`, colours, layout, `completion/@only-if-correct` and the rest | None | 3 Out | Configuration of one solving app |

### Grid and cells

| JPZ | xd v4 | Category | Notes |
|---|---|---|---|
| `grid/@width`, `@height` | The grid lines | 1 Clean | |
| `cell/@type="letter"` with `@solution` | A-Z ("Grid") | 1 Clean | |
| `cell/@type="block"` | `#` or `.` | 1 Clean | |
| `cell/@type="void"`, or a cell left out | `_` | 1 Clean | |
| `cell/@type="clue"`, `cell/clue`, `cell/arrow`, `grid-look/arrows` | None | 3 Out | Clues printed inside squares (arrowword) |
| `cell/@solution` absent on a letter cell | `?` | 1 Clean | The applet schema applies its wrong-letter colour only to cells that have a solution, so an absent solution means "not known" |
| `cell/@solution` longer than one character | A rebus key and `Rebus:` ("Rebus") | 1 Clean | `@solution` is an untyped string.  The schema mentions multi-letter cells only under `background-picture/@rebus` |
| Alternates for a cell | `Rebus: 1=O\|A` ([PR #28]) | 1 Clean | In the other direction: JPZ's schema has one `@solution` per cell and nothing for alternates |
| `cell/@solve-state`, `@solve-status` (`pencil`, `revealed`) | None | 3 Out | Solve state |
| `cell/@hint` (the solution is shown to the solver), a given | None | 3 Out | Same as ipuz `value` |
| `cell/@number` | None; numbers appear only in clue references | 2 Lossy | Same as ipuz: xd stores no cell numbers |
| `cell/@top-right-number`, `@bottom-right-number`, `grid-look/numbered-sides`, `@numbering-scheme` | None | 3 Out | |
| `cell/@x` as a range (a cell spanning several squares) | None | 3 Out | |
| `cell/@noclue` | None | 3 Out | xd lists the clues it has; nothing marks an entry as deliberately unclued |

### Cell styles

| JPZ | xd v4 | Category | Notes |
|---|---|---|---|
| `cell/@background-shape="circle"` | `background: circle` ("Design") | 1 Clean | `circle` is the only shape in the schema |
| `cell/@top-bar`, `@left-bar` | `bar-top`, `bar-left` | 1 Clean | The same two edges as xd |
| `grid-look/@bars-in-collocations`, `@collocation-separator-style` | None | 3 Out | Bars that mark word breaks inside an entry, not entry boundaries |
| `cell/@background-color` | None, or `background: shaded` | 3 Later | [#5].  A grey could be written as `shaded`, losing the colour |
| `cell/@foreground-color` | None | 3 Later | A letter colour is asked for in [#5] |
| `cell/@background-shape-color` | None | 3 Later | orta's `decoration-color` in [#5] |
| `grid-look/@block-color`, `@grid-line-color`, `@font-color`, `@number-color`, `@font`, `@cell-size-in-pixels`, `@thick-border`, `@italian-style` | None | 3 Out | Rendering of the whole grid |
| `cell/@bold`, `@italic` | None | 3 Out | |
| `cell/background-picture` (`encoded-image` in base64, or `svg`) | `background-image` with a data URI | 1 Clean | JPZ embeds the image, which is what the draft prefers.  Formats: JPG, GIF, PNG, WEBP, SVG |
| `background-picture/@rebus` (the picture appears only in the solution) | None | 3 Later | When an image is shown: [#25] |
| `background-picture/@href` | None | 3 Out | |

### Words and clues

JPZ names every entry as a `word`, a list of cells in order, and each clue
points at a word.  xd has no such list: an entry is a run of cells across or
down, bounded by blocks, bars and the grid's edge.

| JPZ | xd v4 | Category | Notes |
|---|---|---|---|
| `word` that is a straight run across or down | Implied by the grid | 1 Clean | |
| `word` of any other shape: bent, reversed (`x="10-5"`), or in separate parts | None | 3 Out | |
| `word/@solution` (the answer with its word breaks, as in `Big Ben`) | The answer after ` ~ ` | 2 Lossy | An xd answer is one word; the break is lost |
| `word/@hidden`, `@keyword`, `@is-theme`, `@word-separator-bars` | None, or a clue metadata key | 2 Lossy | `is-theme` could be a clue metadata key; no key is reserved |
| `clues` (at most two blocks) with `title` | `A` and `D` clue lines | 2 Lossy | Blocks titled Across and Down convert.  Any other title has nowhere to go; v4 drops `Cluegroup` |
| `clues/@ordering`, `@hide-numbers` | None | 3 Out | |
| `clue/@number` | The clue reference | 1 Clean | |
| `clue` text | The clue body | 1 Clean | |
| `clue/@format` (printed in brackets after the clue) | Text in the clue body, or a clue metadata key | 2 Lossy | Enumeration; same as ipuz |
| `clue/@is-link` (a clue that only points at another part of its word) | A clue line | 2 Lossy | Nothing marks it as a pointer |
| `clue/@hint-url` | `{@text \| href: …@}` in the clue body, or a clue metadata key | 2 Lossy | xd links text inside the clue; JPZ attaches one link to the whole clue |
| `clue/@citation`, `@tags` | Clue metadata keys | 2 Lossy | No standard names |

### Markup

A JPZ clue, the `instructions` element and a clue block's `title` may contain
`span`, `b`, `i`, `u`, `sub`, `sup` and `br`.  The metadata elements are plain
strings.

| JPZ | xd v4 | Category | Notes |
|---|---|---|---|
| `b`, `i`, `u`, `sub`, `sup` | `{*…*}`, `{/…/}`, `{_…_}`, `{~…~}`, `{^…^}` | 1 Clean | |
| `br` | `{\\}` | 1 Clean | |
| `span` | Plain text | 1 Clean | It carries no formatting in the schema |

### What xd v4 can say that JPZ cannot

- **Several accepted answers in a cell, and cells that change together**
  ([PR #28]).  The schema has one solution per cell.
- **Several answers for one clue.**
- **Strike-through, small caps, and an image inside clue text.**
- **Formatting in the title, author and other metadata.**  JPZ metadata is
  plain text.
- **Shading without a colour**, `background: shaded`.  JPZ needs a colour.

Whether a JPZ cell can be correct when empty is not clear from the schema:
`solution=""` is valid XML, but nothing says how it differs from an absent
solution.

## Across Lite .puz

Derived from puz.py, as said above.  Names are puz.py's attributes and the
four-letter codes of the extension sections.

### Header and strings

| .puz | xd v4 | Category | Notes |
|---|---|---|---|
| `title` | `Title` | 1 Clean | |
| `author` | `Author` | 1 Clean | Often holds a whole credit line ("By X / Edited by Y"), since .puz has no editor field.  `puz2xd` copies it as is; the printed credit is what `Byline` is for ([PR #32]) |
| `copyright` | `Copyright` | 1 Clean | |
| No editor or date field | `Editor`, `Date` | 1 Clean | In the other direction: xd holds what .puz cannot.  Converters take them from the author string, the filename or the source |
| `notes` (the notepad) | Notes | 2 Lossy | One string, used for instructions and notes alike.  Same gap as the others: [#26], [#4].  `puz2xd` writes a `Notes:` metadata field, joining its lines into one |
| `width`, `height` | The grid lines | 1 Clean | One byte each in .puz, so at most 255 |
| `encoding` (ISO-8859-1 before file version 2, UTF-8 from version 2) | UTF-8 | 2 Lossy | Real files often hold bytes from other encodings; see [character-encoding.md](character-encoding.md) |
| `puzzletype` 0x0401, diagramless | None | 2 Lossy | The solved grid can be written.  Nothing in xd says it is a diagramless.  `puz2xd` writes the diagramless block `:` as `_` |
| `preamble`, `postscript`, `unk1`, `unk2`, the four checksums | None | 3 Out | File integrity and bytes puz.py only round-trips |

### Grid and cells

| .puz | xd v4 | Category | Notes |
|---|---|---|---|
| `solution`, a letter | A-Z ("Grid") | 1 Clean | |
| `solution`, `.` (or `:` in a diagramless) | `#` or `.` | 1 Clean | v4 reads `.` as a block, as .puz does |
| No non-existent cell | `_` | 1 Clean | In the other direction: a .puz grid is a full rectangle, so shaped grids use blocks |
| `solution`, any other single character (digit, symbol) | A rebus key standing for itself, `Rebus: 1=1` | 1 Clean | `puz2xd` does this, with a warning |
| `GRBS` and `RTBL` (rebus grid and its table, `0:HEART;1:DIAMOND;`) | A rebus key and `Rebus: 1=HEART` ("Rebus") | 1 Clean | One string per cell |
| The `solution` byte under a rebus cell (usually the first letter) | An extra option, `1=HEART\|H` ([PR #28]) | 2 Lossy | puz.py stores this letter but does not say whether a solver may enter it instead.  `puz2xd` drops it |
| `fill` (the solver's letters, `-` for empty) | None | 3 Out | Solve state |
| `RUSR` (the solver's rebus entries) | None | 3 Out | Solve state |
| `GEXT` bits 0x10, 0x20, 0x40 (was incorrect, is incorrect, revealed) | None | 3 Out | Solve state |
| `LTIM` (seconds elapsed, running or stopped) | None | 3 Out | Solve state |
| `solution_state` 0x0002, solution not provided | `?` in every letter cell | 2 Lossy | The v4 meaning of `?` fits.  puz.py does not say what the `solution` bytes hold in such a file, and `puz2xd` does not check the state |

### Cell styles

| .puz | xd v4 | Category | Notes |
|---|---|---|---|
| `GEXT` bit 0x80, circled | `background: circle` ("Design") | 1 Clean | `puz2xd` still writes the v3 form, a `Special: circle` field and a lower-case letter, which v4 drops ([#30]).  It also loses the circle on a cell that is both circled and a rebus |
| No shading, colour, bars or images | `background: shaded`, `bar-top`, `bar-left`, `background-image` | 1 Clean | In the other direction.  Publishers use the circle bit for shaded squares, so a circle from a .puz may have been shading in print |

### Clues

| .puz | xd v4 | Category | Notes |
|---|---|---|---|
| `clues`, one list in grid order | `A` and `D` clue lines ("Clues") | 1 Clean | .puz stores no numbers or directions; both come from numbering the grid, which is how `puz2xd` builds the references |
| No answers | The answer after ` ~ ` | 1 Clean | In the other direction: the converter reads each answer out of the grid, expanding rebuses |
| Clue text | The clue body | 1 Clean | A plain string.  There is no markup in .puz, so nothing to convert, and xdown has no .puz form |

### Across Lite text format

puz.py also reads Across Lite's text format (`<ACROSS PUZZLE>` and
`<ACROSS PUZZLE v2>`).  Its sections are `TITLE`, `AUTHOR`, `COPYRIGHT`,
`SIZE`, `GRID`, `REBUS`, `ACROSS`, `DOWN` and `NOTEPAD`, and they map as the
binary fields above do.  A `REBUS` line is `marker:SOLUTION:short`, and a
`MARK;` line there circles every lower-case cell, the same device as xd v3's
`Special` field.

### What xd v4 can say that .puz cannot

Most of v4: non-existent cells, a per-cell unknown solution, alternates and
linked cells, shading, bars, images, clue markup, clue metadata, an editor, a
date, clue numbers that differ from the conventional numbering, and uniclues.
A converter from xd to .puz has to drop or flatten all of these.

## Solution scrambling and checksums

| Format | Mechanism | xd v4 | Category |
|---|---|---|---|
| .puz | `solution_state` 0x0004: the solution letters are scrambled with a four-digit key, and `scrambled_cksum` lets an app check a fill without the key | None | 3 Out |
| ipuz | `checksum`: a salt and one SHA-1 hash per correct solution, so that a file can omit `solution` and still be checked | None | 3 Out |
| JPZ | None in the schema | | |

An xd file states its solution in the open; that is the point of a corpus
format.  A file whose solution is withheld is written with `?` cells.  Two
things follow for converters:

- A scrambled .puz has to be unlocked before conversion.  `puz2xd` does not
  look at `solution_state`, so a locked file converts with its scrambled
  letters as the grid.  This is not listed in [#30] yet.
- [PR #28] gives xd its own rule for whether a grid is solved ("Checking a
  solve": the grid and the `Rebus` field decide, never the answers on clue
  lines).  That covers what ipuz uses several hashes for, without hiding
  anything.

## Summary: gaps that point at open issues

| Gap | Seen in | Issue | Blocks v4.0? |
|---|---|---|---|
| Alternates, linked cells, cells correct when empty | ipuz arrays and per-direction values; none of the three can link cells | [#12], [#13], [PR #28] | Yes, in review |
| Cell colours: background, letter, decoration | ipuz `color`, `colortext`; JPZ `background-color`, `foreground-color` | [#5] | The baseline (circle, shaded, bars) does; colours can follow |
| Decorations other than a circle | ipuz `shapebg` | [#5] | No |
| A notes section in a file with headings, and its format | ipuz `notes`; JPZ `description`; .puz `notes` | [#26], [#4] | The heading rule may; the rest is additive |
| Instructions as distinct from notes | ipuz `intro`; JPZ `instructions` | [#4] | No |
| After-solve text | ipuz `explanation`; JPZ `completion` | [#18] | No |
| When an image or style is shown, and images over several cells | ipuz styles on `solution`, `slice`; JPZ `background-picture/@rebus` | [#25] | No |
| Audio and video in clues | None of the three has them | [#6] | No |
| The credit as printed | .puz `author` in practice | [#11], [PR #32] | No |
| Converters behind the draft | `puz2xd`, `ipuz2xd` | [#30] | Release gate |

[#16] (text revised after a puzzle ran) has no counterpart in any of the three
formats.

### Gaps with no issue

These came out of the comparison and are not tracked anywhere.  None of them
changes what an existing file means, so by the rule in [#24] none blocks v4.0.

- **Givens**, cells shown filled at the start: ipuz `value`, JPZ `hint`.
- **Enumerations**: ipuz `enumeration`, JPZ `clue/@format`.  Today they go in
  the clue text or under an unreserved clue metadata key.
- **Cross-references between clues**: ipuz `references` and `continued`, JPZ
  `is-link`.  The spec's example uses `^Refs:` but reserves no key.
- **Word breaks in an answer**: ipuz `Clue.answer`, JPZ `word/@solution`.
- **Cell numbers** that do not follow conventional numbering, and the spec not
  saying how numbers are assigned.
- **Clue groups other than Across and Down**, and their titles, now that
  `Cluegroup` is dropped.
- **Entries that are not a straight run** across or down: ipuz `zones` and
  `Clue.cells`, JPZ `word`.
- **A flag for a diagramless**: ipuz kind, .puz `puzzletype`.
- **A bar on the right or bottom edge of the grid**, and dotted or dashed bars.
- **The format of `Date`**, which the spec does not state.
- **Converter fixes not in [#30]**: `ipuz2xd` leaves HTML tags in clue text,
  ignores the ipuz `date` field and drops cell styles; `puz2xd` converts a
  locked .puz without unscrambling it.

## What could not be determined

- **ipuz array values.**  The description of an array of values does not
  say whether the values are alternatives or are all in the cell together.
- **ipuz empty value in `solution`.**  Not defined; read here as "not known".
- **JPZ `rights` and `copyright`**, and the format of `created`: undocumented
  in the schema.
- **JPZ alternates and empty solutions.**  Nothing in the schema; an
  application may have a convention the schema does not show.
- **.puz with no solution** (`solution_state` 0x0002): puz.py does not say what
  the solution bytes hold, and its comment on this field says the values it uses differ
  from the documentation.
- **Whether Across Lite accepts the first letter of a rebus.**  puz.py stores
  the letter but its own check compares the whole string.
- **Converter behaviour** is described from reading `puz2xd.py` and
  `ipuz2xd.py`, not from running them on test files.  In particular, what
  `ipuz2xd` does with a `solution` cell that is an array or an object was not
  tested.

[#4]: https://github.com/century-arcade/xdformat/issues/4
[#5]: https://github.com/century-arcade/xdformat/issues/5
[#6]: https://github.com/century-arcade/xdformat/issues/6
[#11]: https://github.com/century-arcade/xdformat/issues/11
[#12]: https://github.com/century-arcade/xdformat/issues/12
[#13]: https://github.com/century-arcade/xdformat/issues/13
[#16]: https://github.com/century-arcade/xdformat/issues/16
[#18]: https://github.com/century-arcade/xdformat/issues/18
[#24]: https://github.com/century-arcade/xdformat/issues/24
[#25]: https://github.com/century-arcade/xdformat/issues/25
[#26]: https://github.com/century-arcade/xdformat/issues/26
[#30]: https://github.com/century-arcade/xdformat/issues/30
[PR #28]: https://github.com/century-arcade/xdformat/pull/28
[PR #32]: https://github.com/century-arcade/xdformat/pull/32
