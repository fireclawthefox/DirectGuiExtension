#Requires:
#    Can we get conjunction between two sizer to work to simultaneously size two splitframes at once?
#    Collapse function?





"""This module contains the DirectSplitFrame class."""

__all__ = ['DirectSplitFrame']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from . import DirectGuiHelper as DGH


DGG.HORIZONTAL_INVERTED = 'horizontal_inverted'


class DirectItemContainer():
    def __init__(self, element, **kw):
        self.element = element
        #if "stretch" in kw:
        #    if kw.get("stretch"):
        #        pass
        #    del kw["stretch"]
        #self.margin = VBase4(0,0,0,0)
        #if "margin" in kw:
        #    self.margin = kw.get("margin")

class DirectSplitFrame(DirectFrame):
    """
    Two frames that can be resized with a small line between them
    """

    def __init__(self, parent = None, **kw):
        self.skipInitRefresh = True
        optiondefs = (
            # Define type of DirectGuiWidget
            ('pgFunc',         PGItem,      None),
            ('numStates',      1,           None),
            ('state',          DGG.NORMAL,  None),
            ('borderWidth',    (0, 0),      self.setBorderWidth),
            ('orientation', DGG.HORIZONTAL, self.refresh),
            ('framesize',      (-1,1,-1,1), None),

            # TODO: Change this. This only works for certain circumstances
            ('pixel2d',        False,       self.refresh),

            ('showSplitter',   True,        self.setSplitter),
            ('splitterPos',    0,           self.refresh),
            ('splitterWidth',  0.02,        self.refresh),
            ('splitterColor', (.7, .7, .7, 1), None),
            ('splitterHighlightColor', (.9, .9, .9, 1), None),

            ('firstFrameUpdateSizeFunc', None,  None),
            ('secondFrameUpdateSizeFunc', None, None),
            ('firstFrameMinSize', None,     None),
            ('secondFrameMinSize', None,    None),

            ('suppressMouse',  0,           None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectSplitFrame)

        self.resetFrameSize()

        self.dragDropTask = None
        self.ignoreMinSizeCheck = False

        self.firstFrame = self.createcomponent(
            'firstFrame', (), None,
            DirectFrame, (self,),
            frameSize = (-0.45, 0.45, -1, 1),
            pos = (-0.55, 0, 0),)

        self.secondFrame = self.createcomponent(
            'secondFrame', (), None,
            DirectFrame, (self,),
            frameSize = (-0.45, 0.45, -1, 1),
            pos = (0.55, 0, 0),)

        self.splitter = self.createcomponent(
            'splitter', (), None,
            DirectFrame, (self,),
            numStates = 2,
            frameSize = (-0.01, 0.01, -1, 1),
            frameColor = self['splitterColor'],
            text = "<\n>",
            text_scale = 0.05,
            text_align = TextNode.ACenter,
            state = 'normal')
        self.splitter.bind(DGG.ENTER, self.enter)
        self.splitter.bind(DGG.EXIT, self.exit)
        self.splitter.bind(DGG.B1PRESS, self.dragStart)
        self.splitter.bind(DGG.B1RELEASE, self.dragStop)

        self.setSplitter(self['splitterWidth'])

        self.skipInitRefresh = False
        # initialize once at the end
        self.refresh()

    def setSplitter(self, width=0.02):
        if not hasattr(self, "splitter"): return
        if self['showSplitter'] == False:
            self.splitter.hide()
            self['splitterWidth'] = 0
        else:
            self.splitter.show()
            self['splitterWidth'] = width


    def refresh(self):
        """
        Recalculate the position of every item in this panel and set the frame-
        size of the panel accordingly if auto update is enabled.
        """
        # sanity checks so we don't get here to early
        if self.skipInitRefresh: return
        if not hasattr(self, "bounds"): return

        width = DGH.getRealWidth(self)
        height = DGH.getRealHeight(self)

        if self["orientation"] == DGG.HORIZONTAL:
            self.splitter.setX(self["splitterPos"])
            self.checkMinSIze()

            if self["pixel2d"]:
                splitterPosInPercent = 1 - self["splitterPos"]/width
                leftWidth = width * (1-splitterPosInPercent) - (self["splitterWidth"] / 2)
                rightWidth = width * splitterPosInPercent - (self["splitterWidth"] / 2)
            else:
                leftWidth = (width / 2) + self["splitterPos"] - (self["splitterWidth"] / 2)
                rightWidth = (width / 2) - self["splitterPos"] - (self["splitterWidth"] / 2)

            self.firstFrame["frameSize"] = (-leftWidth/2, leftWidth/2, self["frameSize"][2], self["frameSize"][3])
            self.firstFrame.setX((-leftWidth / 2) - (self["splitterWidth"] / 2) + self["splitterPos"])
            self.firstFrame.setZ(0)
            self.secondFrame["frameSize"] = (-rightWidth/2, rightWidth/2, self["frameSize"][2], self["frameSize"][3])
            self.secondFrame.setX((rightWidth / 2) + (self["splitterWidth"] / 2) + self["splitterPos"])
            self.secondFrame.setZ(0)

            self.splitter["frameSize"] = (-self["splitterWidth"]/2, self["splitterWidth"]/2, self["frameSize"][2], self["frameSize"][3])
            self.splitter["text_roll"] = 0

        elif self["orientation"] == DGG.VERTICAL:
            self.splitter.setZ(self["splitterPos"])
            self.checkMinSIze()

            if self["pixel2d"]:
                splitterPosInPercent = 1 - self["splitterPos"]/height
                topHeight = height * splitterPosInPercent - (self["splitterWidth"] / 2)
                bottomHeight = height * (1-splitterPosInPercent) - (self["splitterWidth"] / 2)
            else:
                topHeight = (height / 2) - self["splitterPos"] - (self["splitterWidth"] / 2)
                bottomHeight = (height / 2) + self["splitterPos"] - (self["splitterWidth"] / 2)

            self.firstFrame["frameSize"] = (self["frameSize"][0], self["frameSize"][1], -topHeight/2, topHeight/2)
            self.firstFrame.setX(0)
            self.firstFrame.setZ((topHeight / 2) + (self["splitterWidth"] / 2) + self["splitterPos"])
            self.secondFrame["frameSize"] = (self["frameSize"][0], self["frameSize"][1], -bottomHeight/2, bottomHeight/2)
            self.secondFrame.setX(0)
            self.secondFrame.setZ((-bottomHeight / 2) - (self["splitterWidth"] / 2) + self["splitterPos"])

            self.splitter["frameSize"] = (self["frameSize"][0], self["frameSize"][1], -self["splitterWidth"]/2, self["splitterWidth"]/2)
            self.splitter["text_roll"] = 90


        base.messenger.send(self.uniqueName("update-size"))
        if self['firstFrameUpdateSizeFunc'] is not None:
            self['firstFrameUpdateSizeFunc']()
        if self['secondFrameUpdateSizeFunc'] is not None:
            self['secondFrameUpdateSizeFunc']()

    def checkMinSIze(self):
        if self.ignoreMinSizeCheck: return
        # ignore further minimum size checks until we are done
        self.ignoreMinSizeCheck = True

        if self["orientation"] == DGG.HORIZONTAL:
            minLeft = self['firstFrameMinSize'] if self['firstFrameMinSize'] is not None else 0
            minRight = self['secondFrameMinSize'] if self['secondFrameMinSize'] is not None else 0
            if self.splitter.getX() - self["splitterWidth"] / 2 < self["frameSize"][0] + minLeft:
                self.splitter.setX(self["frameSize"][0] + self["splitterWidth"] / 2 + minLeft)
            elif self.splitter.getX() + self["splitterWidth"] / 2 > self["frameSize"][1] - minRight:
                self.splitter.setX(self["frameSize"][1] - self["splitterWidth"] / 2 - minRight)
            self["splitterPos"] = self.splitter.getX()

        elif self["orientation"] == DGG.VERTICAL:
            minTop = self['firstFrameMinSize'] if self['firstFrameMinSize'] is not None else 0
            minBottom = self['secondFrameMinSize'] if self['secondFrameMinSize'] is not None else 0
            if self.splitter.getZ() - self["splitterWidth"] / 2 < self["frameSize"][2] + minTop:
                self.splitter.setZ(self["frameSize"][2] + self["splitterWidth"] / 2 + minTop)
            elif self.splitter.getZ() + self["splitterWidth"] / 2 > self["frameSize"][3] - minBottom:
                self.splitter.setZ(self["frameSize"][3] - self["splitterWidth"] / 2 - minBottom)
            self["splitterPos"] = self.splitter.getZ()

        self.ignoreMinSizeCheck = False

    def enter(self, event):
        self.splitter["frameColor"] = self['splitterHighlightColor']

    def exit(self, event):
        self.splitter["frameColor"] = self['splitterColor']

    def dragStart(self, event):
        """
        Start dragging the window around
        """
        if self.dragDropTask is not None:
            # remove any existing tasks
            taskMgr.remove(self.dragDropTask)

        self.splitter["frameColor"] = self['splitterHighlightColor']

        # get the windows position as seen from render2d
        vWidget2render2d = self.splitter.getPos(render2d)
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
            if self["orientation"] == DGG.HORIZONTAL:
                newPos.setY(0)
                newPos.setZ(self.splitter.getZ(render2d))
                self.splitter.setPos(render2d, newPos)
                self.checkMinSIze()

            elif self["orientation"] == DGG.VERTICAL:
                newPos.setX(self.splitter.getX(render2d))
                newPos.setY(0)
                self.splitter.setPos(render2d, newPos)
                self.checkMinSIze()
            self.refresh()
            self.splitter["frameColor"] = self['splitterHighlightColor']
        return t.cont

    def dragStop(self, event):
        """
        Stop dragging the splitter around
        """
        # kill the drag and drop task
        taskMgr.remove(self.dragDropTask)
        self.splitter["frameColor"] = self['splitterColor']
        self.refresh()
