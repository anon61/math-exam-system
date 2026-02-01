// src/lib.typ

// --- CONFIGURATION ---
#let show-solutions = true // Toggle to false to hide answers

// 1. LOAD THE DATABASE
#let questions = yaml("../data/questions.yaml")
#let definitions = yaml("../data/definitions.yaml")
#let tools = yaml("../data/tools.yaml")
#let examples = yaml("../data/examples.yaml")
#let mistakes = yaml("../data/mistakes.yaml")

// 2. BUILD THE KNOWLEDGE BASE (Dictionary Lookup)
// We convert lists to dictionaries for fast ID lookup
#let to-dict(list) = {
  let d = (:)
  for item in list {
    d.insert(item.id, item)
  }
  d
}

#let KB = (
  defs: to-dict(definitions),
  tools: to-dict(tools),
  ex: to-dict(examples),
  err: to-dict(mistakes),
  questions: to-dict(questions), // &lt;--- ADD THIS LINE
)

// 3. DEFINE THE ACCESSOR FUNCTIONS

// Function: #def("id")
// Usage: #def("def-bounded")
#let def(id) = {
  if id in KB.defs {
    let d = KB.defs.at(id)
    // Render: Bold Dark Blue Text with a link
    text(fill: rgb("#003366"), weight: "bold")[#d.term]
  } else {
    text(fill: red)[Unknown Def: #id]
  }
}

// Function: #tool("id")
// Usage: #tool("tool-tri-ineq")
#let tool(id) = {
  if id in KB.tools {
    let t = KB.tools.at(id)
    // Render: Italic Purple Text
    text(fill: rgb("#663399"), style: "italic")[#t.name]
  } else {
    text(fill: red)[Unknown Tool: #id]
  }
}

// Function: #ex("id")
// Usage: #ex("ex-harmonic")
#let ex(id) = {
  if id in KB.ex {
    let e = KB.ex.at(id)
    // Render: Green Text for Standard, Red for Counter-Example
    let color = if e.type == "Counter-Example" { rgb("#AA0000") } else { rgb("#006600") }
    text(fill: color)[#e.name]
  } else {
    text(fill: red)[Unknown Ex: #id]
  }
}

// Function: #mistake("id")
// Usage: #mistake("err-sign")
#let mistake(id) = {
  if id in KB.err {
    let m = KB.err.at(id)
    // Render: Red Strikethrough or Warning
    text(fill: red)[⚠️ #m.name]
  } else {
    text(fill: red)[Unknown Mistake: #id]
  }
}

// 1. Define Evaluation Scope
// This allows strings in YAML (like "Let $x$ be #def('limit')...") to be compiled.
#let eval-scope = (
  def: def,
  tool: tool,
  ex: ex,
  mistake: mistake
)

// 2. Question Renderer
#let question(id) = {
  if id in KB.questions {
    let q = KB.questions.at(id)
    
    // Visual Container
    block(
      width: 100%,
      stroke: 1pt + rgb("#003366"), // Academic Blue
      radius: 4pt,
      inset: 12pt,
      below: 1em,
      breakable: false, 
      [
        // Header: Topic + Metadata
        #grid(
          columns: (1fr, auto),
          align(left)[#text(fill: rgb("#003366"), weight: "bold")[#q.topic]],
          align(right)[#text(style: "italic", fill: luma(100))[#q.year | #q.lecturer]]
        )
        #line(length: 100%, stroke: 0.5pt + luma(200))
        #v(5pt)

        // Section: Given
        #if "given" in q and q.given != none [
          #strong[Given:]
          #pad(left: 1em)[#eval(q.given, mode: "markup", scope: eval-scope)]
        ]

        // Section: To Prove
        #if "to_prove" in q and q.to_prove != none [
          #strong[To Prove:]
          #pad(left: 1em)[#eval(q.to_prove, mode: "markup", scope: eval-scope)]
        ]

        // Section: Hint
        #if "hint" in q and q.hint != none and q.hint != "" [
          #v(5pt)
          #block(
            fill: luma(245), 
            inset: 8pt, 
            radius: 2pt, 
            width: 100%,
            text(size: 0.9em, style: "italic", fill: luma(80))[
              *Hint:* #eval(q.hint, mode: "markup", scope: eval-scope)
            ]
          )
        ]

        // E. Solutions (Conditional Render)
        #if show-solutions and "answer_steps" in q and q.answer_steps != none {
          block(
            width: 100%,
            inset: (top: 10pt),
            stroke: (top: 1pt + luma(200)),
            [
              #text(fill: rgb("#004400"), weight: "bold")[Official Solution:]
              #for step in q.answer_steps [
                #pad(left: 1em, top: 0.5em)[
                  #strong[#step.title] (#text(style: "italic")[#step.type]) \
                  #eval(step.content, mode: "markup", scope: eval-scope)
                ]
              ]
            ]
          )
        }
      ]
    )
  } else {
    text(fill: red)[Unknown Question ID: #id]
  }
}