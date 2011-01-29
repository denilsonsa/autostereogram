#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

from __future__ import division
from __future__ import print_function

import numpy
import PIL.Image


def random_image(dimensions):
    '''Returns a RGB image filled with random pixels.'''

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
    # Direction is either:
    # +1 for wall-eyed
    # -1 for cross-eyed
    dir = 1
    # This scale is multiplied by depth
    scale = 0.25

    DEBUG = False

    # Sanity check
    if round(255*scale) >= pattern_width:
        # Yeah! Half-Life reference in the warning message! :)
        print('WARNING! "pattern_width" is too small for current "scale". Prepare for unforseen consequences.')

    # Loading the depth image
    depth_img = PIL.Image.open('depthmap.png').convert('L')

    # TODO: Someday, allow loading an image as the repeating pattern
    #       And the loaded image must be wider than 'pattern_width'
    pattern_img = random_image((pattern_width, depth_img.size[1]))
    pattern_img.save('pattern.png')  # DEBUG-only
    #pattern_img.show()  # DEBUG-only

    # Creating the output image
    out_img = PIL.Image.new('RGB',
        (depth_img.size[0] + pattern_width, depth_img.size[1])
    )

    # The pixel access objects, with indexes [x,y]
    depth = depth_img.load()
    pattern = pattern_img.load()
    out = out_img.load()

    # Generating the output image
    out_img.paste(pattern_img, (0,0))

    for y in xrange(0, out_img.size[1]):
        for x in xrange(0, depth_img.size[0]):
            sx = round(x + dir*scale*depth[x,y])
            if sx < 0:
                # In Python: -3 % 10 => 7
                sx = sx % pattern_width

            if DEBUG:
                print("x,y=%3d,%3d depth=%3d out[%3d,%3d]=out[%3d,%3d]" % (
                    x,y, depth[x,y],
                    x + pattern_width, y,
                    sx, y
                ))

            out[x + pattern_width, y] = out[sx, y]

        # Fill out any remaining horizontal space.
        # Actually, this loop shouldn't run.
        x += 1
        while x + pattern_width < out_img.size[0]:
            out[x + pattern_width, y] = out[x, y]
            x += 1

    # Saving the final image
    out_img.save('out.png')
    out_img.show()  # DEBUG-only ?


if __name__ == "__main__":
    main()
