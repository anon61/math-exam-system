// (Ensuring helper functions exist)

#let img(filename) = image("/assets/images/" + filename)

#let hint-box(body) = block(
  fill: yellow.lighten(80%),
  inset: 8pt,
  radius: 4pt,
  width: 100%,
  body
)

#let ddx(f) = $ frac(d, dx) #f $