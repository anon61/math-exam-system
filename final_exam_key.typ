
#import "/src/lib.typ": *

#show_solutions.update(true)

#set page(
  paper: "a4", 
  margin: 2cm,
  header: align(right)[
    *Math Exam Generated on #datetime.today().display()*
  ]
)
#set text(font: "Times New Roman", size: 11pt)

= Exam: General (KEY)

== Question 1
#question("qn-calc-integral")

== Question 2
#question("qn-comb-pascal")

== Question 3
#question("qn-complex-roots")

== Question 4
#question("qn-limit-proof")

== Question 5
#question("qn-limit-squeeze")

== Question 6
#question("qn-linalg-eigen")

== Question 7
#question("qn-logic-imply")

== Question 8
#question("qn-series-ratio")

== Question 9
#question("qn-vec-dot")

== Question 10
#question("qn-set-demorgan")

== Question 11
#question("qn-top-open")



#v(2em)
#align(center)[*End of Examination*]
