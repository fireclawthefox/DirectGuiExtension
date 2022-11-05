"""Implements a pop-up menu containing multiple clickable options and sub-menus."""

__all__ = ['DirectMenuBar']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import *
from direct.gui.DirectLabel import *
from direct.gui.DirectFrame import *
from .DirectBoxSizer import DirectBoxSizer
from .DirectAutoSizer import DirectAutoSizer
from . import DirectGuiHelper as DGH

class DirectMenuBar(DirectBoxSizer):
    def __init__(self, parent = None, **kw):
        optiondefs = (
            # List of items to display on the popup menu
            ('menuItems',       [],             self.setItems),
        )
        self.kw_args_copy = kw.copy()
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectBoxSizer.__init__(self, parent)
        # Call option initialization functions
        self.initialiseoptions(DirectMenuBar)

        self.selected_menu_item = None

        if len(self["menuItems"]) > 0:
            self.refresh()

    def setItems(self):
        self.removeAllItems()

        for item in self["menuItems"]:
            self.addItem(item, skipRefresh=True)
            item.onCloseMenuFunc = self.setSelectedMenuItem
            item.bind(DGG.B1PRESS, self.showPopupMenuItem, [item])
            item.bind(DGG.WITHIN, self.toggleMenuItem, [item])
            item.cancelFrame.bind(DGG.B1PRESS, self.hidePopupMenu, extraArgs=[item])
        self.refresh()

    def setSelectedMenuItem(self, item=None):
        self.selected_menu_item = item

    def showPopupMenuItem(self, item, event=None):
        item.showPopupMenu(event)
        self.setSelectedMenuItem(item)

    def toggleMenuItem(self, otherItem, args=None):
        if self.selected_menu_item is None \
        or self.selected_menu_item == otherItem:
            return

        self.selected_menu_item.hidePopupMenu(hideParentMenu=True)
        otherItem.showPopupMenu()
        self.setSelectedMenuItem(otherItem)

    def hidePopupMenu(self, item, event=None):
        item.hidePopupMenu(event, True)
        self.setSelectedMenuItem()
