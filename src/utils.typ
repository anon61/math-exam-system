// src/utils.typ
// UI Components & Helper Functions

#let img(filename) = image("/assets/images/" + filename)
#let ddx(f) = $ frac(d, dx) #f $
#let iso = $ tilde.equiv $

// 1. Dot Pattern (Returns the raw tiling for 'fill')
#let dot-pattern(spacing: 5mm, color: luma(220)) = tiling(size: (spacing, spacing))[
  #place(center + horizon, circle(radius: 0.5pt, fill: color))
]

// 2. Dot Grid (Returns a filled rect for 'background')
#let dot-grid(spacing: 5mm, color: luma(220)) = {
  rect(width: 100%, height: 100%, fill: dot-pattern(spacing: spacing, color: color))
}

// 3. Grading Ladder (Vertical Stack for Margins)
// This renders a clean vertical strip 0-10 that fits perfectly in the margin.
#let grading-ladder(max-points: 10) = {
  let cells = range(0, max-points + 1).map(n => {
    box(
      width: 1.5em, 
      height: 1.2em, 
      stroke: (bottom: 0.5pt + luma(200)), 
      align(center + horizon, text(size: 8pt, fill: luma(150))[#n])
    )
  })
  // Stack vertically
  block(
    stroke: 0.5pt + luma(200),
    radius: 4pt,
    clip: true,
    stack(dir: ttb, ..cells)
  )
}

// 4. Margin Note Helper
#let margin-cue(body) = {
  place(left, dx: -52mm, block(width: 45mm, align(right, body)))
}