"""This module contains the DirectCollapsibleFrame class."""

__all__ = ['DirectCollapsibleFrame']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from . import DirectGuiHelper as DGH


class DirectCollapsibleFrame(DirectFrame):
    """
    A frame containing a clickable header to show and hide its content frame
    """

    def __init__(self, parent = None, **kw):
        self.skipInitRefresh = True
        optiondefs = (
            ('headerheight',           0.1, None),
            ('collapsed',           False, self.setCollapsed),

            ('collapseText',   'collapse >>', None),
            ('extendText',     'extend <<', None),
            ('frameSize',      (-0.5, 0.5, -0.5, 0.5), self.setFrameSize)
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        frameSize = self['frameSize']

        # set up the header button to collapse/extend
        self.toggleCollapseButton = self.createcomponent(
            'toggleCollapseButton', (), None,
            DirectButton, (self,),
            text=self['extendText'] if self['collapsed'] else self['collapseText'],
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_pos=(frameSize[0]+0.02, frameSize[3]-self['headerheight']/2.0),
            borderWidth=(0.02, 0.02),
            relief=DGG.FLAT,
            pressEffect=False,
            frameSize = (
                frameSize[0], frameSize[1],
                frameSize[3]-self['headerheight'], frameSize[3]),
            command=self.toggleCollapsed)

        # Call option initialization functions
        self.initialiseoptions(DirectCollapsibleFrame)

        self.resetFrameSize()
        self.updateFrameSize()

        self.originalFrameSize = self['frameSize']

    def addItem(self, element, *args):
        print(element)
        for arg in args:
            print(type(arg), arg)

    def updateFrameSize(self):
        self.toggleCollapseButton['frameSize'] = (
            DGH.getRealLeft(self), DGH.getRealRight(self),
            DGH.getRealTop(self)-self['headerheight'], DGH.getRealTop(self))
        self.originalFrameSize = self['frameSize']
        self.toggleCollapseButton["text_pos"] = (DGH.getRealLeft(self)+0.02, DGH.getRealTop(self)-self['headerheight']/2.0)

    def toggleCollapsed(self):
        self['collapsed'] = not self['collapsed']

    def setCollapsedTo(self, collapsed):
        self['collapsed'] = collapsed
        self.setCollapsed()

    def setCollapsed(self):
        # we're probably to early here
        if not hasattr(self, 'originalFrameSize'): return

        fs = self['frameSize']

        if self['collapsed']:
            # collapse
            self['frameSize'] = (fs[0],fs[1],fs[3]-self['headerheight'],fs[3])

            # hide all children
            for child in self.getChildren():
                # skip our toggle collapse button
                if child == self.toggleCollapseButton: continue
                # hide the child
                child.hide()

            # change the toggle button text
            self.toggleCollapseButton['text'] = self['extendText']

            # send notice about us being collapsed
            base.messenger.send(self.getCollapsedEvent())

        else:
            # extend
            self['frameSize'] = self.originalFrameSize
            for child in self.getChildren():
                # skip our toggle collapse button
                if child == self.toggleCollapseButton: continue
                # show the child
                child.show()

            # change the toggle button text
            self.toggleCollapseButton['text'] = self['collapseText']

            # send notice about us being extended
            base.messenger.send(self.getExtendedEvent())

    def getCollapsedEvent(self):
        return self.uniqueName("collapsed")

    def getExtendedEvent(self):
        return self.uniqueName("extended")
