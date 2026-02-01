#import "../src/lib.typ": *

#set page(paper: "a4", margin: 2cm)
#set text(font: "Times New Roman", size: 11pt)

= Math Exam Engine Test
_Generated on #datetime.today().display()_

== Part A: System Check
- *Database Loaded:* #KB.questions.len() questions found.
- *Solutions Mode:* #if show-solutions [ON] else [OFF]

== Part B: Question Rendering
// Attempting to render the Limit Proof Question
#question("qn-limit-proof")

== Part C: Error Handling
// Attempting to render a non-existent question
#question("qn-missing-id")
