# -*- coding: utf-8 -*-

"""
legofy.palettes
---------------

This module contains the `lego` palette mappings.

Color mapping source;
 - http://www.brickjournal.com/files/PDFs/2010LEGOcolorpalette.pdf


    USAGE:
    $ legofy.palettes.legos

See README for project details.
"""
from __future__ import division


LEGOS = {
    'bw': {
        'A': [  0,   0,   0],
        'B': [ 60,  60,  60],
        'C': [110, 110, 110],
        'D': [180, 180, 180],
        'E': [255, 255, 255],
        },

    'solid': {
        'A' : [0, 0, 0],
        'B' : [60,60,60],
        'C' : [110,110,110],
        'D' : [180,180,180],
        'E' : [255, 255, 255],
        'F' : [250, 224, 197],
        'G' : [232, 165, 121],
        'H' : [255, 229, 69],
        'I' : [125, 69, 16],
        'J' : [84, 54, 41],
        'K' : [252, 184, 226],
        'L' : [214, 21, 105],
        'M' : [159, 212, 68],
        'N' : [77, 219, 255],
        'O' : [22, 114, 181]
        },           

    'portrait': {
        'A' : [0, 0, 0],
        'B' : [60,60,60],
        'C' : [110,110,110],
        'D' : [180,180,180],
        'E' : [255, 255, 255],
        'F' : [250, 224, 197],
        'G' : [232, 165, 121],
        'H' : [255, 229, 69],
        'I' : [125, 69, 16],
        'J' : [84, 54, 41],
        'K' : [252, 184, 226],
        'N' : [77, 219, 255],
        'O' : [22, 114, 181]
        },  

    'art': {
        'H' : [255, 229, 69],
        'K' : [252, 184, 226],
        'L' : [214, 21, 105],
        'M' : [159, 212, 68],
        'N' : [77, 219, 255],
        'O' : [22, 114, 181]
        }, 
    }

substitutes = {
        'A': 'B',
        'B': 'A',
        'C': 'B',
        'D': 'C',
        'E': 'D',
        'F': 'M',
        'G': 'G',
        'H': 'I',
        'I': 'H',
        'J': 'E',
        'K': 'J',
        'L': 'K',
        'M': 'L',
        'N': 'O',
        'O': 'N',
        'P': 'N',
        'Q': 'H',
        'R': 'S',
        'S': 'R',
        'T': 'U',
        'U': 'T',
        'V': 'U',
        'W': 'R'
    }


def extend_palette(palette, colors=256, rgb=3):
    """Extend palette colors to 256 rgb sets."""
    missing_colors = colors - len(palette)//rgb
    if missing_colors > 0:
        first_color = palette[:rgb]
        palette += first_color * missing_colors
    return palette[:colors*rgb]


def legos():
    """Build flattened lego palettes."""
    return _flatten_palettes(LEGOS.copy())


def _flatten_palettes(palettes):
    """Convert palette mappings into color list."""
    flattened = {}
    palettes = _merge_palettes(palettes)
    for palette in palettes:
        flat = [i for sub in palettes[palette].values() for i in sub]
        flattened.update({palette: flat})
    return flattened


def _merge_palettes(palettes):
    """Build unified palette using all colors."""
    unified = {}
    for palette in palettes:
        for item in palettes[palette]:
            unified.update({item: palettes[palette][item]})
    palettes.update({'all': unified})
    return palettes
