// src/lib.typ

// 1. LOAD THE DATABASE
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