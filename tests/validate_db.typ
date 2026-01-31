// tests/validate_db.typ
#import "../src/lib.typ": eval-scope

#let questions = yaml("../data/questions.yaml")

#text(fill: green)[
  Database Integrity Check: PASSED
]

#line(length: 100%)
#v(8pt)

Total questions validated: #questions.len()

#for q in questions {
  // Validate 'given' if it exists and is not empty
  if "given" in q and q.given != none { 
    eval(q.given, mode: "markup", scope: eval-scope) 
  }
  
  // Validate 'to_prove' if it exists and is not empty
  if "to_prove" in q and q.to_prove != none { 
    eval(q.to_prove, mode: "markup", scope: eval-scope) 
  }
  
  // Validate 'body' if it exists (Legacy Schema)
  if "body" in q and q.body != none { 
    eval(q.body, mode: "markup", scope: eval-scope) 
  }

  // Validate 'hint'
  if "hint" in q and q.hint != none { 
    eval(q.hint, mode: "markup", scope: eval-scope) 
  }
}