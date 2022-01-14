"""This module contains the DirectBoxSizer class."""

__all__ = ['DirectBoxSizer']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from . import DirectGuiHelper as DGH


DGG.HORIZONTAL_INVERTED = 'horizontal_inverted'


class DirectItemContainer():
    def __init__(self, element, **kw):
        self.element = element
        self.updateFunc = None
        if "updateFunc" in kw:
            self.updateFunc = kw.get("updateFunc")

class DirectBoxSizer(DirectFrame):
    """
    A frame to add multiple other directGui elements to that will then be
    automatically be placed stacked next to each other.
    """

    # Horizontal
    A_Center = 0b1
    A_Left = 0b10
    A_Right = 0b100

    # Vertical
    A_Middle = 0b1000
    A_Top = 0b10000
    A_Bottom = 0b100000

    def __init__(self, parent = None, **kw):
        self.skipInitRefresh = True
        optiondefs = (
            # Define type of DirectGuiWidget
            ('items',          [],          self.refresh),
            ('pgFunc',         PGItem,      None),
            ('numStates',      1,           None),
            ('state',          DGG.NORMAL,  None),
            ('borderWidth',    (0, 0),      self.setBorderWidth),

            ('orientation', DGG.HORIZONTAL, self.refresh),
            ('itemMargin',     (0,0,0,0),   self.refresh),
            ('itemAlign',  self.A_Left|self.A_Top, self.refresh),
            ('autoUpdateFrameSize', True,   None),

            ('suppressMouse',  0,           None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectBoxSizer)

        self.itemsLeft = 0
        self.itemsRight = 0
        self.itemsBottom = 0
        self.itemsTop = 0

        self.skipInitRefresh = False
        # initialize once at the end
        self.refresh()

    def addItem(self, element, **kw):
        """
        Adds the given item to this panel stack
        """
        element.reparentTo(self)
        container = DirectItemContainer(element, **kw)
        self["items"].append(container)
        if "skipRefresh" in kw:
            return
        self.refresh()

    def removeItem(self, element):
        """
        Remove this item from the panel
        """
        for item in self["items"]:
            if element == item.element:
                self["items"].remove(item)
                self.refresh()
                return 1
        return 0

    def refresh(self):
        """
        Recalculate the position of every item in this panel and set the frame-
        size of the panel accordingly if auto update is enabled.
        """
        if self.skipInitRefresh: return
        # sanity check so we don't get here to early
        if not hasattr(self, "bounds"): return
        if len(self["items"]) == 0: return

        for item in self["items"]:
            item.element.frameInitialiseFunc()

        nextX = 0
        nextY = 0

        sizer_pad = self["pad"]

        b_top = 0
        b_bottom = 0
        b_left = 0
        b_right = 0

        margin_left = self["itemMargin"][0]
        margin_right = self["itemMargin"][1]
        margin_bottom = self["itemMargin"][2]
        margin_top = self["itemMargin"][3]

        if self["autoUpdateFrameSize"]:
            # set the frame size to 0, we'll calculate the new size at the end
            self["frameSize"] = (0, 0, 0, 0)

        itemsWidth = 0
        itemsHeight = 0
        if self['orientation'] == DGG.HORIZONTAL:
            # Horizontal - Left to Right placement
            if not self["autoUpdateFrameSize"]:
                # get the left side of the box sizer frame
                if self["frameSize"] != None:
                    nextX = self["frameSize"][0]

            # go through all items in the box and place them
            for item in self["items"]:
                curElem = item.element
                y = -DGH.getRealBottom(curElem)

                # Vertical Alingment
                if self["itemAlign"] & self.A_Middle:
                    # Items are alligned by their center
                    y -= DGH.getRealHeight(curElem) / 2 - sizer_pad[1]

                    # get the new top and bottom if we should resize the box
                    b_bottom = min(b_bottom, -DGH.getRealHeight(curElem) / 2)
                    b_top = max(b_top, DGH.getRealHeight(curElem) / 2)
                elif self["itemAlign"] & self.A_Top:
                    # Items are alligned by their upper edge
                    y -= DGH.getRealHeight(curElem)
                    # Vertical adjustment to the box' size
                    y += self["frameSize"][3]

                    # get the new top and bottom if we should resize the box
                    b_bottom = min(b_bottom, -DGH.getRealHeight(curElem))
                    b_top = 0
                else:
                    # Items are alligned by their lower edge
                    b_top = max(b_top, DGH.getRealHeight(curElem))
                    # Vertical adjustment to the box' size
                    y += self["frameSize"][2]

                # place the element and calculate the next x position
                curElem.setPos(nextX - DGH.getRealLeft(curElem), 0, y)
                itemWidth = (DGH.getRealWidth(curElem) + margin_left + margin_right)
                nextX += itemWidth
                b_right = nextX
                itemsWidth += itemWidth

        elif self['orientation'] == DGG.HORIZONTAL_INVERTED:
            # Horizontal - Right to Left
            if not self["autoUpdateFrameSize"]:
                if self["frameSize"] != None:
                    nextX = self["frameSize"][1]
            for item in self["items"]:
                curElem = item.element
                y = -DGH.getRealBottom(curElem)

                # Vertical Alingment
                if self["itemAlign"] & self.A_Middle:
                    # Items are alligned by their center
                    y -= DGH.getRealHeight(curElem) / 2 + sizer_pad[1]

                    # get the new top and bottom if we should resize the box
                    b_bottom = min(b_bottom, -DGH.getRealHeight(curElem) / 2)
                    b_top = max(b_top, DGH.getRealHeight(curElem) / 2)
                elif self["itemAlign"] & self.A_Top:
                    # Items are alligned by their upper edge
                    y -= DGH.getRealHeight(curElem)
                    # Vertical adjustment to the box' size
                    y += self["frameSize"][3]

                    # get the new top and bottom if we should resize the box
                    b_bottom = min(b_bottom, -DGH.getRealHeight(curElem))
                    b_top = 0
                else:
                    # Items are alligned by their lower edge
                    b_top = max(b_top, DGH.getRealHeight(curElem))
                    # Vertical adjustment to the box' size
                    y += self["frameSize"][2]

                # place the element and calculate the next x position
                curElem.setPos(nextX + DGH.getRealRight(curElem), 0, y)
                itemWidth = (DGH.getRealWidth(curElem) + margin_left + margin_right)
                nextX -= itemWidth
                b_left = nextX
                itemsWidth += itemWidth

        elif self['orientation'] == DGG.VERTICAL:
            # Vertical - Top to Bottom
            if not self["autoUpdateFrameSize"]:
                if self["frameSize"] != None:
                    nextY = self["frameSize"][3]
            for item in self["items"]:
                curElem = item.element
                x = sizer_pad[0]

                # Horizontal Alingment
                if self["itemAlign"] & self.A_Left:
                    # Items are alligned by their Left edge
                    x -= DGH.getRealLeft(curElem)
                    # Horizontal adjustment to the box' size
                    x += self["frameSize"][0]

                    # get the new left and right if we should resize the box
                    b_left = 0
                    b_right = max(b_right, DGH.getRealWidth(curElem))
                elif self["itemAlign"] & self.A_Right:
                    # Items are alligned by their Right edge
                    x -= DGH.getRealRight(curElem)
                    # Horizontal adjustment to the box' size
                    x += self["frameSize"][1]

                    # get the new left and right if we should resize the box
                    b_left = min(b_left, -DGH.getRealWidth(curElem))
                    b_right = 0
                else:
                    # Items are alligned by their Center
                    b_left = min(b_left, DGH.getRealLeft(curElem))
                    b_right = max(b_right, DGH.getRealRight(curElem))

                # place the element and calculate the next y position
                curElem.setPos(x, 0, nextY - DGH.getRealTop(curElem))
                itemHeight = (DGH.getRealHeight(curElem) + margin_top + margin_bottom)
                nextY -= itemHeight
                b_bottom = nextY
                itemsHeight += itemHeight

        elif self['orientation'] == DGG.VERTICAL_INVERTED:
            # Vertical - Bottom to Top
            if not self["autoUpdateFrameSize"]:
                if self["frameSize"] != None:
                    nextY = self["frameSize"][2]
            for item in self["items"]:
                curElem = item.element
                x = sizer_pad[0]
                if self["itemAlign"] & self.A_Left:
                    # Items are alligned by their Left edge
                    x -= DGH.getRealLeft(curElem)
                    # Horizontal adjustment to the box' size
                    x += self["frameSize"][0]

                    # get the new left and right if we should resize the box
                    b_left = 0
                    b_right = max(b_right, DGH.getRealWidth(curElem))
                elif self["itemAlign"] & self.A_Right:
                    x -= DGH.getRealRight(curElem)
                    # Horizontal adjustment to the box' size
                    x += self["frameSize"][1]

                    # get the new left and right if we should resize the box
                    b_left = min(b_left, -DGH.getRealWidth(curElem))
                    b_right = 0
                else:
                    # Items are alligned by their Center
                    b_left = min(b_left, DGH.getRealLeft(curElem))
                    b_right = max(b_right, DGH.getRealRight(curElem))

                # place the element and calculate the next y position
                curElem.setPos(x, 0, nextY - DGH.getRealBottom(curElem))
                itemHeight = (DGH.getRealHeight(curElem) + margin_top + margin_bottom)
                nextY += itemHeight
                b_bottom = nextY
                itemsHeight += itemHeight

        else:
            raise ValueError('Invalid value for orientation: %s' % (self['orientation']))

        if self["autoUpdateFrameSize"]:
            self["frameSize"] = (b_left+(-sizer_pad[0]), b_right+sizer_pad[0], b_bottom+(-sizer_pad[1]), b_top+sizer_pad[1])
        else:
            if self['orientation'] in [DGG.HORIZONTAL, DGG.HORIZONTAL_INVERTED]:
                # update Horizontal Align for the whole item block
                if self["itemAlign"] & self.A_Center:
                    if self['orientation'] == DGG.HORIZONTAL_INVERTED:
                        xShift = DGH.getRealWidth(self)/2 - itemsWidth/2
                    else:
                        xShift = DGH.getRealWidth(self)/2 - itemsWidth/2
                    for item in self["items"]:
                        if self['orientation'] == DGG.HORIZONTAL_INVERTED:
                            #item.element.setX(item.element.getX() - xShift)
                            pass
                        else:
                            item.element.setX(item.element.getX() + xShift)
                elif self["itemAlign"] & self.A_Right:
                    xShift = DGH.getRealWidth(self)
                    if self['orientation'] == DGG.HORIZONTAL_INVERTED:
                        xShift = -xShift
                    for item in self["items"]:
                        item.element.setX(item.element.getX() + xShift)

            elif self['orientation'] in [DGG.VERTICAL, DGG.VERTICAL_INVERTED]:
                # update Vertical Align for Horizontally elements
                if self["itemAlign"] & self.A_Middle:
                    if self['orientation'] == DGG.VERTICAL_INVERTED:
                        yShift = DGH.getRealHeight(self)/2 + itemsHeight/2
                    else:
                        yShift = DGH.getRealHeight(self)/2 - itemsHeight/2
                    for item in self["items"]:
                        item.element.setZ(item.element.getZ() - yShift)
                elif self["itemAlign"] & self.A_Bottom:
                    if self['orientation'] == DGG.VERTICAL_INVERTED:
                        yShift = DGH.getRealHeight(self)/2 + itemsHeight/2
                    else:
                        yShift = DGH.getRealHeight(self) - itemsHeight
                    for item in self["items"]:
                        item.element.setZ(item.element.getZ() - yShift)

        #TODO: Maybe the item index has to be changed for inverted positioning
        # store item block edges
        self.itemsLeft = b_left + (-sizer_pad[0]) + self.getX()
        self.itemsRight = b_right + sizer_pad[0] + self.getX()
        self.itemsBottom = b_bottom + (-sizer_pad[1]) # + self.getZ()
        self.itemsTop = b_top + sizer_pad[1] # + self.getZ()

        for item in self["items"]:
            if item.updateFunc is not None:
                item.updateFunc()
