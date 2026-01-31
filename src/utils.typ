// src/utils.typ

// Helper for absolute image paths from the project root.
#let img(filename) = image("/assets/images/" + filename)

// A semantic helper for creating a styled hint box.
#let hint-box(body) = block(
  fill: yellow.lighten(80%),
  inset: 8pt,
  radius: 4pt,
  width: 100%,
  body,
)

// A mathematical helper for rendering a derivative.
#let ddx(f) = $ frac(d, "dx") #f $
