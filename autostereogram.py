#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt
import os.path
import sys

import numpy
import PIL.Image


SCRIPTNAME = __file__


class ProgramOptions(object):
    '''Holds the program options.'''

    def __init__(self):
        self.args = []

        self.depthmap_filename = ''
        self.pattern_filename = ''
        self.output_filename = ''

        # Direction is either +1 for wall-eyed or -1 for cross-eyed
        self.dir = 1
        self.pattern_width = 140
        #self.scale = 0.25
        self.scale = 0.125

        self.debug = False
        self.print_warnings = True


available_parameters = [
    ('', '', '\nFile input/output options:'),
    ('o:', 'output=',  'Save the output image file '
                       '(if omitted, it will only be displayed on screen)'),
    ('p:', 'pattern=', 'Image file to use as a repeating pattern '
                       '(if omitted, a random pattern will be generated)'),
    ('', '', '\nStereogram options:'),
    ('w:', 'width=',   'Set the width of the repeating pattern (default: 140 pixels)'),
    ('s:', 'scale=',   'Scale the depth image pixel values (default: 0.125)'),
    ('c',  'cross',    'Generate a cross-eyed stereogram (default is wall-eyed)'),
    ('', '', '\nPrinting options:'),
    ('h',  'help',     'Print help'),
    ('q',  'quiet',    'Don\'t print warnings'),
    ('',   'debug',    'Print extra debugging output'),
]


def parse_parameters(argv, opt):
    '''Receives the parameters as 'argv', parses and stores them into 'opt'.
    Returns nothing.
    Calls sys.exit() and/or print_help() if needed.

    argv should be sys.argv[1:]
    opt should be an instance of ProgramOptions()
    '''

    # Using getopt to parse the parameters:
    try:
        opts, args = getopt.getopt(
            argv,
            ''.join(short for short,x,y in available_parameters),
            [long for x,long,y in available_parameters if long]
        )
    except getopt.GetoptError as e:
        print(SCRIPTNAME + ': ' + str(e))
        print(SCRIPTNAME + ': Use --help for usage instructions.')
        sys.exit(2)

    # And now storing the parameters at 'opt'
    for o,v in opts:
        if o in ('-o', '--output'):
            opt.output_filename = v
        elif o in ('-p', '--pattern'):
            opt.pattern_filename = v

        elif o in ('-w', '--width'):
            opt.pattern_width = int(v)
        elif o in ('-s', '--scale'):
            opt.scale = float(v)
        elif o in ('-c', '--cross'):
            opt.dir = -1

        elif o in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif o in ('-q', '--quiet'):
            opt.print_warnings = False
        elif o == '--debug':
            opt.debug = True

        else:
            print(SCRIPTNAME + ': Invalid parameter: {0}'.format(o))
            print(SCRIPTNAME + ': Use --help for usage instructions.')
            sys.exit(2)

    opt.args = args

    if len(args) == 0:
        print(SCRIPTNAME + ': Missing filename')
        print(SCRIPTNAME + ': Use --help for usage instructions.')
        sys.exit(2)
    elif len(args) == 1:
        opt.depthmap_filename = args[0]
    elif len(args) > 1:
        print(SCRIPTNAME + ': Only one filename is accepted, but multiple were passed.')
        print(SCRIPTNAME + ': Use --help for usage instructions.')
        sys.exit(2)


def print_help():
    print('Usage: {0} [options] depthmap.png'.format(SCRIPTNAME))
    print('Creates a "Single Image Random Dot Stereogram (SIRDS)" based on input image.')

    long_length = 2 + max(len(long) for x,long,y in available_parameters)
    for short, long, desc in available_parameters:
        if short or long:
            if short and long:
                comma = ', '
            else:
                comma = '  '

            if short == '':
                short = '  '
            else:
                short = '-' + short[0]

            if long:
                long = '--' + long

            print('  {0}{1}{2:{3}}  {4}'.format(
                short, comma, long, long_length, desc
            ))
        else:
            print(desc)


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


def make_stereogram(options):
    '''Receives a ProgramOptions() instance, and do all the hard work!'''
    # Handy alias:
    o = options

    # Sanity check
    if( o.print_warnings
    and round(255 * o.scale) >= o.pattern_width
    ):
        print(SCRIPTNAME +
            ': WARNING! "pattern_width" is too small for current "scale".'
        )

    # Loading the depth image
    depthmap_img = PIL.Image.open(o.depthmap_filename)

    # Converting to grayscale
    if( o.print_warnings
    and depthmap_img.mode != 'L'
    ):
        print(SCRIPTNAME + 
            ': Warning! Converting "{0}" to grayscale.'
            .format(o.depthmap_filename)
        )
    depthmap_img = depthmap_img.convert('L')

    # Loading the pattern image
    if o.pattern_filename:
        pattern_img = PIL.Image.open(o.pattern_filename)

        if( o.print_warnings
        and pattern_img.size[0] < o.pattern_width
        ):
            print(SCRIPTNAME +
                ': WARNING! "{0}" width is less than "pattern_width".'
                .format(o.pattern_filename)
            )
    # Or generating a random pattern
    else:
        pattern_img = random_image((o.pattern_width, depthmap_img.size[1]))

    # Creating the output image
    output_img = PIL.Image.new('RGB',
        (depthmap_img.size[0] + o.pattern_width, depthmap_img.size[1])
    )

    # Copying the pattern to the left side of the output image
    y = 0
    while y < output_img.size[1]:
        output_img.paste(pattern_img, (0,y))
        y += pattern_img.size[1]

    # The pixel access objects, with indexes [x,y]
    depth = depthmap_img.load()
    out = output_img.load()

    # Iterating over other pixels to generate the stereogram
    for y in xrange(0, depthmap_img.size[1]):
        for x in xrange(0, depthmap_img.size[0]):
            # Find the source pixel
            sx = round(x + o.dir * o.scale * depth[x,y])
            if sx < 0:
                # In Python: -3 % 10 => 7
                sx = sx % o.pattern_width

            if o.debug:
                print("x,y=%3d,%3d depth=%3d out[%3d,%3d]=out[%3d,%3d]" % (
                    x,y, depth[x,y],
                    x + o.pattern_width, y,
                    sx, y
                ))

            # Copy the pixel
            out[x + o.pattern_width, y] = out[sx, y]

        # Fill out any remaining horizontal space.
        # Actually, this loop won't run.
        x += 1
        while x + o.pattern_width < output_img.size[0]:
            out[x + o.pattern_width, y] = out[x, y]
            x += 1

    # Save or show the final image
    if o.output_filename:
        output_img.save(o.output_filename)
    else:
        output_img.show()


def main(argv):
    global SCRIPTNAME
    SCRIPTNAME = os.path.basename(sys.argv[0])

    opt = ProgramOptions()
    parse_parameters(argv[1:], opt)

    make_stereogram(opt)


if __name__ == "__main__":
    main(sys.argv)
