// src/utils.typ
// UI Components & Helper Functions

#let img(filename) = image("/assets/images/" + filename)
#let ddx(f) = $ frac(d, dx) #f $
#let iso = $ tilde.equiv $

#let dot-pattern(spacing: 5mm, color: luma(220)) = tiling(size: (spacing, spacing))[
  #place(center + horizon, circle(radius: 0.5pt, fill: color))
]

#let dot-grid(spacing: 5mm, color: luma(220)) = {
  rect(width: 100%, height: 100%, fill: dot-pattern(spacing: spacing, color: color))
}

// --- SMART SNAKE-LAYOUT GRAPH ---
// Wraps nodes into rows of 3. 
// Alternates LTR -> RTL -> LTR to keep the flow continuous.
#let proof-flow(nodes) = {
  let row-size = 3
  let node-style(label) = rect(
    width: 100%, // fixed width for uniformity
    height: auto,
    inset: 10pt,
    radius: 4pt,
    fill: white,
    stroke: 1pt + rgb("#1d3557"),
    align(center + horizon, text(size: 8pt, weight: "bold", fill: rgb("#1d3557"))[#label])
  )
  
  let arrow-right = align(center + horizon, text(size: 14pt, fill: luma(150))[$ arrow.r $])
  let arrow-left = align(center + horizon, text(size: 14pt, fill: luma(150))[$ arrow.l $])
  let arrow-down = text(size: 14pt, fill: luma(150))[$ arrow.b $]

  // Partition nodes into rows
  let rows = ()
  let current-row = ()
  for (i, node) in nodes.enumerate() {
    current-row.push(node)
    if current-row.len() == row-size or i == nodes.len() - 1 {
      rows.push(current-row)
      current-row = ()
    }
  }

  let flow-visuals = ()
  
  for (r_idx, row-nodes) in rows.enumerate() {
    let direction = if calc.even(r_idx) { "ltr" } else { "rtl" }
    
    // Build the horizontal row
    let row-items = ()
    for (n_idx, label) in row-nodes.enumerate() {
      // Add Node
      row-items.push(node-style(label))
      
      // Add Arrow (if not last in row)
      if n_idx < row-nodes.len() - 1 {
        if direction == "ltr" { row-items.push(arrow-right) }
        else { row-items.push(arrow-left) }
      }
    }
    
    // If RTL, we must reverse the visual stack order (but logic remains RTL)
    if direction == "rtl" {
        row-items = row-items.rev()
    }

    // Add the Row to the main container
    flow-visuals.push(
      grid(
        columns: (1fr, auto, 1fr, auto, 1fr), // 3 nodes + 2 arrows max
        align: horizon,
        gutter: 5pt,
        ..row-items
      )
    )

    // Add Vertical Connector (if not last row)
    if r_idx < rows.len() - 1 {
      // Connector logic: 
      // If LTR -> Down arrow on RIGHT side
      // If RTL -> Down arrow on LEFT side
      let align-dir = if direction == "ltr" { right } else { left }
      flow-visuals.push(
        block(width: 100%, align(align-dir, pad(x: 12%, arrow-down)))
      )
    }
  }

  // Render the whole snake
  block(
    width: 100%,
    inset: 10pt,
    stack(dir: ttb, spacing: 5pt, ..flow-visuals)
  )
}