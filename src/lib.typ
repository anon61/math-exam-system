// src/lib.typ
// This is the Logic Core of the exam system.

// Import the custom functions to create an evaluation scope.
#import "utils.typ"

// CRITICAL: Create a scope dictionary from the `utils` module.
// This allows us to pass our custom functions (`ddx`, `hint-box`, etc.)
// into the `eval()` function for use within the YAML strings.
#let eval-scope = dictionary(utils)

// Loads and filters the question database.
#let get-questions(path, query: (:)) = {
  // Load the entire question bank from the YAML file.
  let questions = yaml(path)

  // Filter the questions based on the provided query.
  // The query is a dictionary where keys are metadata fields (e.g., "year")
  // and values are the desired match (e.g., 2024).
  return questions.filter(q => {
    var passes = true
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

// Renders a list of questions into a worksheet format.
#let render-worksheet(questions) = {
  // Display the number of questions found.
  heading(level: 1, numbering: none)[Worksheet]
  text(size: 8pt)[Generated on #datetime.today().display() with #questions.len() questions.]
  
  // Use a numbered list for the questions.
  counter(heading).update(0)
  counter("worksheet-q").update(0)

  for q in questions {
    // Increment question counter and display in a heading.
    pagebreak(weak: true)
    heading(level: 2, numbering: "1.", "Question #" + str(counter("worksheet-q").step()))

    // The core of the system:
    // Evaluate the Typst string from the YAML file's 'body' field.
    // We MUST pass the `eval-scope` so it knows what `ddx` means.
    eval(q.body, mode: "markup", scope: eval-scope)

    // Also evaluate the 'hint' field.
    eval(q.hint, mode: "markup", scope: eval-scope)

    // Display metadata for reference.
    align(right, text(size: 7pt, fill: gray)[
      ID: #q.id | Year: #q.year | Topic: #q.topic
    ])
  }
}
