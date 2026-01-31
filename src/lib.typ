// src/lib.typ
// This is the Logic Core of the exam system.

// Import the custom functions to create an evaluation scope.
#import "utils.typ"

// CRITICAL: Create a scope dictionary from the `utils` module.
#let eval-scope = dictionary(utils)

// Loads and filters the question database.
#let get-questions(path, query: (:)) = {
  let questions = yaml(path)
  return questions.filter(q => {
    let passes = true
    if query.len() == 0 { return true }
    for (key, value) in query {
      if q.at(key, default: none) != value {
        passes = false
        break
      }
    }
    return passes
  })
}

// Renders a list of questions into a professional worksheet format.
#let render-worksheet(questions) = {
  if questions.len() == 0 {
    align(center + horizon)[
      #text(size: 14pt, fill: red)[No questions found matching this filter.]
    ]
    return // Stop rendering
  }

  counter("worksheet-q").update(0)

  for (i, q) in questions.enumerate() {
    // FIX: Only pagebreak AFTER the first question.
    if i > 0 { pagebreak() }

    // --- Question Header ---
    // Uses a grid to align the title and metadata badges.
    let lecturer = q.at("lecturer", default: "N/A")
    grid(
      columns: (1fr, auto),
      align: (left, bottom),
      // Left side: Question Title
      text(size: 16pt, weight: "bold")[Question #(i + 1)],
      // Right side: Metadata Badges
      block(
        inset: (bottom: 4pt),
        text(size: 9pt)[
          #rect(
            fill: luma(230),
            radius: 4pt,
            inset: 5pt,
            [ #q.year | #lecturer ]
          )
        ]
      )
    )

    // --- Question Body ---
    // A block provides spacing and a container for the question content.
    block(
      inset: (top: 1em, bottom: 2em),
      eval(q.body, mode: "markup", scope: eval-scope)
    )

    // --- Answer Area ---
    // A block with a 1pt stroke defines the main answer box.
    // `height: 1fr` makes it fill the remaining vertical space on the page.
    block(
        width: 100%,
        height: 1fr,
        stroke: 1pt + luma(200),
        // Top section for planning work.
        rect(
            width: 100%,
            fill: luma(240),
            inset: 8pt,
            text(weight: "bold")["Strategy / Key Concepts"]
        )
    )
  }
}

// Renders a summary page with hints for all questions.
#let render-hints(questions) = {
  pagebreak()
  heading(level: 1, numbering: none)[Hints & Techniques]

  // A table to neatly organize the hints.
  table(
    columns: (auto, 1fr, 2fr),
    align: (center, left, left),
    inset: 10pt,
    stroke: .5pt,
    [*Question*], [*Technique*], [*Hint*],
    ..questions.enumerate().map(((i, q)) => {
      let fixed_hint = q.hint.replace("uv'", "u v'").replace("u'v", "u' v")
      return (
        align(center, str(i + 1)),
        q.technique,
        // Hints can contain Typst markup, so they must be evaluated.
        eval(fixed_hint, mode: "markup", scope: eval-scope)
      )
    }).flatten()
  )
}