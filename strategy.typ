#import "src/lib.typ": get-questions, render-strategy, exam-doc

#show: doc => exam-doc(title: "Strategy Guide & Hints", doc)
// FIX: Added leading slash '/'
#let questions = get-questions("/data/questions.yaml")

#render-strategy(questions)