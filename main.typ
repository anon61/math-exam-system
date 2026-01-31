#import "src/lib.typ": get-questions, render-worksheet, render-hints, exam-doc

// Apply the Template
#show: doc => exam-doc(title: "Real Analysis Midterm", doc)

// Configuration
#let filter = (:)

// Execution (Note the '/' at the start of the path)
#let questions = get-questions("/data/questions.yaml", query: filter)

#render-worksheet(questions)
#render-hints(questions)