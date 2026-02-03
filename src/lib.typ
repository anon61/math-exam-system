// src/lib.typ

// --- 1. GLOBAL CONFIGURATION ---
#let show_solutions = state("solutions", true) 

// Palette
#let c-primary   = rgb("#003366") // Navy Blue
#let c-secondary = rgb("#663399") // Purple
#let c-success   = rgb("#006600") // Green
#let c-error     = rgb("#b30000") // Red
#let c-gray      = rgb("#666666") // Gray

// --- 2. DATA LOADING ---
#let questions = yaml("../data/questions.yaml")
#let definitions = yaml("../data/definitions.yaml")
#let tools = yaml("../data/tools.yaml")
#let examples = yaml("../data/examples.yaml")
#let mistakes = yaml("../data/mistakes.yaml")
#let lectures = yaml("../data/lectures.yaml")
#let tutorials = yaml("../data/tutorials.yaml")

#let to-dict(list) = {
  let d = (:)
  for item in list {
    if "id" in item { d.insert(item.id, item) }
  }
  d
}

#let KB = (
  defs: to-dict(definitions),
  tools: to-dict(tools),
  ex: to-dict(examples),
  err: to-dict(mistakes),
  questions: to-dict(questions),
  lecs: to-dict(lectures),
  tuts: to-dict(tutorials)
)

// --- 3. UI HELPER COMPONENTS ---

// A small colored tag for metadata (e.g. "Calculus", "2024")
#let meta-tag(text-content, color) = {
  box(
    fill: color.lighten(90%),
    stroke: color,
    inset: (x: 0.5em, y: 0.2em),
    radius: 3pt,
    text(fill: color.darken(10%), size: 0.8em, weight: "bold", text-content)
  )
}

// Generic Card
#let card(title, icon, color, body) = {
  block(
    fill: color.lighten(95%),
    stroke: (left: 4pt + color),
    inset: 1em,
    radius: 4pt,
    width: 100%,
    breakable: false,
    [
      #text(fill: color, weight: "bold", size: 1.1em)[#icon #title]
      #v(0.5em)
      #body
    ]
  )
}

// --- 4. RENDERERS ---
#let def(id) = {
  if id in KB.defs {
    let d = KB.defs.at(id)
    card(d.at("term", default: id), "📖", c-primary, d.content)
  } else { text(fill: c-error)[Unknown Def: #id] }
}

#let tool(id) = {
  if id in KB.tools {
    let t = KB.tools.at(id)
    card(t.at("name", default: id), "🛠️", c-secondary, [
      *Statement:* #t.at("statement", default: t.at("description", default: ""))
    ])
  } else { text(fill: c-error)[Unknown Tool: #id] }
}

#let ex(id) = {
  if id in KB.ex {
    let e = KB.ex.at(id)
    let type = e.at("type", default: "Standard")
    let color = if type == "Counter-Example" { c-error } else { c-success }
    card(e.at("name", default: id) + " (" + type + ")", "💡", color, e.content)
  } else { text(fill: c-error)[Unknown Ex: #id] }
}

#let mistake(id) = {
  if id in KB.err {
    let m = KB.err.at(id)
    card(m.at("name", default: id), "⚠️", c-error, [
      *Error:* #m.description \
      *Correction:* #m.at("correction", default: "N/A")
    ])
  } else { text(fill: c-error)[Unknown Mistake: #id] }
}

#let lecture(id) = {
  if id in KB.lecs {
    let l = KB.lecs.at(id)
    card(l.at("title", default: id), "🎓", black, [
      *Date:* #l.at("date", default: "N/A") \
      *Topics:* #l.at("definition_ids", default: ()).join(", ")
    ])
  } else { text(fill: c-error)[Unknown Lecture: #id] }
}

#let tutorial(id) = {
  if id in KB.tuts {
    let t = KB.tuts.at(id)
    card(t.at("title", default: id), "✍️", black, [
      *Focus:* #t.at("content", default: "Practice Session")
    ])
  } else { text(fill: c-error)[Unknown Tutorial: #id] }
}

#let eval-scope = (def: def, tool: tool, ex: ex, mistake: mistake, lecture: lecture, tutorial: tutorial)

// --- 5. SMART QUESTION RENDERER ---
#let question(id) = {
  if id in KB.questions {
    let q = KB.questions.at(id)
    
    // Outer Container
    block(
      width: 100%, 
      breakable: true,
      stroke: (bottom: 0.5pt + c-gray.lighten(50%)),
      inset: (bottom: 2em),
      {
        // 1. HEADER
        grid(
          columns: (1fr, auto),
          align: (left, right),
          stack(dir: ltr, spacing: 0.5em,
            meta-tag(q.at("topic", default: "General"), c-primary),
            meta-tag(str(q.at("year", default: "N/A")), c-gray)
          ),
          text(style: "italic", fill: c-gray, size: 0.9em)[#q.at("lecturer", default: "Unknown")]
        )
        v(1em)

        // 2. BODY
        stack(dir: ttb, spacing: 0.8em,
          // Given
          if q.at("given", default: "") != "" {
            // NEW (Fixed)
            block(
              stroke: (left: 2pt + c-gray), 
              inset: (left: 0.5em)
            )[
              *Given:* #eval(q.given, mode: "markup", scope: eval-scope)
            ]
          },
          // Image (FIXED: Direct flow + White BG for visibility)
          if q.at("image", default: none) != none and q.at("image") != "" {
             align(center, 
               box(
                 fill: white, 
                 inset: 10pt, 
                 radius: 4pt, 
                 stroke: 0.5pt + gray,
                 image("/data/images/" + q.at("image"), width: 60%)
               )
             )
          },
          // To Prove
          if q.at("to_prove", default: "") != "" {
             pad(left: 0.5em)[
              *To Prove:* #eval(q.to_prove, mode: "markup", scope: eval-scope)
             ]
          }
        )
        v(0.5em)

        // 3. HINT
        let hint = q.at("hint", default: none)
        if hint != none {
          block(
            fill: luma(250), 
            stroke: (dash: "dashed", paint: c-gray), 
            inset: 8pt, 
            radius: 4pt, 
            width: 100%
          )[
            *Hint:* #eval(hint, mode: "markup", scope: eval-scope)
          ]
        }

        // 4. SOLUTION (Timeline)
        context if show_solutions.get() {
          let steps = q.at("answer_steps", default: ())
          if type(steps) == array and steps.len() > 0 {
            v(1.5em)
            text(fill: c-success, weight: "bold")[Official Solution]
            v(0.5em)
            
            // Timeline Loop
            stack(dir: ttb, spacing: 0em, ..steps.map(step => {
              grid(
                columns: (2em, 1fr),
                // Left: Line & Dot
                align(center + top)[
                  #place(circle(radius: 3pt, fill: c-success), dy: 0.4em)
                  #line(start: (0pt, 0.4em), end: (0pt, 100% + 1em), stroke: (paint: c-success.lighten(60%), thickness: 1pt))
                ],
                // Right: Content
                pad(bottom: 1.5em)[
                   *#step.at("title", default: "Step")* #h(0.5em) 
                   #text(style: "italic", fill: c-gray)[(#step.at("type", default: "logic"))]
                   #v(0.3em)
                   #eval(step.at("content", default: ""), mode: "markup", scope: eval-scope)
                ]
              )
            }))
          }
        }
      }
    )
  } else {
    text(fill: c-error)[Unknown Question ID: #id]
  }
}