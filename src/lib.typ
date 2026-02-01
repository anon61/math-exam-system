// src/lib.typ
// The Logic Core & Renderer

#import "utils.typ": *

// --- KNOWLEDGE BASE (KB) LOADER ---
#let KB = (
  examples: yaml("../data/examples.yaml"),
  // definitions: yaml("../data/definitions.yaml"),
  // tools: yaml("../data/tools.yaml"),
  // mistakes: yaml("../data/mistakes.yaml"),
  // courses: yaml("../data/courses.yaml"),
  // lectures: yaml("../data/lectures.yaml"),
  // tutorials: yaml("../data/tutorials.yaml"),
  // questions: yaml("../data/questions.yaml"),
)

// FIX: Comprehensive scope definition to handle all symbols used in YAML
#let eval-scope = (
  img: img, 
  ddx: ddx, 
  iso: iso, 
  subseteq: sym.subset.eq,
  sect: sym.inter,
  setminus: sym.without,
  iff: sym.arrow.l.r.double,
  implies: sym.arrow.r.double,
  supp: math.op("supp")
)

// --- LOADER ---
#let get-questions(path, query: (:)) = {
  let data = if path.ends-with(".json") { json(path) } else { yaml(path) }
  return data.filter(q => {
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

// --- ATOMIC RENDERERS ---
#let ex-colors = (
  "Standard": green,
  "Counter-Example": red,
  "Non-Example": orange,
)

#let ex(id) = {
  let item = KB.examples.find(e => e.id == id)
  if item == none {
    return text(fill: red)[*Error: Example `#id` not found.*]
  }

  let item-color = ex-colors.at(item.type)

  block(
    fill: item-color.lighten(90%),
    stroke: (left: 3pt + item-color),
    inset: 8pt,
    radius: 3pt,
    [
      #text(weight: "bold")[#item.name (#item.type)]
      #v(0.5em)
      #item.content
    ]
  )
}

// --- DOCUMENT TEMPLATE ---
#let exam-doc(title: "Real Analysis Exam", body) = {
  set page(
    paper: "a4",
    margin: (left: 20mm, right: 20mm, top: 20mm, bottom: 20mm),
    numbering: "1 / 1"
  )
  
  set text(font: "New Computer Modern", size: 11pt, lang: "en")
  set par(justify: true)
  
  align(center)[
    #text(size: 1.5em, weight: "bold", fill: rgb("#1d3557"))[#title]
    #v(0.5em)
    #text(size: 10pt, style: "italic")[Student Name: #line(length: 6cm)   ID: #line(length: 4cm)]
  ]
  v(1cm)
  
  body
}

// --- RENDERER 1: WORKSHEET ---
#let render-worksheet(questions) = {
  if questions.len() == 0 { return }

  for (i, q) in questions.enumerate() {
    if i > 0 { pagebreak() }
    
    // Header
    block(
      width: 100%, fill: rgb("#f1f3f5"), inset: 8pt, radius: 4pt, stroke: (left: 3pt + rgb("#1d3557")),
      grid(
        columns: (auto, 1fr, auto), align: horizon,
        text(size: 12pt, weight: "bold", fill: rgb("#1d3557"))[Question #(i+1)],
        align(center, text(weight: "bold", fill: luma(100))[#q.topic]),
        text(size: 9pt, style: "italic")[#q.year | #q.at("lecturer", default: "Unknown")]
      )
    )
    v(1em)

    // Body
    block(
      width: 100%, height: 1fr,
      {
        block(
          width: 100%, stroke: (bottom: 0.5pt + luma(200)), inset: (bottom: 1em),
          {
             text(weight: "bold")[
               #if "given" in q and q.given != none {
                 text(fill: rgb("#1d3557"))[Given: ] + eval(q.given, mode: "markup", scope: eval-scope)
              }
             ]
             if "to_prove" in q and q.to_prove != none {
               v(0.5em)
               block(
                fill: rgb("#fff9db"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#fcc419")),
                [*To Prove:* #eval(q.to_prove, mode: "markup", scope: eval-scope)]
               )
             }
          }
        )
        v(1em)

        block(
          width: 100%, height: 1fr, stroke: 0.5pt + luma(150), radius: 4pt, clip: true,
          stack(dir: ttb,
            block(width: 100%, height: 20%, fill: luma(250), inset: 8pt, stroke: (bottom: (thickness: 0.5pt, paint: luma(150), dash: "dashed")), text(size: 8pt, fill: luma(150), weight: "bold")[SCRATCHPAD]),
            block(width: 100%, height: 1fr, fill: dot-pattern(), inset: 8pt, text(size: 8pt, fill: luma(150), weight: "bold")[FORMAL PROOF])
          )
        )
      }
    )
  }
}

// --- RENDERER 2: STRATEGY ---
#let render-strategy(questions) = {
  text(style: "italic", fill: luma(100))[Tools, techniques, and common pitfalls.]
  v(1.5em)

  for (i, q) in questions.enumerate() {
    block(
      width: 100%, breakable: false, stroke: 0.5pt + luma(200), radius: 4pt, clip: true,
      stack(dir: ttb,
        block(
          width: 100%, fill: luma(245), inset: 8pt, stroke: (bottom: 0.5pt + luma(200)),
          grid(columns: (auto, 1fr), [*Q#(i+1)* #h(1em) #q.topic], align(right, text(size: 9pt, style: "italic")[Tools: #q.at("tools", default: "-")]))
        ),
        grid(
          columns: (1fr, 2fr), inset: 10pt, column-gutter: 1em,
          [*Common Mistakes:* \ #if "common_mistakes" in q { text(size: 10pt, fill: rgb("#c92a2a"))[#q.common_mistakes] } else { "-" }],
          [*Hint:* \ #if "hint" in q { eval(q.hint, mode: "markup", scope: eval-scope) } else { "-" }]
        )
      )
    )
    v(1em)
  }
}

// --- RENDERER 3: SOLUTIONS (Graph-Enabled) ---
#let render-solutions(questions) = {
  for (i, q) in questions.enumerate() {
    if i > 0 { pagebreak() }
    
    // 1. HEADER
    block(
      width: 100%, fill: rgb("#e7f5ff"), inset: 12pt, radius: 4pt, stroke: (left: 4pt + rgb("#1d3557")),
      [
        #text(size: 14pt, weight: "bold", fill: rgb("#1d3557"))[Solution to Question #(i+1)] \
        #v(0.3em)
        #text(size: 11pt, style: "italic")[Topic: #q.topic]
      ]
    )
    v(1.5em)

    // 2. RE-STATE PROBLEM
    block(
      width: 100%, fill: white, stroke: 0.5pt + luma(200), inset: 10pt, radius: 4pt, breakable: false, 
      [
        #text(size: 9pt, weight: "bold", fill: luma(100))[PROBLEM STATEMENT] \
        #v(0.5em)
        *Given:* #if "given" in q { eval(q.given, mode: "markup", scope: eval-scope) } \
        *To Prove:* #if "to_prove" in q { eval(q.to_prove, mode: "markup", scope: eval-scope) }
      ]
    )
    v(1.5em)

    // 3. AUTO-GENERATED PROOF GRAPH (SNAKE LAYOUT)
    if "answer_steps" in q {
      // Logic: Extract *every* step title to build the map
      let logic-nodes = ()
      for step in q.answer_steps {
         // We use the 'title' field of every step to build the full flow
         if "title" in step {
           logic-nodes.push(step.title)
         }
      }

      if logic-nodes.len() > 0 {
        block(
          width: 100%, fill: rgb("#f8f9fa"), inset: 10pt, radius: 4pt, stroke: (left: 2pt + luma(150)), breakable: false,
          [
            #text(size: 10pt, weight: "bold", fill: luma(100))[PROOF STRATEGY MAP] \
            #v(1em)
            #proof-flow(logic-nodes)
          ]
        )
        v(1.5em)
      }
    }
    
    // 4. FORMAL STEPS
    if "answer_steps" in q {
      for step in q.answer_steps {
        let type = step.at("type", default: "step")
        let title = step.at("title", default: "Step")
        
        if type == "setup" {
          block(width: 100%, inset: (left: 4pt), breakable: false, [#text(weight: "bold", size: 9pt, fill: luma(100))[#title] \ #text(fill: luma(80), style: "italic")[#eval(step.content, mode: "markup", scope: eval-scope)]])
          v(0.8em)
        } else if type == "claim" {
          block(
            width: 100%, fill: rgb("#fff"), stroke: (left: 3pt + rgb("#1d3557"), top: 0.5pt + luma(220), right: 0.5pt + luma(220), bottom: 0.5pt + luma(220)), inset: 12pt, radius: (right: 4pt, top: 2pt, bottom: 2pt), breakable: false, 
            [#text(weight: "bold", fill: rgb("#1d3557"))[Claim: #title] \ #v(0.3em) #eval(step.content, mode: "markup", scope: eval-scope) 
            #if "proof" in step { v(0.8em); line(length: 100%, stroke: 0.5pt + luma(220)); v(0.5em); text(size: 10pt)[*Proof:* #eval(step.proof, mode: "markup", scope: eval-scope) #h(1fr) $square.filled.tiny$] }]
          )
          v(1em)
        } else if type == "calculation" {
          block(width: 100%, breakable: false, [#text(size: 9pt, weight: "bold", fill: luma(150))[#title] #align(center, eval(step.content, mode: "markup", scope: eval-scope))])
          v(0.5em)
        } else if type == "conclusion" {
          block(width: 100%, fill: rgb("#f0fdf4"), stroke: (left: 3pt + rgb("#16a34a")), inset: 12pt, breakable: false, [#text(weight: "bold", fill: rgb("#16a34a"))[#title] \ #eval(step.content, mode: "markup", scope: eval-scope)])
        } else {
          block(width: 100%, inset: (left: 1em), breakable: false, eval(step.content, mode: "markup", scope: eval-scope))
          v(0.8em)
        }
      }
    }
    v(1fr);
    align(right)[$square.filled$]
  }
}