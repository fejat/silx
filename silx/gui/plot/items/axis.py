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
"""This module provides the class for axes of the :class:`Plot`.
"""

__authors__ = ["V. Valls"]
__license__ = "MIT"
__date__ = "26/06/2017"

import logging
from ... import qt

_logger = logging.getLogger(__name__)


class Axis(qt.QObject):
    """Abstract axis class of the plot.

    States are half-stored on the backend of the plot, and half-stored on this
    object.

    TODO It would be good to store all the states of an axis in this object.
    """

    sigInvertedChanged = qt.Signal(bool)
    """Signal emitted when axis orientation has changed"""

    sigLogarithmicChanged = qt.Signal(bool)
    """Signal emitted when axis scale has changed"""

    sigAutoScaleChanged = qt.Signal(bool)
    """Signal emitted when axis autoscale has changed"""

    sigLimitsChanged = qt.Signal(float, float)
    """Signal emitted when axis autoscale has changed"""

    def __init__(self, plot):
        """Constructor

        :param silx.gui.plot.PlotWidget.PlotWidget plot: Parent plot of this
            axis
        """
        qt.QObject.__init__(self, parent=plot)
        self._isLog = False
        self._isAutoScale = True
        # Store default labels provided to setGraph[X|Y]Label
        self._defaultLabel = ''
        # Store currently displayed labels
        # Current label can differ from input one with active curve handling
        self._currentLabel = ''
        self._plot = plot

    def getLimits(self):
        """Get the limits of this axis.

        :return: Minimum and maximum values of this axis as tuple
        """
        raise NotImplementedError()

    def setLimits(self, vmin, vmax):
        """Set this axis limits.

        :param float vmin: minimum axis value
        :param float vmax: maximum axis value
        """
        raise NotImplementedError()

    def _checkLimits(self, vmin, vmax):
        """Makes sure axis range is not empty

        :param float vmin: Min axis value
        :param float vmax: Max axis value
        :return: (min, max) making sure min < max
        :rtype: 2-tuple of float
        """
        if vmax < vmin:
            _logger.debug('%s axis: max < min, inverting limits.', self._defaultLabel)
            vmin, vmax = vmax, vmin
        elif vmax == vmin:
            _logger.debug('%s axis: max == min, expanding limits.', self._defaultLabel)
            if vmin == 0.:
                vmin, vmax = -0.1, 0.1
            elif vmin < 0:
                vmin, vmax = vmin * 1.1, vmin * 0.9
            else:  # xmin > 0
                vmin, vmax = vmin * 0.9, vmin * 1.1

        return vmin, vmax

    def isInverted(self):
        """Return True if the axis is inverted (top to bottom for the y-axis),
        False otherwise."""
        return False

    def setInverted(self, isInverted):
        """Set the axis orientation.

        :param bool flag: True for Y axis going from top to bottom,
                          False for Y axis going from bottom to top
        """
        raise NotImplementedError()

    def getLabel(self):
        """Return the current displayed label of this axis.

        :param str axis: The Y axis for which to get the label (left or right)
        :rtype: str
        """
        return self._currentLabel

    def setLabel(self, label):
        """Set the label displayed on the plot for this axis.

        The provided label can be temporarily replaced by the label of the
        active curve if any.

        :param str label: The axis label
        """
        self._defaultLabel = label
        self._setCurrentLabel(label)
        self._plot._setDirtyPlot()

    def _setCurrentLabel(self, label):
        """Define the label currently displayed.

        If the label is None or empty the default label is used.

        :param str label: Currently displayed label
        :returns: str
        """
        if label is None or label == '':
            label = self._defaultLabel
        if label is None:
            label = ''
        self._currentLabel = label
        return label

    def isLogarithmic(self):
        """Return True if this axis scale is logarithmic, False if linear.

        :rtype: bool
        """
        return self._isLog

    def setLogarithmic(self, flag):
        """Set the scale of this axes (either linear or logarithmic).

        :param bool flag: True to use a logarithmic scale, False for linear.
        """
        if bool(flag) == self._isLog:
            return
        self._isLog = bool(flag)

        self._setLogarithmic(self._isLog)

        # TODO hackish way of forcing update of curves and images
        for item in self._plot._getItems(withhidden=True):
            item._updated()
        self._plot._invalidateDataRange()
        self._plot.resetZoom()

        self.sigLogarithmicChanged.emit(self._isLog)

    def isAutoScale(self):
        """Return True if axis is automatically adjusting its limits.

        :rtype: bool
        """
        return self._isAutoScale

    def setAutoScale(self, flag=True):
        """Set the axis limits adjusting behavior of :meth:`resetZoom`.

        :param bool flag: True to resize limits automatically,
                          False to disable it.
        """
        self._isAutoScale = bool(flag)
        self.sigAutoScaleChanged.emit(self._isAutoScale)


class XAxis(Axis):
    """Axis class defining primitives for the X axis"""

    def _setCurrentLabel(self, label):
        """Define the label currently displayed in the plot for this axis.

        :param str label: Label to display
        """
        label = Axis._setCurrentLabel(self, label)
        self._plot._backend.setGraphXLabel(label)
        return label

    def getLimits(self):
        """Get the graph X (bottom) limits.

        :return: Minimum and maximum values of the X axis
        """
        return self._plot._backend.getGraphXLimits()

    def setLimits(self, xmin, xmax):
        """Set the graph X (bottom) limits.

        :param float xmin: minimum bottom axis value
        :param float xmax: maximum bottom axis value
        """
        xmin, xmax = self._checkLimits(xmin, xmax)

        self._plot._backend.setGraphXLimits(xmin, xmax)
        self._plot._setDirtyPlot()

        self.sigLimitsChanged.emit(xmin, xmax)
        self._plot._notifyLimitsChanged(emitSignal=False)

    def _setLogarithmic(self, flag):
        """Set the bottom X axis scale (either linear or logarithmic).

        :param bool flag: True to use a logarithmic scale, False for linear.
        """
        self._plot._backend.setXAxisLogarithmic(self._isLog)


class YAxis(Axis):
    """Axis class defining primitives for the Y axis"""

    def _setCurrentLabel(self, label):
        """Define the label currently displayed in the plot for this axis.

        :param str label: Label to display
        """
        label = Axis._setCurrentLabel(self, label)
        self._plot._backend.setGraphYLabel(label, axis='left')
        return label

    def getLimits(self):
        """Get the graph Y limits.

        :param str axis: The axis for which to get the limits:
                         Either 'left' or 'right'
        :return: Minimum and maximum values of the X axis
        """
        return self._plot._backend.getGraphYLimits(axis='left')

    def setLimits(self, ymin, ymax):
        """Set the graph Y limits.

        :param float ymin: minimum bottom axis value
        :param float ymax: maximum bottom axis value
        :param str axis: The axis for which to get the limits:
                         Either 'left' or 'right'
        """
        ymin, ymax = self._checkLimits(ymin, ymax)
        self._plot._backend.setGraphYLimits(ymin, ymax, axis='left')
        self._plot._setDirtyPlot()

        self.sigLimitsChanged.emit(ymin, ymax)
        self._plot._notifyLimitsChanged(emitSignal=False)

    def setInverted(self, flag=True):
        """Set the Y axis orientation.

        :param bool flag: True for Y axis going from top to bottom,
                          False for Y axis going from bottom to top
        """
        flag = bool(flag)
        self._plot._backend.setYAxisInverted(flag)
        self._plot._setDirtyPlot()
        self.sigInvertedChanged.emit(flag)

    def isInverted(self):
        """Return True if Y axis goes from top to bottom, False otherwise."""
        return self._plot._backend.isYAxisInverted()

    def _setLogarithmic(self, flag):
        """Set the Y axes scale (either linear or logarithmic).

        :param bool flag: True to use a logarithmic scale, False for linear.
        """
        self._plot._backend.setYAxisLogarithmic(self._isLog)


class YRightAxis(Axis):
    """Proxy axes for the secondary Y axes. It manages it own label and limit
    but share the some state like scale and direction with the main axis."""

    def __init__(self, plot, mainAxis):
        """Constructor

        :param silx.gui.plot.PlotWidget.PlotWidget plot: Parent plot of this
            axis
        :param Axis mainAxis: Axis which sharing state with this axis
        """
        Axis.__init__(self, plot)
        self.__mainAxis = mainAxis

    @property
    def sigInvertedChanged(self):
        """Signal emitted when axis orientation has changed"""
        return self.__mainAxis.sigInvertedChanged

    @property
    def sigLogarithmicChanged(self):
        """Signal emitted when axis scale has changed"""
        return self.__mainAxis.sigLogarithmicChanged

    @property
    def sigAutoScaleChanged(self):
        """Signal emitted when axis autoscale has changed"""
        return self.__mainAxis.sigAutoScaleChanged

    def _setCurrentLabel(self, label):
        """Define the label currently displayed in the plot for this axis.

        :param str label: Label to display
        """
        label = Axis._setCurrentLabel(self, label)
        self._plot._backend.setGraphYLabel(label, axis='right')
        return label

    def getLimits(self):
        """Get the graph Y limits.

        :param str axis: The axis for which to get the limits:
                         Either 'left' or 'right'
        :return: Minimum and maximum values of the X axis
        """
        return self._plot._backend.getGraphYLimits(axis='right')

    def setLimits(self, ymin, ymax):
        """Set the graph Y limits.

        :param float ymin: minimum bottom axis value
        :param float ymax: maximum bottom axis value
        :param str axis: The axis for which to get the limits:
                         Either 'left' or 'right'
        """
        ymin, ymax = self._checkLimits(ymin, ymax)
        self._plot._backend.setGraphYLimits(ymin, ymax, axis='right')
        self._plot._setDirtyPlot()

        self.sigLimitsChanged.emit(ymin, ymax)
        self._plot._notifyLimitsChanged(emitSignal=False)

    def setInverted(self, flag=True):
        """Set the Y axis orientation.

        :param bool flag: True for Y axis going from top to bottom,
                          False for Y axis going from bottom to top
        """
        return self.__mainAxis.setInverted(flag)

    def isInverted(self):
        """Return True if Y axis goes from top to bottom, False otherwise."""
        return self.__mainAxis.isInverted()

    def isLogarithmic(self):
        """Return True if Y axis scale is logarithmic, False if linear."""
        return self.__mainAxis.isLogarithmic()

    def setLogarithmic(self, flag):
        """Set the Y axes scale (either linear or logarithmic).

        :param bool flag: True to use a logarithmic scale, False for linear.
        """
        return self.__mainAxis.setLogarithmic(flag)

    def isAutoScale(self):
        """Return True if Y axes are automatically adjusting its limits."""
        return self.__mainAxis.isAutoScale()

    def setAutoScale(self, flag=True):
        """Set the Y axis limits adjusting behavior of :meth:`resetZoom`.

        :param bool flag: True to resize limits automatically,
                          False to disable it.
        """
        return self.__mainAxis.setAutoScale(flag)
