// src/utils.typ
// This file acts as the API for your YAML strings.

// 1. Image Helper: Forces absolute paths
#let img(filename) = image("/assets/images/" + filename)

// 2. Hint Box: A styled container for hints
#let hint-box(body) = block(
  fill: yellow.lighten(80%),
  inset: 8pt,
  radius: 4pt,
  width: 100%,
  body
)

// 3. Math Macro: Derivative shorthand
#let ddx(f) = $ frac(d, dx) #f $

// 4. Math Symbol: Isomorphism shorthand (Fixes "unknown variable: iso")
#let iso = $ tilde.equiv $