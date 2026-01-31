// tests/validate_db.typ
// This script acts as a CI/CD check to ensure database integrity.
// It loads every question from the YAML file and attempts to evaluate
// both its `body` and `hint`.
// If any entry contains invalid Typst syntax, this script will fail to compile.

#import "../src/lib.typ": eval-scope

#let questions = yaml("../data/questions.yaml")

#text(fill: green)[
  Database Integrity Check: PASSED
]

#line(length: 100%)
#v(8pt)

Total questions validated: #questions.len()

// Loop through every single question in the database.
#for q in questions {
  // Try to evaluate the body. If the Typst is invalid, this will error out.
  eval(q.body, mode: "markup", scope: eval-scope)

  // Also try to evaluate the hint.
  eval(q.hint, mode: "markup", scope: eval-scope)
}

// If the script compiles successfully, it means all entries are valid.
// To test failure, introduce a syntax error into `questions.yaml`,
// for example, `\invalid-command`. The `typst compile` command on this
// file will then return a non-zero exit code.
