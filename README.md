# Generating Image Mosaics

This is the code associated with this [post](https://nickc92.github.io/general/2016/06/25/Image-Mosaics-and-Optimization.html).
It contains code to optimize image mosaics, and to render them at higher resolution.

## Usage

In `mosaic.py`, there are a few variables at the top to set:

```
DO_GREYSCALE = False        # render in greyscale
DO_GREYSCALE_MATCH = False  # do image matching in greyscale
TRANSPARENCY = 0.3          # transparency of tiles. 0=opaque
CIRCLE_DIV = 36             # tile rotation discretization = 360 deg / CIRCLE_DIV.
                            # set CIRCLE_DIV=1 for no rotations
TILE_LONG_SIDE = 55         # the longer edge of the tile will be sized to this many pixels
```

Then it is run as follows:

```
python mosaic.py target_image tile_image_dir
```

`mosaic.py` will consider all `.jpg` files in `tile_image_dir` to be candidate tiles.

As it is optimizing, it periodically will write an image file `result.jpg` that you can
examine.  It also creates a file, `plan.txt`, that is used in rendering.

### Rendering
You can create a higher-resolution version of your mosaic, using the `plan.txt` file that
`mosaic.py` outputs, for the purposes of printing or whatnot:

```
renderPlan.py repro_image planfile scale
```

* `repro_image` is generally the `result.jpg` that `mosaic.py` produces;
* `planfile` is generally `plan.txt` that `mosaic.py` produces;
* `scale`: if `repro_image` is $$N \times N$$ pixels, then the rendered image will be
$$(scale N) \times (scale N)$$ pixels.

`renderPlan.py` produces a file `render.jpg`.
