# autostereogram.py

Small Python program to generate stereograms, also called [Single Image Random Dot Stereogram (SIRDS)][1].

Originally written in January 2011. Uses Python 2 and [PIL][].

If I ever touch this repository again, I should update it to Python 3, replace `getopt` with `argparse`, and use [Pillow][] instead of `PIL`. I may even consider rewriting it in JavaScript using canvas.

## Related projects

* <https://magic-image.appspot.com/> <https://github.com/cobalys/MagicImage> uses this code behind its web interface.

[1]: https://en.wikipedia.org/wiki/Autostereogram
[PIL]: http://www.pythonware.com/products/pil/
[Pillow]: https://python-pillow.org/
