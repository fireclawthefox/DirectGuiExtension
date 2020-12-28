"""This module contains the DirectAutoSizer class."""

__all__ = ['DirectAutoSizer']

import inspect
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiBase import DirectGuiWidget
from . import DirectGuiHelper as DGH
from direct.showbase import ShowBaseGlobal

class DirectAutoSizer(DirectFrame):
    """
    A frame to Automatically resize the given other DirectGui element
    """
    def __init__(self, parent = None, child = None, **kw):
        optiondefs = (
            ('extendHorizontal', True,      None),
            ('extendVertical',   True,      None),
            ('minSize',          (0, 0, 0, 0), self.refresh),
            ('maxSize',          None,      self.refresh),
            ('updateOnWindowResize', True,  self.setUpdateOnWindowResize),
            ('childUpdateSizeFunc', None,   None)
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        self.parentObject = parent
        self.child = child
        child.reparentTo(self)

        # Call option initialization functions
        self.initialiseoptions(DirectAutoSizer)

    def setUpdateOnWindowResize(self):
        if self['updateOnWindowResize']:
            # Make sure the sizer scales with window size changes
            self.screenSize = base.getSize()
            self.accept('window-event', self.windowEventHandler)
        else:
            # stop updating on window resize events
            self.ignore('window-event')
            self.screenSize = None

    def windowEventHandler(self, window=None):
        if window != base.win:
            # This event isn't about our window.
            return

        #if window is not None: # window is none if panda3d is not started
        #    if self.screenSize == base.getSize():
        #        return
        #self.screenSize = base.getSize()
        self.refresh()

    def refresh(self):
        """Resize the sizer and its child element"""
        # store left/right/bottom/top
        l=r=b=t=0

        # dependent on our parent, make sure the size values are set correct
        if self.parentObject is None or self.parentObject == ShowBaseGlobal.aspect2d:
            # the default parent of directGui widgets
            l = base.a2dLeft
            r = base.a2dRight
            b = base.a2dBottom
            t = base.a2dTop
        elif DirectGuiWidget in inspect.getmro(type(self.parentObject)):
            # We have a "normal" DirectGui widget here
            bounds = self.parentObject.bounds
            l, r, b, t = bounds
        else:
            #TODO: Check which type of object we got here. Maybe add some more
            #      checks for NodePaths
            l=b=-1
            r=t=1

        childSize = self.child['frameSize']
        if childSize is None:
            childSize = self.child.getBounds()

        childScale = self.child["scale"]
        if childScale is None:
            childScale = 1.0

        if not self['extendHorizontal']:
            l = childSize[0] * childScale
            r = childSize[1] * childScale


        if not self['extendVertical']:
            b = childSize[2] * childScale
            t = childSize[3] * childScale

        #TODO: Better check for positive/negative numbers
        if l > self['minSize'][0]: l = self['minSize'][0]
        if r < self['minSize'][1]: r = self['minSize'][1]
        if b > self['minSize'][2]: b = self['minSize'][2]
        if t < self['minSize'][3]: t = self['minSize'][3]

        if self['maxSize'] is not None:
            if l < self['maxSize'][0]: l = self['maxSize'][0]
            if r > self['maxSize'][1]: r = self['maxSize'][1]
            if b < self['maxSize'][2]: b = self['maxSize'][2]
            if t > self['maxSize'][3]: t = self['maxSize'][3]

        # recalculate size according to position
        l -= self.child.getX()
        r += self.child.getX()
        b -= self.child.getZ()
        t += self.child.getZ()

        # actual resizing of our child element
        self.child["frameSize"] = [l/childScale,r/childScale,b/childScale,t/childScale]
        self["frameSize"] = self.child["frameSize"]

        base.messenger.send(self.uniqueName("update-size"))
        if self['childUpdateSizeFunc'] is not None:
            self['childUpdateSizeFunc']()
