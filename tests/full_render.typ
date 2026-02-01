#import "../src/lib.typ": *

#set page(paper: "a4", margin: 1cm)
#set text(font: "Times New Roman", size: 10pt)

= 🛡️ Full Database Render Test
_This document renders every node to ensure no runtime errors._

== 1. Definitions
#for (id, val) in KB.defs {
  [#strong(id): ] 
  def(id)
  parbreak()
}

== 2. Tools (Theorems)
#for (id, val) in KB.tools {
  [#strong(id): ]
  tool(id)
  parbreak()
}

== 3. Examples
#for (id, val) in KB.ex {
  [#strong(id): ]
  ex(id)
  parbreak()
}

== 4. Mistakes
#for (id, val) in KB.err {
  [#strong(id): ]
  mistake(id)
  parbreak()
}

== 5. Questions
#for (id, val) in KB.questions {
  v(1em)
  text(weight: "bold")[Rendering #id:]
  question(id)
}
