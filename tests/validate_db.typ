#import "../src/lib.typ": eval-scope

#let questions = yaml("../data/questions.yaml")

#print("Validating " + str(questions.len()) + " questions...")

#for (i, q) in questions.enumerate() {
  let q_id = q.at("id", default: "Index " + str(i))

  // 1. CRITICAL: Enforce The Generalized Schema Structure
  // These fields are now MANDATORY. The build will fail without them.
  let required_fields = ("topic", "tools", "common_mistakes", "year", "lecturer")
  
  for field in required_fields {
    if field not in q {
      panic("SCHEMA VIOLATION in [" + q_id + "]: Missing mandatory field '" + field + "'")
    }
  }

  // 2. Validate Math Content (Prevent rendering crashes)
  // We wrap these in a check to ensure they aren't just empty strings
  if "given" in q and q.given != none { 
    let _ = eval(q.given, mode: "markup", scope: eval-scope) 
  }
  
  if "to_prove" in q and q.to_prove != none { 
    let _ = eval(q.to_prove, mode: "markup", scope: eval-scope) 
  }
  
  if "hint" in q and q.hint != none { 
    let _ = eval(q.hint, mode: "markup", scope: eval-scope) 
  }

  // 3. Logic Check
  if q.topic == "" or q.topic == none {
    panic("DATA ERROR in [" + q_id + "]: Topic cannot be empty.")
  }
}

#text(fill: green, weight: "bold")[
  ✓ SUCCESS: All questions adhere to the Generalized Schema.
]