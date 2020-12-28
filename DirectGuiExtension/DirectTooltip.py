"""This snippet shows how to create a tooltip text that will be attached
to the cursor and check it's position to not move out of the screen."""

__all__ = ['DirectTooltip']

import sys

from panda3d.core import TextNode
from direct.gui.DirectGui import DirectLabel

class DirectTooltip(DirectLabel):
    def __init__(self, parent = None, **kw):
        optiondefs = (
            ('text',        'Tooltip',      None),
            ('text_align',  TextNode.ALeft, None),
            #('text_fg',    (1, 1, 1, 1),    None),
            #('text_bg',    (0, 0, 0, 0.75), None),
            #('text_frame', (0, 0, 0, 0.75), None),
            ('borderWidth', (0.05, 0.05),   None),
            #('parent',      base.pixel2d,   None),
            #('sortOrder',   1000,           None),
           )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)
        # Initialize superclasses
        DirectLabel.__init__(self, parent)

        # make sure the text apears slightly right below the cursor
        if parent is base.pixel2d:
            self.textXShift = 10
            self.textYShift = -32
        else:
            self.textXShift = 0.05
            self.textYShift = -0.08

        self.mousePos = None

        # this will determine when the tooltip should be moved in the
        # respective direction, whereby
        # 1  : display edge
        # <1 : margin inside the window
        # >1 : margin outside the window
        self.xEdgeStartShift = 0.99
        self.yEdgeStartShift = 0.99

        # make sure the tooltip is shown on top
        self.setBin('gui-popup', 0)

        # Call option initialization functions
        self.initialiseoptions(DirectTooltip)

        self.hide()

    def show(self, text=None, args=None):
        if text is not None:
            self.setText(text)
            self.resetFrameSize()#setFrameSize(True)
        DirectLabel.show(self)

        # add the tooltips update task so it will be updated every frame
        base.taskMgr.add(self.updateTooltipPos, self.taskName("task_updateTooltipPos"))

    def hide(self, args=None):
        DirectLabel.hide(self)

        # remove the tooltips update task
        base.taskMgr.remove(self.taskName("task_updateTooltipPos"))

    def updateTooltipPos(self, task):
        # calculate new aspec tratio
        wp = base.win.getProperties()
        aspX = 1.0
        aspY = 1.0
        wpXSize = wp.getXSize()
        wpYSize = wp.getYSize()
        if self.getParent() != base.pixel2d:
            # calculate the aspect ratio of the window if we're not reparented
            # to the pixel2d nodepath
            if wpXSize > wpYSize:
                aspX = wpXSize / float(wpYSize)
            else:
                aspY = wpYSize / float(wpXSize)

        # variables to store the mouses current x and y position
        x = 0.0
        y = 0.0
        if base.mouseWatcherNode.hasMouse():
            DirectLabel.show(self)

            # Move the tooltip to the mouse

            # get the mouse position
            if self.getParent() == base.pixel2d:
                x = base.win.getPointer(0).getX()
                y = -base.win.getPointer(0).getY()
            else:
                x = (base.mouseWatcherNode.getMouseX()*aspX)
                y = (base.mouseWatcherNode.getMouseY()*aspY)

            # set the text to the current mouse position
            self.setPos(
                x + self.textXShift,
                0,
                y + self.textYShift)

            bounds = self.getBounds()
            # bounds = left, right, bottom, top

            # calculate the texts bounds respecting its current position
            xLeft = self.getX() + bounds[0]*self.getScale()[0]
            xRight = self.getX() + bounds[1]*self.getScale()[0]
            yUp = self.getZ() + bounds[3]*self.getScale()[1]
            yDown = self.getZ() + bounds[2]*self.getScale()[1]

            # these will be used to shift the text in the desired direction
            xShift = 0.0
            yShift = 0.0

            if self.getParent() == base.pixel2d:
                # make sure to have the correct edges in a pixel2d environment
                # even if the window has been resized
                self.xEdgeStartShift = wpXSize * 0.99
                self.yEdgeStartShift = wpYSize * 0.99

            if xRight/aspX > self.xEdgeStartShift:
                # shift to the left
                xShift = self.xEdgeStartShift - xRight/aspX
            elif xLeft/aspX < -self.xEdgeStartShift:
                # shift to the right
                xShift = -(self.xEdgeStartShift + xLeft/aspX)
            if yUp/aspY > self.yEdgeStartShift:
                # shift down
                yShift = self.yEdgeStartShift - yUp/aspY
            elif yDown/aspY < -self.yEdgeStartShift:
                # shift up
                yShift = -(self.yEdgeStartShift + yDown/aspY)

            # some aspect ratio calculation
            xShift *= aspX
            yShift *= aspY

            # move the tooltip to the new position
            self.setX(self.getX() + xShift)
            self.setZ(self.getZ() + yShift)

        else:
            DirectLabel.hide(self)


        # continue the task until it got manually stopped
        return task.cont

