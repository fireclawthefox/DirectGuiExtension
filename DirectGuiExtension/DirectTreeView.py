"""This module contains the DirectTreeView class."""

__all__ = ['DirectTreeView']

import os
import uuid
import logging

from panda3d.core import *

from direct.gui.DirectCheckBox import *
from direct.gui.DirectLabel import *
from direct.gui.DirectFrame import *
from .DirectBoxSizer import DirectBoxSizer
from . import DirectGuiHelper as DGH
from direct.gui import DirectGuiGlobals as DGG
#from dataclasses import dataclass

class DirectTreeEntry:
    name = ""
    uuid = uuid.uuid4()
    def __init__(self, name, uuid=None):
        self.name = name
        if uuid:
            self.uuid = uuid

class DirectTreeView(DirectBoxSizer):
    """
    A frame for displaying a tree structure.

    The Trees visualization can be defined by overwriting the createEntry method
    which must return one widget that will be added as a tree node.
    """
    def __init__(self, parent = None, **kw):
        root = Filename.fromOsSpecific(os.path.dirname(__file__))
        optiondefs = (
            ('imageCollapse', f"{root}/data/icons/minusnode.gif", DGG.INITOPT),
            ('imageCollapsed', f"{root}/data/icons/plusnode.gif", DGG.INITOPT),
            ('collapseImageScale', 0.025, self.refreshTree),
            ('collapseFrameSize', (-0.05, 0.05, -0.05, 0.05), self.refreshTree),
            ('treeTextScale', 0.1, self.refreshTree),
            ('tree',    {},   self.refreshTree),
            ('indentationWidth', 0.1, None)
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectBoxSizer.__init__(self, parent, orientation=DGG.VERTICAL, **kw)

        self.collapsedElements = []
        self.indent_level = 0

        # Call option initialization functions
        self.initialiseoptions(DirectTreeView)

        self.refreshTree()

    def refreshTree(self):
        for item in self["items"]:
            item.element.destroy()
        self.removeAllItems(False)
        self.__createTree(self["tree"])
        self.refresh()

    def __createTree(self, branch, indent_level=0):
        for element, sub_branch in branch.items():
            if type(sub_branch) == dict:
                entry = self.createEntry(element, True, indent_level, sub_branch)
                self.addItem(entry, skipRefresh=True)
                if element in self.collapsedElements:
                    continue
                indent_level += 1
                self.__createTree(sub_branch, indent_level)
                indent_level -= 1
            else:
                entry = self.createEntry(element, False, indent_level, sub_branch)
                self.addItem(entry, skipRefresh=True)

    def createEntry(self, element, hasChildren, indent_level, sub_branch):
        frame = DirectFrame(
            frameColor=(0,0,0,0)
        )

        indentation = self["indentationWidth"] * indent_level

        img_scale = self["collapseImageScale"]

        if hasChildren:
            self.createCollapseCheckBox(frame, indentation, element, img_scale)

        element_name = self.getElementName(element)

        lbl = DirectLabel(
            text=element_name,
            scale=self["treeTextScale"],
            text_align=TextNode.ALeft,
            pos=(img_scale*2+0.02+indentation,0,0),
            parent=frame
        )

        frame["frameSize"] = (0, img_scale*2+0.02+indentation+DGH.getRealWidth(lbl), DGH.getRealBottom(lbl), DGH.getRealTop(lbl))

        return frame

    def getElementName(self, element):
        if hasattr(element, "name"):
            return element.name
        elif type(element) == str:
            return element
        else:
            logging.warning(f"Unknow element type {type(element)} for {element}")
        return ""

    def createCollapseCheckBox(self, parent, x_pos, element, img_scale=0.025):
        imgFilter = SamplerState.FT_nearest

        imgCollapse = loader.loadTexture(self["imageCollapse"])
        imgCollapse.setMagfilter(imgFilter)
        imgCollapse.setMinfilter(imgFilter)

        imgCollapsed = loader.loadTexture(self["imageCollapsed"])
        imgCollapsed.setMagfilter(imgFilter)
        imgCollapsed.setMinfilter(imgFilter)

        btnC = DirectCheckBox(
            relief=DGG.FLAT,
            pos=(img_scale+x_pos,0,0.03),
            frameSize=self["collapseFrameSize"],
            frameColor=(0,0,0,0),
            command=self.collapseElement,
            extraArgs=[element],
            image=imgCollapsed if element in self.collapsedElements else imgCollapse,
            uncheckedImage=imgCollapse,
            checkedImage=imgCollapsed,
            image_scale=img_scale,
            isChecked=element in self.collapsedElements,
            parent=parent)
        btnC.setTransparency(TransparencyAttrib.M_alpha)

    def collapseElement(self, collapse, element):
        if element is not None:
            base.messenger.send(f"beforeRefreshTreeView-{id(self)}")
            if collapse:
                self.collapsedElements.append(element)
            else:
                self.collapsedElements.remove(element)
            self.refreshTree()
            base.messenger.send(f"afterRefreshTreeView-{id(self)}")
