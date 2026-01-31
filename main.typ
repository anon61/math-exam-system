#import "src/lib.typ": get-questions, render-worksheet, render-hints

// Define Query (Empty = Show All)
#let filter = (:)

// Load & Render
#let questions = get-questions("/data/questions.yaml", query: filter)
#render-worksheet(questions)
#render-hints(questions)