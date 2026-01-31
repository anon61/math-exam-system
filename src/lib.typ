// src/lib.typ
// The Logic Core & Renderer

#import "utils.typ": *

// FIX: Explicitly define the scope to avoid dictionary/module type errors
#let eval-scope = (
  img: img, 
  ddx: ddx, 
  iso: iso
)

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

// --- DOCUMENT TEMPLATE ---
#let exam-doc(title: "Real Analysis Exam", body) = {
  set page(
    paper: "a4",
    // 55mm Left Margin (Active), 15mm Right Margin (Safe Zone)
    margin: (left: 55mm, right: 15mm, top: 20mm, bottom: 20mm),
    numbering: "1 / 1"
  )
  
  set text(font: "New Computer Modern", size: 11pt, lang: "en")
  set par(justify: true)

  align(center)[
    #text(size: 1.5em, weight: "bold", fill: rgb("#1d3557"))[#title]
    #v(0.5em)
    #text(size: 10pt, style: "italic")[Student Name: #line(length: 6cm)  ID: #line(length: 4cm)]
  ]
  v(1cm)
  
  body
}

// --- QUESTION RENDERER ---
#let render-worksheet(questions) = {
  if questions.len() == 0 {
    align(center + horizon, text(fill: red)[No questions found matching this filter.])
    return
  }

  for (i, q) in questions.enumerate() {
    // Always start a new page for each question to maximize space
    if i > 0 { pagebreak() }
    
    // -- COMPONENT A: Active Margin --
    margin-cue[
      #stack(dir: ttb, spacing: 1em,
        // 1. Question ID
        text(size: 14pt, weight: "bold", fill: rgb("#1d3557"))[Q#(i+1)],
        
        // 2. Metadata
        text(size: 8pt, style: "italic", fill: luma(100))[
          #q.year \ #q.at("lecturer", default: "")
        ],

        // 3. Grading Ladder (Vertical)
        grading-ladder(max-points: 10),

        // 4. Cue / Recall (Only if present)
        if "cue" in q and q.cue != none {
          block(
            width: 100%, 
            inset: (right: 4pt),
            stroke: (right: 1pt + rgb("#1d3557")),
            text(size: 9pt, fill: rgb("#1d3557"))[
              *Recall:* \ #eval(q.cue, mode: "markup", scope: eval-scope)
            ]
          )
        }
      )
    ]

    // -- COMPONENT B: Main Body --
    // We use a container that fills the page height
    block(
      width: 100%,
      height: 100%, // Fill the page
      stroke: (bottom: 0.5pt + luma(200)),
      {
        // 1. Question Header & Given
        text(weight: "bold")[
          #if "given" in q and q.given != none {
             text(fill: rgb("#1d3557"))[Given: ] + eval(q.given, mode: "markup", scope: eval-scope)
          } else if "body" in q and q.body != none {
             eval(q.body, mode: "markup", scope: eval-scope)
          }
        ]
        
        // 2. To Prove (Highlighted)
        if "to_prove" in q and q.to_prove != none {
          v(0.5em)
          block(
            fill: rgb("#fff9db"), 
            inset: 8pt, 
            radius: 4pt, 
            width: 100%,
            stroke: (left: 2pt + rgb("#fcc419")),
            [*To Prove:* #eval(q.to_prove, mode: "markup", scope: eval-scope)]
          )
        }

        v(1em)

        // 3. EXPANDING ANSWER BOX (Split-Brain)
        // Uses '1fr' to take up all remaining space on the page
        block(
          width: 100%,
          height: 1fr, // MAXIMIZE SPACE
          stroke: 0.5pt + luma(150),
          radius: 4pt,
          clip: true,
          stack(dir: ttb,
            
            // Zone 1: Scratchpad (Fixed height, ~20%)
            block(
              width: 100%,
              height: 20%,
              fill: luma(250),
              inset: 8pt,
              stroke: (bottom: (thickness: 0.5pt, paint: luma(150), dash: "dashed")),
              [
                #text(size: 8pt, fill: luma(150), weight: "bold", font: "Dejavu Sans Mono")[SCRATCHPAD]
                // Clean: No ghost text here
              ]
            ),
            
            // Zone 2: Formal Proof (Fills remaining)
            block(
              width: 100%,
              height: 1fr, // Takes the rest of the box
              fill: dot-pattern(),
              inset: 8pt,
              [
                 #text(size: 8pt, fill: luma(150), weight: "bold", font: "Dejavu Sans Mono")[FORMAL PROOF]
                 // Clean: No ghost text here
              ]
            )
          )
        )
      }
    )
  }
}

// --- HINT PAGE RENDERER ---
#let render-hints(questions) = {
  pagebreak()
  heading(level: 1, numbering: none)[Hints & Summary]
  
  table(
    columns: (auto, 1fr, 2fr),
    inset: 10pt,
    fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
    align: (center, left, left),
    table.header([*Q*], [*Technique*], [*Hint*]),
    ..questions.enumerate().map(((i, q)) => (
      [*#(i+1)*],
      q.at("technique", default: "-"),
      if "hint" in q and q.hint != none { eval(q.hint, mode: "markup", scope: eval-scope) } else { "" }
    )).flatten()
  )
}