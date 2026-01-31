// (The Logic Core - Implementing the 3-Phase Layout)

#import "utils.typ"
#let eval-scope = dictionary(utils)

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

#let render-worksheet(questions) = {
  // --- 1. Global Typography Settings ---
  set text(font: "New Computer Modern", size: 12pt)
  set math.equation(numbering: none)
  set par(justify: true)
  
  // --- Empty State Check ---
  if questions.len() == 0 {
    align(center + horizon)[
      #text(size: 14pt, fill: red)[No questions found matching this filter.]
    ]
    return
  }

  // --- Main Loop ---
  for (i, q) in questions.enumerate() {
    // Page Break Logic (Skip on first item)
    if i > 0 { pagebreak() }

    // --- A. The Header Zone (Navy Theme) ---
    let lecturer = q.at("lecturer", default: "Unknown")
    
    grid(
      columns: (1fr, auto),
      align: (left, horizon),
      // Title
      text(weight: "bold", size: 18pt, fill: rgb("#1d3557"))[Question #(i + 1)],
      // Metadata Pill
      rect(
        fill: rgb("#e0fbfc"),
        radius: 10pt,
        inset: (x: 12pt, y: 6pt),
        stroke: none,
        text(size: 10pt, fill: rgb("#1d3557"), weight: "bold")[#q.year | #lecturer]
      )
    )
    v(0.5em)

    // --- B. The Structured Body (Given / To Prove) ---
    // Given Block (Blue)
    if "given" in q {
      block(
        width: 100%,
        fill: rgb("#e0fbfc"),
        inset: 10pt,
        radius: (top: 4pt),
        stroke: (left: 3pt + rgb("#1d3557")),
        [
          #text(weight: "bold", fill: rgb("#1d3557"))[Given:] \ 
          #eval(q.given, mode: "markup", scope: eval-scope)
        ]
      )
    }
    
    // To Prove Block (Yellow)
    if "to_prove" in q {
      block(
        width: 100%,
        fill: rgb("#fff3b0"),
        inset: 10pt,
        radius: (bottom: 4pt),
        stroke: (left: 3pt + rgb("#ffb703")),
        [
          #text(weight: "bold", fill: rgb("#fb8500"))[To Prove:] \ 
          #eval(q.to_prove, mode: "markup", scope: eval-scope)
        ]
      )
    }

    v(1em)

    // --- C. The Analyst's Workbench (3-Phase Answer Grid) ---
    block(
      width: 100%,
      height: 1fr,
      stroke: 1pt + luma(200),
      radius: 4pt,
      clip: true, // Ensures internal content doesn't overflow border
      grid(
        rows: (auto, 15%, 1fr),
        columns: (100%),
        
        // Phase 1: The Arsenal (Definitions)
        block(
          width: 100%,
          inset: 8pt,
          fill: luma(250),
          stroke: (bottom: 1pt + luma(200)),
          [
            #text(size: 9pt, weight: "bold", fill: rgb("#1d3557"))[THE ARSENAL: RELEVANT DEFINITIONS & THEOREMS]
            #v(2em) // Space for student to write
          ]
        ),

        // Phase 2: The Heuristic (Proof Sketch)
        block(
          width: 100%,
          height: 100%,
          fill: rgb("#fffbe6"), // Pale Yellow
          inset: 10pt,
          stroke: (bottom: (paint: luma(200), thickness: 1pt, dash: "dashed")),
          [
            #text(font: "Dejavu Sans Mono", size: 9pt, fill: luma(100))[PROOF SKETCH / HEURISTIC] \ 
            #text(style: "italic", size: 10pt, fill: luma(150))[Rough ideas... Discretization? Contradiction? Split the domain?]
          ]
        ),

        // Phase 3: The Formal Argument (Main Event)
        grid(
          columns: (1fr, 4cm),
          // Left Col: Formal Proof
          block(
            inset: 12pt,
            height: 100%,
            [
              #text(weight: "bold", size: 11pt)[Formal Proof] \ 
              #v(1em)
              // Empty space for prose
            ]
          ),
          // Right Col: Citations Sidebar
          block(
            height: 100%,
            stroke: (left: 0.5pt + luma(200)),
            inset: 8pt,
            fill: luma(253),
            [
              #align(center, text(style: "italic", size: 9pt, fill: luma(120))[Citations])
            ]
          )
        )
      )
    )
  }
}

#let render-hints(questions) = {
  pagebreak()
  set text(font: "New Computer Modern")
  heading(level: 1, numbering: none)[Hints & Techniques]
  v(1em)
  
  table(
    columns: (auto, 1fr, 2fr),
    align: (center, left, left),
    inset: 12pt,
    stroke: 0.5pt + luma(200),
    fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
    
    table.header(
      [*#text(fill: rgb("#1d3557"))[Q]*],
      [*#text(fill: rgb("#1d3557"))[Technique]*],
      [*#text(fill: rgb("#1d3557"))[Hint]*]
    ),
    
    ..questions.enumerate().map(((i, q)) => {
      (
        align(center + horizon, text(weight: "bold")[#(i + 1)]),
        align(horizon, q.technique),
        eval(q.hint, mode: "markup", scope: eval-scope)
      )
    }).flatten()
  )
}
