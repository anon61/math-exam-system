
#import "/src/lib.typ": *

#show_solutions.update(false)

#set page(
  paper: "a4", 
  margin: 2cm,
  header: align(right)[
    *Math Exam Generated on #datetime.today().display()*
  ]
)
#set text(font: "Times New Roman", size: 11pt)

= Exam: General

== Question 1
#question("q1")

== Question 2
#question("q2")



#v(2em)
#align(center)[*End of Examination*]
