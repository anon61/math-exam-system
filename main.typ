// main.typ
// This is the main entry point for rendering a specific exam PDF.

#import "src/lib.typ": get-questions, render-worksheet

// --- Configuration ---
// Define a query to filter the question database.
// This will select all questions where the year is 2024 AND the topic is "Calculus".
#let filter = (year: 2024, topic: "Calculus")

// --- Execution ---
// 1. Load questions from the YAML database using the filter.
#let questions = get-questions("/data/questions.yaml", query: filter)

// 2. Render the filtered questions into a worksheet.
#render-worksheet(questions)
