#import "src/lib.typ": get-questions, render-worksheet, exam-doc

#show: doc => exam-doc(title: "Real Analysis Exam", doc)
// FIX: Added leading slash '/' to make path absolute from project root
#let questions = get-questions("/data/questions.yaml")

#render-worksheet(questions)