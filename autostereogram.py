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
    # Autostereogram parameters
    pattern_width = 140
    # Direction is either +1 or -1
    # It selects between cross-eyed and wall-eyed
    dir = +1

    # Loading the depth image
    depth_img = PIL.Image.open('depthmap.png').convert('L')

    # TODO: Someday, allow loading an image as the repeating pattern
    pattern_img = random_image((pattern_width, depth_img.size[1]))
    pattern_img.save('pattern.png')  # DEBUG-only
    #pattern_img.show()  # DEBUG-only

    # Creating the output image
    out_img = PIL.Image.new('RGB',
        (depth_img.size[0] + 2*pattern_width, depth_img.size[1])
    )

    # The pixel access objects, with indexes [x,y]
    depth = depth_img.load()
    pattern = pattern_img.load()
    out = out_img.load()

    # Generating the output image
    out_img.paste(pattern_img, (0,0))

    for y in xrange(0, out_img.size[1]):
        for x in xrange(pattern_width, out_img.size[0]):
            # FIXME! Out-of-bounds on "x-pattern_width"
            out[x,y] = out[x-pattern_width, y]

    # Saving the final image
    out_img.save('out.png')
    out_img.show()  # DEBUG-only ?


if __name__ == "__main__":
    main()
