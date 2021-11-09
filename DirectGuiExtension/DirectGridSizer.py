"""This module contains the DirectBoxSizer class."""

__all__ = ['DirectGridSizer']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from . import DirectGuiHelper as DGH


class DirectItemContainer():
    def __init__(self, element, rowIndex, columnIndex, widthInColumns, heightInRows):
        self.element = element
        self.rowIndex = rowIndex
        self.columnIndex = columnIndex
        self.widthInColumns = widthInColumns
        self.heightInRows = heightInRows

class DirectGridSizer(DirectFrame):
    """
    A frame to add multiple other directGui elements to that will then be
    automatically be placed stacked next to each other.
    """
    def __init__(self, parent = None, **kw):
        self.skipInitRefresh = True
        optiondefs = (
            # Define type of DirectGuiWidget
            ('items',          [],          self.refresh),
            ('pgFunc',         PGItem,      None),
            ('numStates',      1,           None),
            ('state',          DGG.NORMAL,  None),
            ('borderWidth',    (0, 0),      self.setBorderWidth),

            ('itemMargin',     (0,0,0,0),   self.refresh),
            ('numRows',        4,           self.refresh),
            ('numColumns',     4,           self.refresh),
            ('autoUpdateFrameSize', True,   None),
            ('boxAlign',    TextNode.ALeft, self.refresh),

            ('suppressMouse',  0,           None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectGridSizer)

        self.skipInitRefresh = False
        # initialize once at the end
        self.refresh()

    def addItem(self, element, row, column, widthInColumns=1, heightInRows=1):
        """
        Adds the given item to this panel stack
        """
        element.reparentTo(self)
        container = DirectItemContainer(element, row, column, widthInColumns, heightInRows)
        self["items"].append(container)
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

    def clearItems(self):
        for item in self["items"][:]:
            self["items"].remove(item)
        self.refresh()

    def refresh(self):
        """
        Recalculate the position of every item in this panel and set the frame-
        size of the panel accordingly if auto update is enabled.
        """
        # sanity checks so we don't get here to early
        if self.skipInitRefresh: return
        if not hasattr(self, "bounds"): return

        for item in self["items"]:
            item.element.frameInitialiseFunc()

        # variables to store the maximum row and column widths
        rowHeights = [0]*self["numRows"]
        columnWidths = [0]*self["numColumns"]

        b_top = 0
        b_bottom = 0
        b_left = 0
        b_right = 0

        pad_x = self["pad"][0]
        pad_y = self["pad"][1]

        margin_left = self["itemMargin"][0]
        margin_right = self["itemMargin"][1]
        margin_bottom = self["itemMargin"][2]
        margin_top = self["itemMargin"][3]

        if self["autoUpdateFrameSize"]:
            self["frameSize"] = (0, 0, 0, 0)

        # get the max row and column sizes
        for r in range(self["numRows"]):
            for c in range(self["numColumns"]):

                for item in self["items"]:
                    if item.rowIndex == r and item.columnIndex == c:
                        rowHeights[r] = max(rowHeights[r], DGH.getRealHeight(item.element) / item.heightInRows + margin_bottom + margin_top)
                        columnWidths[c] = max(columnWidths[c], DGH.getRealWidth(item.element) / item.widthInColumns + margin_left + margin_right)
                        break

        for item in self["items"]:
            r = item.rowIndex
            c = item.columnIndex

            if r >= self["numRows"]:
                raise IndexError(f"Row index defined in item {item.element} exceeded number of rows in grid sizer: numRows={self['numRows']}")
            if c >= self["numColumns"]:
                raise IndexError(f"Column index defined in item {item.element} exceeded number of columns in grid sizer: numColumns={self['numColumns']}")

            z = 0
            for i in range(r):
                z -= rowHeights[i]

            x = 0
            for i in range(c):
                x += columnWidths[i]

            item.element.setPos(pad_x + x + margin_left, 0, pad_y + z + margin_top)

        if self["autoUpdateFrameSize"]:

            for item in self["items"]:
                b_left = min(b_left, DGH.getRealLeft(item.element) + item.element.getX())
                b_right = max(b_right, DGH.getRealRight(item.element) + item.element.getX())

                b_bottom = min(b_bottom, DGH.getRealBottom(item.element) + item.element.getZ())
                b_top = max(b_top, DGH.getRealTop(item.element) + item.element.getZ())

            self["frameSize"] = [b_left+pad_x, b_right+pad_x, b_bottom+pad_y, b_top+pad_y]

            xShift = 0
            if self["boxAlign"] == TextNode.ACenter:
                self["frameSize"][0] = self["frameSize"][0] - self["frameSize"][1]/2
                self["frameSize"][1] = self["frameSize"][1]/2
                xShift = -self["frameSize"][1]/2
            if self["boxAlign"] == TextNode.ARight:
                self["frameSize"][0] = self["frameSize"][1]
                self["frameSize"][1] = self["frameSize"][0]
                xShift = -self["frameSize"][1]
