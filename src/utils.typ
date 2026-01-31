#let img(filename) = image("/assets/images/" + filename)
#let ddx(f) = $ frac(d, dx) #f $
#let iso = $ tilde.equiv $

#let dot-pattern(spacing: 5mm, color: luma(220)) = tiling(size: (spacing, spacing))[
  #place(center + horizon, circle(radius: 0.5pt, fill: color))
]