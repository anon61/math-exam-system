// src/lib.typ
// The Logic Core & Renderer

#import "utils.typ": *

#let eval-scope = (img: img, ddx: ddx, iso: iso)

// --- LOADER ---
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
    // Full Width (20mm margins)
    margin: (left: 20mm, right: 20mm, top: 20mm, bottom: 20mm),
    numbering: "1 / 1"
  )
  
  set text(font: "New Computer Modern", size: 11pt, lang: "en")
  set par(justify: true)
  
  // Header
  align(center)[
    #text(size: 1.5em, weight: "bold", fill: rgb("#1d3557"))[#title]
    #v(0.5em)
    #text(size: 10pt, style: "italic")[Student Name: #line(length: 6cm)  ID: #line(length: 4cm)]
  ]
  v(1cm)
  
  body
}

// ==========================================
// RENDERER 1: THE WORKSHEET (Questions)
// ==========================================
#let render-worksheet(questions) = {
  if questions.len() == 0 { return }

  for (i, q) in questions.enumerate() {
    if i > 0 { pagebreak() }
    
    // 1. Question Header
    block(
      width: 100%,
      fill: rgb("#f1f3f5"),
      inset: 8pt,
      radius: 4pt,
      stroke: (left: 3pt + rgb("#1d3557")),
      grid(
        columns: (auto, 1fr, auto),
        align: horizon,
        text(size: 12pt, weight: "bold", fill: rgb("#1d3557"))[Question #(i+1)],
        align(center, text(weight: "bold", fill: luma(100))[#q.topic]),
        text(size: 9pt, style: "italic")[#q.year | #q.at("lecturer", default: "Unknown")]
      )
    )
    v(1em)

    // 2. Question Body
    block(
      width: 100%,
      height: 1fr,
      {
        block(
          width: 100%,
          stroke: (bottom: 0.5pt + luma(200)),
          inset: (bottom: 1em),
          {
             text(weight: "bold")[
              #if "given" in q and q.given != none {
                 text(fill: rgb("#1d3557"))[Given: ] + eval(q.given, mode: "markup", scope: eval-scope)
              }
             ]
             if "to_prove" in q and q.to_prove != none {
               v(0.5em)
               block(
                fill: rgb("#fff9db"), 
                inset: 10pt, radius: 4pt, width: 100%,
                stroke: (left: 3pt + rgb("#fcc419")),
                [*To Prove:* #eval(q.to_prove, mode: "markup", scope: eval-scope)]
               )
             }
          }
        )
        v(1em)

        // 3. Split-Brain Answer Box
        block(
          width: 100%,
          height: 1fr,
          stroke: 0.5pt + luma(150),
          radius: 4pt,
          clip: true,
          stack(dir: ttb,
            block(
              width: 100%, height: 20%, fill: luma(250), inset: 8pt,
              stroke: (bottom: (thickness: 0.5pt, paint: luma(150), dash: "dashed")),
              text(size: 8pt, fill: luma(150), weight: "bold")[SCRATCHPAD]
            ),
            block(
              width: 100%, height: 1fr, fill: dot-pattern(), inset: 8pt,
              text(size: 8pt, fill: luma(150), weight: "bold")[FORMAL PROOF]
            )
          )
        )
      }
    )
  }
}

// ==========================================
// RENDERER 2: STRATEGY GUIDE (Hints)
// ==========================================
#let render-strategy(questions) = {
  // No pagebreak here - handled by the file
  text(style: "italic", fill: luma(100))[Tools, techniques, and common pitfalls for this exam.]
  v(1.5em)

  for (i, q) in questions.enumerate() {
    block(
      width: 100%,
      breakable: false,
      stroke: 0.5pt + luma(200),
      radius: 4pt,
      clip: true,
      stack(dir: ttb,
        // Header
        block(
          width: 100%, fill: luma(245), inset: 8pt,
          stroke: (bottom: 0.5pt + luma(200)),
          grid(
            columns: (auto, 1fr),
            [*Q#(i+1)* #h(1em) #q.topic],
            align(right, text(size: 9pt, style: "italic")[Tools: #q.at("tools", default: "-")])
          )
        ),
        // Analysis Grid
        grid(
          columns: (1fr, 2fr),
          inset: 10pt,
          column-gutter: 1em,
          [
             *Common Mistakes:* \
             #if "common_mistakes" in q { 
               text(size: 10pt, fill: rgb("#c92a2a"))[#q.common_mistakes] 
             } else { "-" }
          ],
          [
             *Hint:* \
             #if "hint" in q { 
               eval(q.hint, mode: "markup", scope: eval-scope) 
             } else { "-" }
          ]
        )
      )
    )
    v(1em)
  }
}

// ==========================================
// RENDERER 3: FULL SOLUTIONS
// ==========================================
#let render-solutions(questions) = {
  // No pagebreak start here
  
  for (i, q) in questions.enumerate() {
    if i > 0 { pagebreak() } // Break page for each solution
    
    // Solution Header
    block(
      width: 100%,
      fill: rgb("#e7f5ff"),
      inset: 12pt,
      radius: 4pt,
      stroke: (left: 4pt + rgb("#1d3557")),
      [
        #text(size: 14pt, weight: "bold", fill: rgb("#1d3557"))[Solution to Question #(i+1)] \
        #v(0.3em)
        #text(size: 11pt, style: "italic")[Topic: #q.topic]
      ]
    )
    v(2em)
    
    // The Full Answer Text
    block(
      width: 100%,
      inset: 5pt,
      [
        #if "answer" in q { 
           set par(leading: 0.8em)
           eval(q.answer, mode: "markup", scope: eval-scope) 
        } else {
           text(style: "italic", fill: luma(150))[No formal solution provided in database.]
        }
      ]
    )
    
    align(right)[$square$]
  }
}