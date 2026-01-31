// Comprehensive Test Suite

#import "/src/lib.typ": get-questions, render-worksheet, render-hints
#import "/src/utils.typ": *

#let test-heading(body) = {
  text(weight: "bold", fill: blue, body)
  line(length: 100%)
  v(1em)
}

// --- Test `get-questions` ---
#test-heading("Testing `get-questions` function")

// Test 1: Load all questions from the test suite file
#let all-test-questions = get-questions("/data/test_suite_questions.yaml")
#assert.eq(all-test-questions.len(), 4, message: "Should load all 4 questions from the test suite.")

// Test 2: Apply a query that returns one question
#let single-result = get-questions("/data/test_suite_questions.yaml", query: (year: 2022))
#assert.eq(single-result.len(), 1, message: "Query for year 2022 should return 1 question.")
#assert.eq(single-result.first().id, "FILTER-2022", message: "Query for year 2022 should return the correct question.")

// Test 3: Apply a query that returns multiple questions
#let multi-result = get-questions("/data/test_suite_questions.yaml", query: (lecturer: "Dr. Test"))
#assert.eq(multi-result.len(), 3, message: "Query for lecturer 'Dr. Test' should return 3 questions.")

// Test 4: Apply a query that returns no questions
#let no-results = get-questions("/data/test_suite_questions.yaml", query: (topic: "Non-existent Topic"))
#assert.eq(no-results.len(), 0, message: "Query for a non-existent topic should return 0 questions.")

// Test 5: Load from an empty YAML file
#let empty-questions = get-questions("/data/empty_questions.yaml")
#assert.eq(empty-questions.len(), 0, message: "Loading from an empty YAML file should result in an empty list.")

#text(fill: green, "All `get-questions` tests passed!")
#v(2em)


// --- Test Rendering Functions ---
#test-heading("Testing Rendering Functions (for crash-safety)")

// Test 6: Render a full worksheet and hints page.
// This is not a visual test, but it ensures the functions don't crash
// with valid, varied data.
#let _ = {
  render-worksheet(all-test-questions)
  render-hints(all-test-questions)
}

// Test 7: Render with an empty list of questions.
// This tests the guard clauses.
#let _ = {
  render-worksheet(())
  render-hints(())
}

// Test 8: Render a single question with missing fields.
#let question-missing-prove = get-questions("/data/test_suite_questions.yaml", query: (id: "MISSING-PROVE"))
#let _ = {
  render-worksheet(question-missing-prove)
}

#text(fill: green, "All rendering functions compiled without errors!")
#v(2em)

#rect(width: 100%, fill: green, inset: 8pt, radius: 4pt, text(white, weight: "bold", align(center, "ALL TESTS PASSED")))
