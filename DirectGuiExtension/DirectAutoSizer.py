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
        self.skipInitRefresh = True
        optiondefs = (
            ('extendHorizontal', True,      None),
            ('extendVertical',   True,      None),
            ('minSize',          (0, 0, 0, 0), self.refresh),
            ('maxSize',          (0, 0, 0, 0), self.refresh),
            ('updateOnWindowResize', True,  self.setUpdateOnWindowResize),
            ('childUpdateSizeFunc', None,   None),
            ('parentGetSizeFunction', None, None),
            ('parentGetSizeExtraArgs', [], None),

            ('suppressMouse',  0,           None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        self.parentObject = parent
        self.child = child
        if child is not None:
            child.reparentTo(self)

        # Call option initialization functions
        self.initialiseoptions(DirectAutoSizer)

        self.skipInitRefresh = False
        # initialize once at the end
        self.refresh()

    def setChild(self, child):
        if self.child is not None:
            self.child.detachNode()
        self.child = child
        self.child.reparentTo(self)
        self.refresh()

    def removeChild(self):
        if self.child is not None:
            self.child.detachNode()
        self.child = None

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

        if self.screenSize == base.getSize():
            return
        self.screenSize = base.getSize()
        self.refresh()

        #TODO: for some reason, the first refresh doesn't always refresh everything correct, so we do it twice here
        self.refresh()

    def refresh(self):
        """Resize the sizer and its child element"""
        if self.skipInitRefresh: return
        if self.child is None:
            return

        # store left/right/bottom/top
        l=r=b=t=0

        # dependent on our parent, make sure the size values are set correct
        if self["parentGetSizeFunction"] is not None:
            # we have a user defined way to get the size, this should be treated
            # most important
            size = self["parentGetSizeFunction"](*self["parentGetSizeExtraArgs"])

            l=size[0]
            r=size[1]
            b=size[2]
            t=size[3]
        elif self.parentObject is None or self.parentObject == ShowBaseGlobal.aspect2d:
            # the default parent of directGui widgets
            l = base.a2dLeft
            r = base.a2dRight
            b = base.a2dBottom
            t = base.a2dTop
        elif self.parentObject == base.pixel2d:
            # we are parented to pixel2d
            xsize, ysize = base.getSize()
            l = 0
            r = xsize
            b = -ysize
            t = 0
        elif DirectGuiWidget in inspect.getmro(type(self.parentObject)):
            # We have a "normal" DirectGui widget here
            bounds = self.parentObject.bounds
            l, r, b, t = bounds
        else:
            # We are parented to something else, probably a nodepath
            self.parentObject.node().setBoundsType(BoundingVolume.BT_box)

            ll = LPoint3()
            ur = LPoint3()

            self.parentObject.calcTightBounds(ll, ur, render)

            l=ll.getX()
            r=ur.getX()
            b=ll.getZ()
            t=ur.getZ()

        childSize = self.child['frameSize']
        if childSize is None:
            childSize = self.child.getBounds()

        if type(self.child["scale"]) == LVecBase3f:
            childScale = self.child["scale"]
        elif self.child["scale"] is not None:
            try:
                childScale = LVecBase3f(self.child["scale"])
            except:
                childScale = self.child["scale"]
        else:
            childScale = LVecBase3f(1.0)

        if not self['extendHorizontal']:
            l = childSize[0] * childScale.getX()
            r = childSize[1] * childScale.getX()

        if not self['extendVertical']:
            b = childSize[2] * childScale.getZ()
            t = childSize[3] * childScale.getZ()

        #TODO: Better check for positive/negative numbers
        if l > self['minSize'][0]: l = self['minSize'][0]
        if r < self['minSize'][1]: r = self['minSize'][1]
        if b > self['minSize'][2]: b = self['minSize'][2]
        if t < self['minSize'][3]: t = self['minSize'][3]

        if self['maxSize'] is not None and self['maxSize'] != (0, 0, 0, 0):
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
        self.child["frameSize"] = [l/childScale.getX(),r/childScale.getX(),b/childScale.getZ(),t/childScale.getZ()]
        self["frameSize"] = self.child["frameSize"]

        base.messenger.send(self.getUpdateSizeEvent())
        if self['childUpdateSizeFunc'] is not None:
            self['childUpdateSizeFunc']()

    def getUpdateSizeEvent(self):
        return self.uniqueName("update-size")
