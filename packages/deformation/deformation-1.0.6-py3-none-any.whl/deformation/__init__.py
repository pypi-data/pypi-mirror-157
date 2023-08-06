#!/usr/bin/env python3

"""
** Simply and efficiently apply a warp chain to an image. **
------------------------------------------------------------

In general, this makes it possible to deform an image
in one direction and in the other but also to transfer boundins boxes from one space to another.
You only need to define a few methods to have access to all the transformations,
which considerably reduces the amount of code.
This module is based on opencv for performance issues.
But unlike opencv, this module deals with the following points:

* Transformation in both directions. *usefull for bounding-boxes*
* Translation to avoid cropping the image and automatic resizing to avoid borders.
* Simplification of the calculation when chaining transformations to avoid intermediate images.

Class diagram
-------------

.. figure:: http://python-docs.ddns.net/deformation/classes.png

Examples
--------
>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> import deformation
>>>
>>> image = np.zeros((12, 20), dtype=np.uint8)
>>> _sum = sum(np.meshgrid(np.arange(image.shape[0]), np.arange(image.shape[1]), indexing='ij'))
>>> image[_sum % 2 == 1] = 255 # mini checkerboard
>>> image = np.kron(image, np.ones((20, 20), dtype=np.uint8)) # normal checkerboard
>>>
>>> rot = deformation.Rotation(np.deg2rad(30), src_shape=image.shape, crop_and_pad=True)
>>> rot
Rotation(30*pi/180, center=(100, 373))
>>> rot.reverse()
Rotation(-30*pi/180, center=(100, 373))
>>> dst_image = rot(image)
>>>
>>> _ = plt.subplot(1, 2, 1)
>>> _ = plt.imshow(image, cmap='gray')
>>> _ = plt.subplot(1, 2, 2)
>>> _ = plt.imshow(dst_image, cmap='gray')
>>> plt.savefig('example.png')
>>>

This gives the following result:

.. figure:: http://python-docs.ddns.net/deformation/example.png
"""

from deformation.core import Transform, AbstractTransform, IdentityTransform
from deformation.poly import PolyTransform, TorchPoly, NotSolvableError
from deformation.perspective import get_perspective_transform, PerspectiveTransform
from deformation.affine import AffineTransform
from deformation.rotation import Rotation
from deformation.doc import make_pdoc


__all__ = [
    'Transform', 'AbstractTransform', 'IdentityTransform',
    'PolyTransform', 'TorchPoly', 'NotSolvableError',
    'get_perspective_transform', 'PerspectiveTransform',
    'AffineTransform',
    'Rotation',
]
__author__ = 'Robin RICHARD (robinechuca) <serveurpython.oz@gmail.com>'
__license__ = 'GNU Affero General Public License v3 or later (AGPLv3+)'
__pdoc__ = make_pdoc(__all__, locals())
__version__ = '1.0.6'
