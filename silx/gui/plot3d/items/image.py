# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""This module provides 2D data and RGB(A) image item class.
"""

from __future__ import absolute_import

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "15/11/2017"

import numpy

from ..scene import primitives
from .core import DataItem3D, ItemChangedType
from .mixins import ColormapMixIn, InterpolationMixIn


class ImageData(DataItem3D, ColormapMixIn, InterpolationMixIn):
    """Description of a 2D image data.

    :param parent: The View widget this item belongs to.
    """

    def __init__(self, parent=None):
        DataItem3D.__init__(self, parent=parent)
        ColormapMixIn.__init__(self)
        InterpolationMixIn.__init__(self)

        self._data = numpy.zeros((0, 0), dtype=numpy.float32)

        self._image = primitives.ImageData(self._data)
        self._getScenePrimitive().children.append(self._image)

        # Connect scene primitive to mix-in class
        ColormapMixIn._setSceneColormap(self, self._image.colormap)
        InterpolationMixIn._setPrimitive(self, self._image)

    def setData(self, data, copy=True):
        """Set the image data to display.

        The data will be casted to float32.

        :param numpy.ndarray data: The image data
        :param bool copy: True (default) to copy the data,
                          False to use as is (do not modify!).
        """
        self._image.setData(data, copy=copy)
        ColormapMixIn._setRangeFromData(self, self.getData(copy=False))
        self._updated(ItemChangedType.DATA)

    def getData(self, copy=True):
        """Get the image data.

        :param bool copy:
            True (default) to get a copy,
            False to get internal representation (do not modify!).
        :rtype: numpy.ndarray
        :return: The image data
        """
        return self._image.getData(copy=copy)


class ImageRgba(DataItem3D, InterpolationMixIn):
    """Description of a 2D data RGB(A) image.

    :param parent: The View widget this item belongs to.
    """

    def __init__(self, parent=None):
        DataItem3D.__init__(self, parent=parent)
        InterpolationMixIn.__init__(self)

        self._data = numpy.zeros((0, 0, 3), dtype=numpy.float32)

        self._image = primitives.ImageRgba(self._data)
        self._getScenePrimitive().children.append(self._image)

        # Connect scene primitive to mix-in class
        InterpolationMixIn._setPrimitive(self, self._image)

    def setData(self, data, copy=True):
        """Set the RGB(A) image data to display.

        Supported array format: float32 in [0, 1], uint8.

        :param numpy.ndarray data:
            The RGBA image data as an array of shape (H, W, Channels)
        :param bool copy: True (default) to copy the data,
                          False to use as is (do not modify!).
        """
        self._image.setData(data, copy=copy)
        self._updated(ItemChangedType.DATA)

    def getData(self, copy=True):
        """Get the image data.

        :param bool copy:
            True (default) to get a copy,
            False to get internal representation (do not modify!).
        :rtype: numpy.ndarray
        :return: The image data
        """
        return self._image.getData(copy=copy)
