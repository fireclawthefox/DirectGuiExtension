"""Implements a pop-up menu containing multiple clickable options and sub-menus."""

__all__ = ['DirectMenuItem']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import *
from direct.gui.DirectLabel import *
from direct.gui.DirectFrame import *
from .DirectBoxSizer import DirectBoxSizer
from . import DirectGuiHelper as DGH

DGG.MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
DGG.MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'
DGG.LEFT = "left"
DGG.RIGHT = "right"
DGG.ABOVE = "above"
DGG.BELOW = "below"

class DirectMenuItemEntry:
    def __init__(self, text, command, extraArgs=None):
        self.text = text
        self.command = command
        self.extraArgs = extraArgs

class DirectMenuItemSubMenu:
    def __init__(self, text, items):
        self.text = text
        self.items = items

class DirectMenuSeparator:
    def __init__(self, height=0.05, padding=(0, 0.1)):
        self.height = height
        self.padding = padding

class DirectMenuItem(DirectButton):
    def __init__(self, parent = None, **kw):
        optiondefs = (
            # List of items to display on the popup menu
            ('items',       [],             self.setItems),
            # The position of the popup menu
            # possible positions: left, above, right, below
            ('popupMenuLocation', DGG.BELOW, None),
            # Background color to use to highlight popup menu items
            ('highlightColor', (.5, .5, .5, 1), None),
            # Background color of unhighlighted menu items
            ('itemFrameColor', None, None),
            # Alignment to use for text on popup menu button
            # Changing this breaks button layout
            ('text_align',  TextNode.ALeft, None),
            # Remove press effect because it looks a bit funny
            ('pressEffect',     0,          DGG.INITOPT),
            ('isSubMenu',       False,      None),
            ('parentMenu',      None,       None),
            # color of the separator line
            ('separatorFrameColor', (.2, .2, .2, 1),   None),
           )
        self.kw_args_copy = kw.copy()
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)
        # Initialize superclasses
        DirectButton.__init__(self, parent)
        # This is created when you set the menu's items
        self.popupMenu = None
        # the selected item
        self.highlightedItem = None
        # A big screen encompassing frame to catch the cancel clicks
        self.cancelFrame = self.createcomponent(
            'cancelframe', (), None,
            DirectFrame, (self,),
            frameSize = (-1, 1, -1, 1),
            relief = None,
            state = 'normal')
        # Make sure this is on top of all the other widgets
        self.cancelFrame.setBin('gui-popup', 0)
        self.cancelFrame.node().setBounds(OmniBoundingVolume())
        self.cancelFrame.bind(DGG.B1PRESS, self.hidePopupMenu, extraArgs=[True])
        # Default action on press is to show popup menu
        self.bind(DGG.B1PRESS, self.showPopupMenu)
        # Check if item is highlighted on release and select it if it is
        self.bind(DGG.B1RELEASE, self._selectHighlighted)
        # Call option initialization functions
        self.initialiseoptions(DirectMenuItem)
        # Need to call this since we explicitly set frame size
        self.resetFrameSize()

    def setItems(self):
        """
        self['items'] = list of DirectMenuItemEntry and DirectMenuItemSubMenu
        Create new popup menu to reflect specified set of items
        """
        # Remove old component if it exits
        if self.popupMenu != None:
            self.destroycomponent('popupMenu')
        # Create new component
        self.popupMenu = self.createcomponent('popupMenu', (), None,
                                              DirectBoxSizer,
                                              (self,),
                                              itemAlign = DirectBoxSizer.A_Left,
                                              orientation = DGG.VERTICAL,
                                              )
        # Make sure it is on top of all the other gui widgets
        self.popupMenu.setBin('gui-popup', 0)
        if not self['items']:
            return
        # Create a new component for each item
        # Find the maximum extents of all items
        itemIndex = 0
        self.minX = self.maxX = self.minZ = self.maxZ = None
        for item in self['items']:
            if type(item) is DirectMenuItemSubMenu:
                subMenuKW = self.kw_args_copy.copy()
                toRemove = ["text", "popupMenuLocation", "items", "isSubMenu", "parentMenu", "frameSize", "scale"]
                for r in toRemove:
                    if r in subMenuKW:
                        del subMenuKW[r]

                c = self.createcomponent(
                    'item%d' % itemIndex, (), 'item',
                    DirectMenuItem,
                    (self.popupMenu,),
                    text=item.text,
                    popupMenuLocation=DGG.RIGHT,
                    items=item.items,
                    isSubMenu=True,
                    parentMenu=self,
                    **subMenuKW,
                    )
            elif type(item) is DirectMenuSeparator:
                c = self.createcomponent(
                    'separator%d' % itemIndex, (), 'separator',
                    DirectFrame,
                    (self.popupMenu,),
                    frameColor=self["separatorFrameColor"] if self["separatorFrameColor"] else self["frameColor"],
                    # set width to 0, we'll fit it to the width of the box later
                    frameSize=(0, 0, -item.height/2, item.height/2),
                    pad=item.padding,
                    )
            else:
                c = self.createcomponent(
                    'item%d' % itemIndex, (), 'item',
                    DirectButton,
                    (self.popupMenu,),
                    text=item.text,
                    text_align=TextNode.ALeft,
                    command=item.command,
                    extraArgs=item.extraArgs,
                    frameColor=self["itemFrameColor"] if self["itemFrameColor"] else self["frameColor"])

                c.bind(DGG.B1RELEASE, self.hidePopupMenu, extraArgs=[True])
            bounds = DGH.getBounds(c)

            c.resetFrameSize()

            self.popupMenu.addItem(c)

            bw_w = c["borderWidth"][0] + c["pad"][0]
            bw_h = c["borderWidth"][1] + c["pad"][1]

            # accept events only for actual selectable elements
            if type(item) is not DirectMenuSeparator:
                self.minX = min(self.minX if self.minX else bounds[0]-bw_w, bounds[0]-bw_w)
                self.maxX = max(self.maxX if self.maxX else bounds[1]+bw_w, bounds[1]+bw_w)
                self.minZ = min(self.minZ if self.minZ else bounds[2]-bw_h, bounds[2]-bw_h)
                self.maxZ = max(self.maxZ if self.maxZ else bounds[3]+bw_h, bounds[3]+bw_h)

                # Highlight background when mouse is in item
                c.bind(DGG.WITHIN,
                          lambda x, item=c: self._highlightItem(item))
                # Restore specified color upon exiting
                fc = self['itemFrameColor'] if self['itemFrameColor'] else c['frameColor']
                c.bind(DGG.WITHOUT,
                          lambda x, item=c, fc=fc: self._unhighlightItem(item, fc))
                c.bind(DGG.MWDOWN, self.scrollPopUpMenu, [-1])
                c.bind(DGG.MWUP, self.scrollPopUpMenu, [1])

            itemIndex += 1

        # Calc max width and height
        if self.minX is None:
            self.minX = 0
            self.maxX = 1
            self.minZ = 0
            self.maxZ = 1
        self.maxWidth = self.maxX - self.minX
        self.maxHeight = self.maxZ - self.minZ
        # Adjust frame size for each item and bind actions to mouse events
        for i in self.popupMenu["items"]:
            item = i.element
            if type(item) is DirectFrame:
                fs = item["frameSize"]
                item['frameSize'] = (self.minX, self.maxX, fs[2], fs[3])
            else:
                # make all entries the same size
                item['frameSize'] = (self.minX, self.maxX, self.minZ, self.maxZ)

        # HACK: Set the user defined popup menu relief here so we don't
        # break the bounds calculation.
        self.popupMenu.setRelief(self['popupMenu_relief'])

        # Set initial state
        self.hidePopupMenu()
        self.bind(DGG.MWDOWN, self.scrollPopUpMenu, [-1])
        self.bind(DGG.MWUP, self.scrollPopUpMenu, [1])
        self.cancelFrame.bind(DGG.MWDOWN, self.scrollPopUpMenu, [-1])
        self.cancelFrame.bind(DGG.MWUP, self.scrollPopUpMenu, [1])

        #self.popupMenu.refresh()

    def showPopupMenu(self, event = None):
        """
        Make popup visible.
        Adjust popup position if default position puts it outside of
        visible screen region
        """

        # Needed attributes (such as minZ) won't be set unless the user has specified
        # items to display. Let's assert that we've given items to work with.
        items = self['items']
        assert items and len(items) > 0, 'Cannot show an empty popup menu! You must add items!'

        # Show the menu
        self.popupMenu.show()
        # Compute bounds
        b = DGH.getBounds(self) #self.getBounds()
        fb = DGH.getBounds(self.popupMenu) #self.popupMenu.getBounds()
        self.popupMenu["itemAlign"] =  DirectBoxSizer.A_Left

        if self['popupMenuLocation'] == DGG.RIGHT:
            # Position menu to the right of the menu
            self.popupMenu.setX(
                DGH.getRealRight(self) / self.getScale()[0]
                + -DGH.getRealLeft(self.popupMenu))
        elif self['popupMenuLocation'] == DGG.LEFT:
            # Position to the left
            # change the item align to right aligned so it will be fitted
            # to the left of the menu
            self.popupMenu["itemAlign"] = DirectBoxSizer.A_Right
            # reposition the popup to the left
            self.popupMenu.setX(-DGH.getRealRight(self.popupMenu))
        else:
            # position to line up with the left edge if the menu is above or below
            self.popupMenu.setX(-DGH.getRealLeft(self.popupMenu))

        if self['popupMenuLocation'] == DGG.ABOVE:
            # Try to set height to line up selected item with button
            self.popupMenu.setZ(
                self, self.maxZ - fb[2])
        elif self['popupMenuLocation'] == DGG.BELOW:
            # Try to set height to line up selected item with button
            self.popupMenu.setZ(
                self, self.minZ+self["item_pad"][0]*2)
        else:
            # Try to set height to line up selected item with button
            self.popupMenu.setZ(
                self, self.maxZ)
        # Make sure the whole popup menu is visible
        pos = self.popupMenu.getPos(render2d)
        scale = self.popupMenu.getScale(render2d)
        # How are we doing relative to the right side of the screen
        maxX = pos[0] + fb[1] * scale[0]
        if maxX > 1.0:
            # Need to move menu to the left
            self.popupMenu.setX(render2d, pos[0] + (1.0 - maxX))
        # How are we doing relative to the right side of the screen
        minX = pos[0]
        if minX < -1.0:
            # Need to move menu to the right
            self.popupMenu.setX(render2d, -1 )
        # How about up and down?
        minZ = pos[2] + fb[2] * scale[2]
        maxZ = pos[2] + fb[3] * scale[2]
        if minZ < -1.0:
            # Menu too low, move it up
            self.popupMenu.setZ(render2d, pos[2] + (-1.0 - minZ))

            # recheck the top position once repositioned
            pos = self.popupMenu.getPos(render2d)
            maxZ = pos[2] + fb[3] * scale[2]
            if maxZ > 1.0:
                # Menu too large to show on screen entirely
                # Try to set height to line up selected item with button
                self.popupMenu.setZ(
                    self, self.minZ)
        elif maxZ > 1.0:
            # Menu too high, move it down
            self.popupMenu.setZ(render2d, pos[2] + (1.0 - maxZ))
            # recheck the top position once repositioned
            pos = self.popupMenu.getPos(render2d)
            minZ = pos[2] + fb[2] * scale[2]
            if minZ < -1.0:
                # Menu too large to show on screen entirely
                # Try to set height to line up selected item with button
                self.popupMenu.setZ(
                    self, self.minZ)
        # Also display cancel frame to catch clicks outside of the popup
        self.cancelFrame.show()
        # Position and scale cancel frame to fill entire window
        self.cancelFrame.setPos(render2d, 0, 0, 0)
        self.cancelFrame.setScale(render2d, 1, 1, 1)

        #self.popupMenu.refresh()

    def hidePopupMenu(self, event = None, hideParentMenu=False):
        """ Put away popup and cancel frame """
        self.popupMenu.hide()
        self.cancelFrame.hide()

        # call up the ancestry tree
        if hideParentMenu:
            if self['isSubMenu']:
                self['parentMenu'].hidePopupMenu(hideParentMenu=True)

    def scrollPopUpMenu(self, direction, event = None):
        """ Scroll the item frame up and down depending on the direction
        which must be a nummeric value. A positive value will scroll up
        while a negative value will scroll down. It will only work if
        items are out of bounds of the window """
        fb = DGH.getBounds(self.popupMenu)#.getBounds()
        pos = self.popupMenu.getPos(render2d)
        scale = self.popupMenu.getScale(render2d)

        minZ = pos[2] + fb[2] * scale[2]
        maxZ = pos[2] + fb[3] * scale[2]
        if (minZ < -1.0 and direction > 0) or (maxZ > 1.0 and direction < 0):
            oldZ = self.popupMenu.getZ()
            #self.popupMenu.setZ(oldZ + direction * self.maxHeight)

    def _selectHighlighted(self, event=None):
        """
        Check to see if item is highlighted (by cursor being within
        that item).  If so, selected it.  If not, do nothing
        """
        if self.highlightedItem:
            # Pass any extra args to command
            self.highlightedItem['command'](*self.highlightedItem['extraArgs'])
            self.hidePopupMenu(hideParentMenu=True)

    def _highlightItem(self, item):
        """ Set frame color of highlighted item, record index """

        for i in self.popupMenu["items"]:
            # make sure all other items are unhighlighted
            base.messenger.send(DGG.WITHOUT + i.element.guiId, [""])

        item['frameColor'] = self['highlightColor']
        self.highlightedItem = item

        if type(item) is DirectMenuItem:
            if item['isSubMenu']:
                taskMgr.doMethodLater(0.2, item.showPopupMenu, "highlight")

    def _unhighlightItem(self, item, frameColor):
        """ Clear frame color """
        item['frameColor'] = frameColor
        self.highlightedItem = None

        if type(item) is DirectMenuItem:
            if item['isSubMenu']:
                def unhiglight(item):
                    if not item.highlightedItem:
                        item.hidePopupMenu()
                taskMgr.doMethodLater(0.2, unhiglight, "unhighlight", extraArgs=[item])
