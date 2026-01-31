#import "src/lib.typ": get-questions, render-worksheet, render-hints

// ====================================================================
// ---                          TITLE PAGE                          ---
// ====================================================================
#set page(
  paper: "us-letter",
  margin: (x: 1in, y: 1in),
)
#set text(font: "New Computer Modern", size: 12pt)

#align(center)[
  #text(size: 24pt, weight: "bold")[Math Exam System Showcase]
  #v(1em)
  #text(size: 16pt)[A Demonstration of All Capabilities]
  #v(3em)
  #line(length: 100%)
  #v(1em)
  #grid(
    columns: (auto, 1fr),
    gutter: 1em,
    [Version:], [1.0.0],
    [Date:], [#datetime.today().display("[day] [month] [year]")],
  )
  #line(length: 100%)
]

#pagebreak()

// ====================================================================
// ---                  FULL WORKSHEET SECTION                      ---
// ====================================================================
#heading(level: 1, numbering: "1.", "Full Worksheet Demonstration")

This section renders all questions from the showcase data file. It demonstrates the 'Modern Academic' theme, the structured 'Given/To Prove' blocks, and the pedagogical answer grid.

#let all-questions = get-questions("/data/showcase_questions.yaml")
#render-worksheet(all-questions)

#pagebreak()

// ====================================================================
// ---                 FILTERING & EMPTY STATE                      ---
// ====================================================================
#heading(level: 1, numbering: "1.", "Filtering and Empty State")

Here, we apply a filter to the question set that yields no results (`year: 2025`). This demonstrates the system's ability to handle empty data sets gracefully by displaying a warning message instead of crashing or rendering an empty page.

#let no-questions = get-questions("/data/showcase_questions.yaml", query: (year: 2025))
#render-worksheet(no-questions)

#pagebreak()

// ====================================================================
// ---                      HINTS & SUMMARY                         ---
// ====================================================================
#heading(level: 1, numbering: "1.", "Hints & Summary Page")

The final section demonstrates the `render-hints` function. It compiles all hints from the showcase questions into a single, easy-to-read summary table. This also shows how custom functions from `utils.typ` (like `#hint-box`) are evaluated and rendered correctly.

#render-hints(all-questions)
