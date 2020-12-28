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
            ('dragAreaHeight',              0.1, None),
            ('resortOnDrag',               True, None),
            ('showClose',                  True, None),
            ('closeButtonPosition',     'Right', None),
            ('closeButtonScale',           0.05, None)
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectScrolledFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectScrolledWindowFrame)

        self.dragDropTask = None

        b = self.bounds
        c = self.createcomponent(
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

        c.bind(DGG.B1PRESS, self.dragStart)
        c.bind(DGG.B1RELEASE, self.dragStop)

        scale = self['closeButtonScale']
        pos = (0,0,self['dragAreaHeight']*0.5)
        if self['closeButtonPosition'] == 'Right':
            pos = (b[1]-scale*0.5,0,self['dragAreaHeight']*0.5)
        elif self['closeButtonPosition'] == 'Left':
            pos = (b[0]+scale*0.5,0,self['dragAreaHeight']*0.5)
        closeBtn = self.createcomponent(
            'closeButton', (), 'closeButton',
            DirectButton,
            (c,),
            text='x',
            scale=scale,
            pos=pos,
            command=self.destroy)

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
