# SimpleSurface
A simpler version of Pycairo's ImageSurface

This package is an attempt to complement PyCairo's functionality by performing a lot of the heavy lifting needed for non-native functionality. A lot of the work is done behind the scenes, saving your keyboard undue wear and tear.

## Comparison Example

### Blue Ellipse using PyCairo
```
import cairo
import math

# Create 600x800 Surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 800)
context = cairo.Context(surface)

# Draw a blue ellipse with top-left corner at (50, 50) measuring 150x200 pixels
x = 50
y = 50
width = 150
height = 200

context.save()
context.translate(x + width / 2., y + height / 2.)
context.scale(width / 2., height / 2.)
context.set_source_rgb(0, 0, 1)
context.arc(0., 0., 1., 0., 2 * math.pi)
context.fill()
context.restore()

# Save as a PDF
pdf_surface = cairo.PDFSurface("example.pdf", 600, 800)
pdf_context = cairo.Context(pdf_surface)
pdf_context.set_source_surface(surface)
pdf_context.paint()
pdf_context.show_page()
```

### Blue Ellipse using SimpleSurface
```
import SimpleSurface

# Create 600x800 Surface
surface = SimpleSurface(600, 800)

# Draw a blue ellipse with top-left corner at (50, 50) measuring 150x200 pixels
surface.ellipse(50, 50, 150, 200, fill_color=(0, 0, 255))

# Save as a PDF
surface.write_to_pdf("example.pdf")
```
