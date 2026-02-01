// src/lib.typ

// --- CONFIGURATION ---
#let show_solutions = state("solutions", true) // Toggle to false to hide answers
#let dark_blue = rgb("#003366")
#let dark_green = rgb("#004400")

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

    block(width: 100%, breakable: true, {
      // 1. Header (Topic | Year | Lecturer)
      grid(
        columns: (1fr, 1fr),
        align(left)[
          #text(weight: "bold", fill: dark_blue, size: 1.1em)[#q.topic]
        ],
        align(right)[
          #text(style: "italic", fill: gray)[#q.year | #q.lecturer]
        ]
      )
      line(length: 100%, stroke: 0.5pt + gray)

      // 2. Given
      pad(left: 0.5em, top: 0.5em)[
        *Given:* \
        #pad(left: 1em)[#eval(q.given, mode: "markup", scope: eval-scope)]
      ]

      // === NEW: IMAGE RENDERING BLOCK ===
      // Checks if the 'image' field exists and is not empty
      context if q.at("image", default: none) != none {
        pad(y: 1em, align(center)[
          // We use absolute path from Project Root
          #image("/data/images/" + q.image, width: 60%)
        ])
      }
      // ==================================

      // 3. To Prove
      pad(left: 0.5em, top: 0.5em)[
        *To Prove:* \
        #pad(left: 1em)[#eval(q.to_prove, mode: "markup", scope: eval-scope)]
      ]

      // 4. Hint (Optional)
      if q.at("hint", default: none) != none {
        pad(top: 0.5em)[
          #block(fill: luma(245), inset: 8pt, radius: 4pt, width: 100%)[
            *Hint:* #text(style: "italic")[#q.hint]
          ]
        ]
      }

      // 5. Official Solution (Hidden/Shown based on toggle)
      context if show_solutions.get() {
        v(1em)
        block(stroke: (left: 2pt + dark_green), inset: (left: 1em))[
          #text(fill: dark_green, weight: "bold")[Official Solution:]
          #v(0.5em)
          #for step in q.answer_steps {
            [*#step.title* _(#step.type)_]
            pad(left: 1em)[#eval(step.content, mode: "markup", scope: eval-scope)]
            v(0.5em)
          }
        ]
      }
    })
  } else {
    text(fill: red)[Unknown Question ID: #id]
  }
}