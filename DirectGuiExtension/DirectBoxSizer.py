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

        self.__refresh_frame_size()

        #
        # Update Item Positions
        #
        if self['orientation'] == DGG.HORIZONTAL:
            # Horizontal - Left to Right placement
            self.__refresh_horizontal_ltr()
        elif self['orientation'] == DGG.HORIZONTAL_INVERTED:
            # Horizontal - Right to Left
            self.__refresh_horizontal_rtl()
        elif self['orientation'] == DGG.VERTICAL:
            # Vertical - Top to Bottom
            self.__refresh_vertical_ttb()
        elif self['orientation'] == DGG.VERTICAL_INVERTED:
            # Vertical - Bottom to Top
            self.__refresh_vertical_btt()
        else:
            raise ValueError('Invalid value for orientation: %s' % (self['orientation']))

        for item in self["items"]:
            if item.updateFunc is not None:
                item.updateFunc()

    def __refresh_frame_size(self):
        if not self["autoUpdateFrameSize"]: return

        width = self.__get_items_width()# + self["pad"][0]*2
        height = self.__get_items_height()# + self["pad"][1]*2

        # dependent on orientation, start at 0 and extend to the
        # maximum height or width and keep the respective other
        # direction centered
        if self['orientation'] == DGG.HORIZONTAL:
            self["frameSize"] = (0, width, -height/2, height/2)
        elif self['orientation'] == DGG.HORIZONTAL_INVERTED:
            self["frameSize"] = (-width, 0, -height/2, height/2)
        elif self['orientation'] == DGG.VERTICAL:
            self["frameSize"] = (-width/2, width/2, -height, 0)
        elif self['orientation'] == DGG.VERTICAL_INVERTED:
            self["frameSize"] = (-width/2, width/2, 0, height)

    def __get_items_width(self):
        '''
        Get the maximum item width
        '''
        width = 0
        for item in self["items"]:
            item_width = (
                DGH.getRealWidth(item.element)
                + self["itemMargin"][0]   # margin left
                + self["itemMargin"][1])  # margin right
            if self['orientation'] in [DGG.VERTICAL, DGG.VERTICAL_INVERTED]:
                # look for the widest item
                width = max(width, item_width)
            else:
                # add up all item widths
                width += item_width
        return width

    def __get_items_height(self):
        '''
        Get the maximum item height
        '''
        height = 0
        for item in self["items"]:
            item_height = (
                DGH.getRealHeight(item.element)
                + self["itemMargin"][3]   # margin top
                + self["itemMargin"][2])  # margin bottom
            if self['orientation'] in [DGG.HORIZONTAL, DGG.HORIZONTAL_INVERTED]:
                # look for the talest item
                height = max(height, item_height)
            else:
                # add up all item heights
                height += item_height
        return height

    #
    # ITEM ORDER POSITION REFRESH
    #
    # HORIZONTAL
    def __refresh_horizontal_ltr(self):
        # Horizontal - Left to Right placement
        # get the left side of the box sizer frame
        nextX = DGH.getRealLeft(self)

        # go through all items in the box and place them
        for item in self["items"]:
            # place the element and calculate the next x position
            y = self.__get_vertical_item_alignment(item.element)
            item.element.setPos(nextX - DGH.getRealLeft(item.element), 0, y)
            nextX += DGH.getRealWidth(item.element)


    def __refresh_horizontal_rtl(self):
        # Horizontal - Right to Left
        # get the right side of the box sizer frame
        nextX = DGH.getRealRight(self)

        # go through all items in the box and place them
        for item in self["items"]:
            # place the element and calculate the next x position
            y = self.__get_vertical_item_alignment(item.element)
            item.element.setPos(nextX - DGH.getRealRight(item.element), 0, y)
            nextX -= DGH.getRealWidth(item.element)

    # VERTICAL
    def __refresh_vertical_ttb(self):
        # Vertical - Top to Bottom
        # get the top side of the box sizer frame
        nextY = DGH.getRealTop(self)

        # go through all items in the box and place them
        for item in self["items"]:
            # place the element and calculate the next y position
            x = self.__get_horizontal_item_alignment(item.element)
            item.element.setPos(x, 0, nextY - DGH.getRealTop(item.element))
            nextY -= DGH.getRealHeight(item.element)

    def __refresh_vertical_btt(self):
        # Vertical - Bottom to Top
        # get the bottom side of the box sizer frame
        nextY = DGH.getRealBottom(self)

        # go through all items in the box and place them
        for item in self["items"]:
            # place the element and calculate the next y position
            x = self.__get_horizontal_item_alignment(item.element)
            item.element.setPos(x, 0, nextY - DGH.getRealBottom(item.element))
            nextY += DGH.getRealHeight(item.element)

    #
    # ITEM ALIGN POSITION CALCULATIONS
    #
    def __get_horizontal_item_alignment(self, curElem):
        # Horizontal Alingment
        if self["itemAlign"] & self.A_Left:
            # get the left side of the frame
            x = self["frameSize"][0]
            # shift x right to be aligned with the items left side
            x -= DGH.getRealLeft(curElem)
            return x
        elif self["itemAlign"] & self.A_Right:
            # get the right side of the frame
            x = self["frameSize"][1]
            # shift x left to be aligned with the items right side
            x -= DGH.getRealRight(curElem)
            return x
        elif self["itemAlign"] & self.A_Center:
            # aligned by the center of the frame
            self_l = DGH.getRealLeft(self)
            self_r = DGH.getRealRight(self)
            x = (self_l + self_r) / 2
            # shift x by items center shift
            item_l = DGH.getRealLeft(curElem)
            item_r = DGH.getRealRight(curElem)
            x += (item_l + item_r) / 2
            return x
        return 0

    def __get_vertical_item_alignment(self, curElem):
        # Vertical Alingment
        if self["itemAlign"] & self.A_Bottom:
            # Vertical adjustment to the box' size
            y = DGH.getRealBottom(self)# self["frameSize"][2]
            # shift y up to be aligned with the items bottom side
            y += DGH.getRealBottom(curElem)
            return y
        elif self["itemAlign"] & self.A_Top:
            # Items are alligned by their upper edge
            y = DGH.getRealTop(self)# self["frameSize"][3]
            # shift y down to be aligned with the items top side
            y -= DGH.getRealTop(curElem)
            return y
        elif self["itemAlign"] & self.A_Middle:
            # Items are alligned by their center
            # aligned by the center of the frame
            self_t = DGH.getRealTop(self)
            self_b = DGH.getRealBottom(self)
            y = (self_t + self_b) / 2
            # shift y by items center shift
            item_t = DGH.getRealTop(curElem)
            item_b = DGH.getRealBottom(curElem)
            y += (item_t + item_b) / 2
            return y
        return 0
