#import "../src/lib.typ": eval-scope

#let questions = yaml("../data/questions.yaml")

#print("Validating " + str(questions.len()) + " questions...")

#for (i, q) in questions.enumerate() {
  let q_id = q.at("id", default: "Index " + str(i))

  // 1. CRITICAL: Enforce The Generalized Schema Structure
  let required_fields = ("topic", "tools", "common_mistakes", "year", "lecturer")
  
  for field in required_fields {
    if field not in q {
      panic("SCHEMA VIOLATION in [" + q_id + "]: Missing mandatory field '" + field + "'")
    }
  }

  // 2. Validate Math Content
  if "given" in q and q.given != none { 
    let _ = eval(q.given, mode: "markup", scope: eval-scope) 
  }
  
  if "to_prove" in q and q.to_prove != none { 
    let _ = eval(q.to_prove, mode: "markup", scope: eval-scope) 
  }
  
  if "hint" in q and q.hint != none { 
    let _ = eval(q.hint, mode: "markup", scope: eval-scope) 
  }
}

#text(fill: green, weight: "bold")[
  ✓ SUCCESS: All questions adhere to the Generalized Schema.
]