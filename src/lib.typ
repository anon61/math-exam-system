// src/lib.typ
// The Logic Core & Renderer

#import "utils.typ"
#let eval-scope = dictionary(utils)

// --- LOADER FUNCTION ---
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

// --- MAIN RENDERER ---
#let render-worksheet(questions) = {
  // 1. Global Typography & Math Settings
  set text(font: "New Computer Modern", size: 12pt)
  set math.equation(numbering: none)
  set par(justify: true)
  
  // 2. Empty State Guard
  if questions.len() == 0 {
    align(center + horizon)[
      #text(size: 14pt, fill: red)[No questions found matching this filter.]
    ]
    return
  }

  // 3. Main Question Loop
  for (i, q) in questions.enumerate() {
    // Page Break (Skip on first item)
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
    
    // Legacy support for 'body' field
    if "body" in q {
       block(
        inset: (top: 1em),
        eval(q.body, mode: "markup", scope: eval-scope)
      )
    }

    v(1em)

    // --- C. The Analyst's Workbench (New "Margin Note" Layout) ---
    block(
      width: 100%,
      height: 1fr,
      // We remove the outer border to let the sections breathe
      stroke: none, 
      radius: 4pt,
      clip: false,
      grid(
        rows: (auto, auto, 1fr),
        columns: (100%),
        gutter: 1em,
        
        // Phase 1: The Active Arsenal
        // "Boxed, Monospace Font, Active Checklists"
        block(
          width: 100%,
          inset: 12pt,
          fill: luma(245),
          stroke: (left: 4pt + rgb("#1d3557")), // Blue left border
          [
            #text(size: 10pt, weight: "bold", fill: rgb("#1d3557"), font: "Dejavu Sans Mono")[THE ARSENAL]
            #v(0.5em)
            #text(size: 10pt, style: "italic", fill: luma(80))[List the theorems and definitions required. Check assumptions:]
            #v(0.5em)
            #text(size: 9pt, font: "Dejavu Sans Mono", fill: luma(100))[
              [ ] Finite Measure? #h(2em) [ ] Non-negative func? #h(2em) [ ] Compact domain? \
              [ ] Continuous? #h(4.2em) [ ] Integrable (L1)? #h(3.6em) [ ] Monotone seq?
            ]
            #v(1.5em) // Space for student writing
          ]
        ),

        // Phase 2: The Sketch (Heuristic)
        // "Light Grey Background, Dashed, Scratch paper feel"
        block(
          width: 100%,
          height: 3cm, // Fixed height for scratchpad
          fill: luma(250), 
          inset: 12pt,
          stroke: (dash: "dashed", paint: luma(150)),
          [
            #text(font: "Dejavu Sans Mono", size: 9pt, fill: luma(100))[PROOF SKETCH / HEURISTIC] \
            #text(style: "italic", size: 10pt, fill: luma(150))[Informal logic. Draw diagrams or outline steps here...]
          ]
        ),

        // Phase 3: The Formal Proof (Margin Note Layout)
        // "2/3 + 1/3 Layout with Justification Rail"
        block(
          width: 100%,
          height: 100%,
          // Main container for the proof section
          stroke: 1pt + luma(200),
          radius: 2pt,
          clip: true,
          grid(
            columns: (3fr, 1fr), // 75% Math, 25% Justification
            rows: (100%),
            
            // Left Column: The Prose (The Math)
            block(
              height: 100%,
              inset: 12pt,
              [
                #text(weight: "bold", size: 11pt, fill: black)[Formal Proof]
                #v(1em)
                // Blank space for prose
              ]
            ),
            
            // Right Column: The Justification Rail (Margin Notes)
            block(
              height: 100%,
              fill: luma(252), // Very faint grey for the rail
              stroke: (left: 0.5pt + luma(200)), // Divider line
              inset: 12pt,
              [
                #align(right, text(style: "italic", size: 9pt, fill: luma(120))[Justification Rail])
                #v(1em)
                #align(right, text(size: 9pt, fill: luma(180))[
                  _e.g. by DCT_ \
                  \
                  _by Triangle Ineq_
                ])
              ]
            )
          )
        )
      )
    )
  }
}

// --- HINT PAGE RENDERER ---
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
        align(horizon, q.at("technique", default: "General")),
        if "hint" in q {
           eval(q.hint, mode: "markup", scope: eval-scope)
        } else {
           "No hint provided."
        }
      )
    }).flatten()
  )
}