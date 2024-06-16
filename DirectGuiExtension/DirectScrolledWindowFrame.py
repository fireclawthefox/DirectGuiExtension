"""This module contains the DirectScrolledWindowFrame class.

It will create a scrolled frame with an extra frame on top of it
"""

__all__ = ['DirectScrolledWindowFrame']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledFrame import DirectScrolledFrame

class DirectScrolledWindowFrame(DirectScrolledFrame):
    """
    A moveable window with a scrolled content frame
    """
    def __init__(self, parent = None, **kw):
        optiondefs = (
            # Define type of DirectGuiWidget
            # The height of the area to drag the widget around
            ('dragAreaHeight',              0.1, self.__updateDragAreaHeight),
            ('resortOnDrag',               True, None),
            ('showClose',                  True, self.__showClose),
            ('closeButtonPosition',     'Right', self.__updateCloseButton),
            ('closeButtonScale',           0.05, self.__updateCloseButton)
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectScrolledFrame.__init__(self, parent)

        self.dragDropTask = None

        b = self["frameSize"]
        self.dragFrame = self.createcomponent(
            'dragFrame', (), 'dragFrame',
            DirectFrame,
            # set the parent of the frame to this class
            (self,),
            state=DGG.NORMAL,
            suppressMouse=True,
            frameColor=(0.5,0.5,0.5,1),
            relief=1,
            pos=(0,0,b[3]),
            # set the size
            frameSize=(b[0],b[1],0, self['dragAreaHeight']))

        self.dragFrame.bind(DGG.B1PRESS, self.dragStart)
        self.dragFrame.bind(DGG.B1RELEASE, self.dragStop)

        scale = self['closeButtonScale']
        pos = (0,0,self['dragAreaHeight']*0.5)
        if self['closeButtonPosition'] == 'Right':
            pos = (b[1]-scale*0.5,0,self['dragAreaHeight']*0.5)
        elif self['closeButtonPosition'] == 'Left':
            pos = (b[0]+scale*0.5,0,self['dragAreaHeight']*0.5)
        self.closeButton = self.createcomponent(
            'closeButton', (), 'closeButton',
            DirectButton,
            (self.dragFrame,),
            text='x',
            scale=scale,
            pos=pos,
            command=self.destroy)

        # Call option initialization functions
        self.initialiseoptions(DirectScrolledWindowFrame)

        self.dragFrame.setPos(0, 0, self.bounds[3])
        self.dragFrame["frameSize"] = (self.bounds[0], self.bounds[1], 0, self['dragAreaHeight'])

    def dragStart(self, event):
        """
        Start dragging the window around
        """
        if self.dragDropTask is not None:
            # remove any existing tasks
            taskMgr.remove(self.dragDropTask)

        if self['resortOnDrag']:
            self.reparentTo(self.parent, 0)

        # get the windows position as seen from render2d
        vWidget2render2d = self.getPos(render2d)
        # get the mouse position as seen from render2d
        vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        # calculate the vector between the mosue and the window
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        # create the task and store the values in it, so we can use it in there
        self.dragDropTask = taskMgr.add(self.dragTask, self.taskName("dragDropTask"))
        self.dragDropTask.editVec = editVec
        self.dragDropTask.mouseVec = vMouse2render2d

    def dragTask(self, t):
        """
        Calculate the new window position ever frame
        """
        # chec if we have the mouse
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            # get the mouse position
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            # calculate the new position using the mouse position and the start
            # vector of the window
            newPos = vMouse2render2d + t.editVec
            # Now set the new windows new position
            self.setPos(render2d, newPos)
        return t.cont

    def dragStop(self, event):
        """
        Stop dragging the window around
        """
        # kill the drag and drop task
        taskMgr.remove(self.dragDropTask)

    def __showClose(self):
        if self["showClose"]:
            self.closeButton.show()
        else:
            self.closeButton.hide()

    def __updateCloseButton(self):
        b = self["frameSize"]
        scale = self['closeButtonScale']
        pos = (0, 0, self['dragAreaHeight'] * 0.5)
        if self['closeButtonPosition'] == 'Right':
            pos = (b[1] - scale * 0.5, 0, self['dragAreaHeight'] * 0.5)
        elif self['closeButtonPosition'] == 'Left':
            pos = (b[0] + scale * 0.5, 0, self['dragAreaHeight'] * 0.5)

        self.closeButton.setPos(pos)
        self.closeButton.setScale(scale)

    def __updateDragAreaHeight(self):
        if not hasattr(self, "bounds"):  # We are here too early
            return

        self.dragFrame.setPos(0, 0, self.bounds[3])
        self.dragFrame["frameSize"] = (self.bounds[0], self.bounds[1], 0, self['dragAreaHeight'])
        self.__updateCloseButton()
