#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

from __future__ import division

import numpy
import PIL.Image


def mul(seq):
    return reduce(lambda x,y: x*y, seq)


def random_image(dimensions):
    # random_integers() returns a 'int64' array
    # But PIL expects a 'uint8' array
    # 
    # I also need to swap width and height in numpy
    r = numpy.array(
        numpy.random.random_integers(0, 255, (dimensions[1], dimensions[0], 3)),
        dtype='uint8'
    )
    img = PIL.Image.fromarray(r, mode="RGB")
    return img


def main():
    depth_img = PIL.Image.open('heightmap.png')

    # The tile_img doesn't need to be the same size as depth_img.
    # It just needs to be the same height. The width can be smaller.
#    tile_img = PIL.Image.new("RGB", depth_img.size)

    # The pixel access object, with indexes [x,y]
#    tile_pixels = tile_img.load()

    # Putting random data into the image:
#    arr = numpy.array(tile_img)
#    arr.put(
#        numpy.arange(arr.size),
#        numpy.random.random_integers(0, 255, arr.size)
#    )
#    tile_img.putdata(arr)

    tile_img = random_image(depth_img.size)
    tile_img.show()


if __name__ == "__main__":
    main()
