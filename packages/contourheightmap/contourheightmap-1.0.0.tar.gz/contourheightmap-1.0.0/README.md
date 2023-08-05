# Contour Heightmap

A fast python library for generating contour maps from heightmaps and images.

Given an image file (preferably RGB PNG), it will output a PNG with contour lines and an SVG file of the contour lines. 

![Heightmap with contour lines](examples/heightmap_500x800.png "Contoured")
![Heightmap with contour lines](examples/heightmap_500x800_contour.png "Contoured")



![Heightmap with contour lines](examples/snowdon.png "Contoured")
![Heightmap with contour lines](examples/snowdon_contour.png "Contoured")


# Quick Start

## How do I contour an image?

```python
from contourheightmap import ContourHeightmap

c = ContourHeightmap()
c.contour("path/to/heightmap.png")
```

Result will be in output.png and output.svg


## How do I provide an output filename?
```python
from contourheightmap import ContourHeightmap

c = ContourHeightmap()
c.contour("path/to/heightmap.png", "path/to/output.png")
```

Output will also be in path/to/output.svg

## How do I output a contoured image from the command line?

```bash
contourheightmap.sh examples/heightmap.png 
```

Result will be in output.png


