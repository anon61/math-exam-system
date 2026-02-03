#import "src/lib.typ": get-questions, render-solutions, exam-doc

#show: doc => exam-doc(title: "Full Solution Key", doc)
// FIX: Added leading slash '/'
#let questions = get-questions("/data/questions.yaml")

#render-solutions(questions)

