// main.typ
// This is the main entry point for rendering a specific exam PDF.

#import "src/lib.typ": get-questions, render-worksheet, render-hints

// --- Configuration ---
// Define a query to filter the question database.
// An empty filter selects all questions.
#let filter = (:) 

// --- Execution ---
// 1. Load questions from the YAML database using the filter.
#let questions = get-questions("/data/questions.yaml", query: filter)

// 2. Render the filtered questions into a worksheet.
#render-worksheet(questions)

// 3. Render the hints page at the end of the document.
#render-hints(questions)
