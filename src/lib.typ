// src/lib.typ

// --- CONFIGURATION ---
// 1. GLOBAL STATE TOGGLE
#let show_solutions = state("solutions", true) 

// 2. COLORS
#let dark_blue = rgb("#003366")
#let dark_green = rgb("#004400")
#let error_red = rgb("#FF0000")

// 3. LOAD THE DATABASE
// We use a safe loader pattern (assuming files exist; if not, Typst will error on file read, which is acceptable at this stage)
#let questions = yaml("../data/questions.yaml")
#let definitions = yaml("../data/definitions.yaml")
#let tools = yaml("../data/tools.yaml")
#let examples = yaml("../data/examples.yaml")
#let mistakes = yaml("../data/mistakes.yaml")

// 4. DICTIONARY CONVERSION
#let to-dict(list) = {
  let d = (:)
  for item in list {
    if "id" in item {
      d.insert(item.id, item)
    }
  }
  d
}

#let KB = (
  defs: to-dict(definitions),
  tools: to-dict(tools),
  ex: to-dict(examples),
  err: to-dict(mistakes),
  questions: to-dict(questions),
)

// 5. HELPER FUNCTIONS
#let def(id) = {
  if id in KB.defs {
    let d = KB.defs.at(id)
    text(fill: dark_blue, weight: "bold")[#d.at("term", default: id)]
  } else {
    text(fill: error_red)[Unknown Def: #id]
  }
}

#let tool(id) = {
  if id in KB.tools {
    let t = KB.tools.at(id)
    text(fill: rgb("#663399"), style: "italic")[#t.at("name", default: id)]
  } else {
    text(fill: error_red)[Unknown Tool: #id]
  }
}

#let ex(id) = {
  if id in KB.ex {
    let e = KB.ex.at(id)
    let type = e.at("type", default: "Standard")
    let color = if type == "Counter-Example" { rgb("#AA0000") } else { rgb("#006600") }
    text(fill: color)[#e.at("name", default: id)]
  } else {
    text(fill: error_red)[Unknown Ex: #id]
  }
}

#let mistake(id) = {
  if id in KB.err {
    let m = KB.err.at(id)
    text(fill: error_red)[⚠️ #m.at("name", default: id)]
  } else {
    text(fill: error_red)[Unknown Mistake: #id]
  }
}

// 6. EVALUATION SCOPE
#let eval-scope = (
  def: def,
  tool: tool,
  ex: ex,
  mistake: mistake
)

// 7. QUESTION RENDERER
#let question(id) = {
  if id in KB.questions {
    let q = KB.questions.at(id)

    block(width: 100%, breakable: true, {
      // --- HEADER ---
      grid(
        columns: (1fr, 1fr),
        align(left)[
          #text(weight: "bold", fill: dark_blue, size: 1.1em)[#q.at("topic", default: "General")]
        ],
        align(right)[
          #text(style: "italic", fill: gray)[
            #q.at("year", default: "Unknown Year") | #q.at("lecturer", default: "Unknown Lecturer")
          ]
        ]
      )
      line(length: 100%, stroke: 0.5pt + gray)

      // --- GIVEN ---
      let given = q.at("given", default: none)
      if given != none {
        pad(left: 0.5em, top: 0.5em)[
          *Given:* \
          #pad(left: 1em)[#eval(given, mode: "markup", scope: eval-scope)]
        ]
      }

      // --- IMAGE ---
      // Robust check: Ensure 'image' exists and is not empty/null
      let img = q.at("image", default: none)
      if img != none and img != "" {
        context {
            pad(y: 1em, align(center)[
              // Try/Catch logic isn't strictly available for file loading, 
              // but we assume the file exists if listed in YAML.
              #image("/data/images/" + img, width: 60%)
            ])
        }
      }

      // --- TO PROVE ---
      let to_prove = q.at("to_prove", default: none)
      if to_prove != none {
        pad(left: 0.5em, top: 0.5em)[
          *To Prove:* \
          #pad(left: 1em)[#eval(to_prove, mode: "markup", scope: eval-scope)]
        ]
      }

      // --- HINT ---
      let hint = q.at("hint", default: none)
      if hint != none {
        pad(top: 0.5em)[
          #block(fill: luma(245), inset: 8pt, radius: 4pt, width: 100%)[
            *Hint:* #text(style: "italic")[#hint]
          ]
        ]
      }

      // --- SOLUTION ---
      context if show_solutions.get() {
        v(1em)
        block(stroke: (left: 2pt + dark_green), inset: (left: 1em))[
          #text(fill: dark_green, weight: "bold")[Official Solution:]
          #v(0.5em)
          
          // iterate safely over steps
          #let steps = q.at("answer_steps", default: ())
          #if type(steps) == array {
            for step in steps {
              let title = step.at("title", default: "Step")
              let type = step.at("type", default: "logic")
              let content = step.at("content", default: "")
              
              [*#title* _(#type)_]
              pad(left: 1em)[#eval(content, mode: "markup", scope: eval-scope)]
              v(0.5em)
            }
          } else {
             text(style: "italic")[No structured solution available.]
          }
        ]
      }
    })
  } else {
    text(fill: error_red)[Unknown Question ID: #id]
  }
}