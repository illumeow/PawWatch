// PawWatch slide template
// Based on @template/slide:1.0.0 (itself derived from slydst), vendored here so
// everyone on the team can compile without a local package install.
//
// Usage:
//   #import "template.typ": *
//   #show: slides.with(title: "...", authors: ("A", "B"), institution: "...")
//
//   = Section        -> section divider slide
//   == Slide title   -> starts a new slide (no #pagebreak() needed)

#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, edge, node

#let default-color = blue.darken(40%)

#let layouts = (
  "small": ("height": 9cm, "space": 1.4cm),
  "medium": ("height": 10.5cm, "space": 1.6cm),
  "large": ("height": 12cm, "space": 1.8cm),
)
#let layout-space = state("space", v(-0.8cm))
#let accent = state("accent", default-color)

// Section dividers (level-1 headings) and focus slides get no header/footer
#let on-section-page() = {
  let page = here().page()
  query(heading.where(level: 1).or(<focus-slide>)).any(h => h.location().page() == page)
}

#let title-slide(content) = {
  set page(footer: none)
  set align(horizon)
  context layout-space.get()
  content
  pagebreak(weak: true)
}

// Big centered statement slide, e.g. #focus[Questions?]
#let focus(body) = {
  pagebreak(weak: true)
  [#metadata(none) <focus-slide>]
  block(width: 100%, height: 100%, align(center + horizon, context {
    text(1.6em, weight: "bold", fill: accent.get(), body)
  }))
  pagebreak(weak: true)
}

// Shaded box for definitions / takeaways
#let callout(title: none, body) = context {
  let c = accent.get()
  block(
    width: 100%,
    inset: (x: 0.8em, y: 0.6em),
    radius: 4pt,
    fill: c.lighten(90%),
    stroke: (left: 3pt + c),
    {
      if title != none { text(weight: "bold", fill: c, title) + linebreak() }
      body
    },
  )
}

// Two-column layout shortcut: #cols[left][right] or #cols(ratio: (3fr, 2fr))[..][..]
#let cols(ratio: (1fr, 1fr), gutter: 1.5em, ..bodies) = grid(
  columns: ratio,
  column-gutter: gutter,
  ..bodies.pos(),
)

#let slides(
  content,
  title: none,
  subtitle: none,
  date: none,
  authors: (),
  institution: none,
  layout: "medium",
  ratio: 16 / 9,
  title-color: none,
) = {
  // Parsing
  if layout not in layouts {
    panic("Unknown layout " + layout)
  }
  let (height, space) = layouts.at(layout)
  let width = ratio * height
  layout-space.update(v(-space / 2))
  if type(authors) != array {
    authors = (authors,)
  }

  // Colors
  if title-color == none {
    title-color = default-color
  }
  accent.update(title-color)

  // Setup
  set document(title: title, author: authors) if title != none
  set page(
    width: width,
    height: height,
    margin: (x: 0.5 * space, top: space, bottom: 0.6 * space),
    header: context {
      let page = here().page()
      if on-section-page() { return }
      let headings = query(heading.where(level: 2))
      let heading = headings.rev().find(x => x.location().page() <= page)
      if heading != none {
        set align(top)
        set text(1.4em, weight: "bold", fill: title-color)
        v(space / 2)
        block(heading.body + if heading.location().page() != page [
          #numbering("(1)", page - heading.location().page() + 1)
        ])
      }
    },
    header-ascent: 0%,
    footer: [
      #set text(0.8em)
      #set align(right)
      #context if not on-section-page() {
        counter(page).display("1/1", both: true)
      }
    ],
    footer-descent: 0.8em,
  )
  set outline(target: heading.where(level: 1), title: none)
  set bibliography(title: none)

  // Rules
  show heading.where(level: 1): x => {
    pagebreak(weak: true)
    set text(1.2em, weight: "bold", fill: title-color)
    block(width: 100%, height: 100%, align(center + horizon, move(dy: -space / 2, x.body)))
    pagebreak(weak: true)
  }
  show heading.where(level: 2): it => {
    pagebreak(weak: true)
    line(length: 100%, stroke: (paint: title-color))
    v(1.1em, weak: true)
  }
  show heading: set text(1.1em, fill: title-color)

  set text(
    font: (
      (name: "Liberation Serif", covers: "latin-in-cjk"),
      "Noto Serif CJK TC",
    ),
    size: 12pt,
    cjk-latin-spacing: auto,
    lang: "en",
  )
  set par(leading: 1.1em, spacing: 1.5em)
  set list(marker: ([•], [‣], [–]))

  show: codly-init.with()
  codly(languages: codly-languages)

  // Title
  if title != none {
    title-slide[
      #text(2.0em, weight: "bold", fill: title-color, title)
      #v(1.4em, weak: true)
      #if subtitle != none { text(1.1em, weight: "bold", subtitle) }
      #if subtitle != none and date != none { text(1.1em)[ \- ] }
      #if date != none { text(1.1em, date) }
      #v(1em, weak: true)
      #let byline = {
        authors.join(", ", last: " and ")
        if institution != none {
          linebreak()
          text(0.85em, fill: luma(90), institution)
        }
      }
      #if subtitle != none or date != none {
        place(bottom, byline)
      } else {
        align(left, byline)
      }
    ]
  }

  content
}
