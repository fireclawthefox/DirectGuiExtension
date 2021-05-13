#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from panda3d import core as p3d


def getBorderSize(guiItem):
    frameType = guiItem.getFrameType()
    if guiItem["frameSize"] is not None \
    or frameType == p3d.PGFrameStyle.TNone \
    or frameType == p3d.PGFrameStyle.TFlat:
        return (0,0)
    return guiItem["borderWidth"]

def getBounds(guiItem):
    #HACK: Sometimes getBounds returns 0s while a frameSize is actually given
    if guiItem.getBounds() == [0,0,0,0] and guiItem['frameSize'] != (0,0,0,0):
        if guiItem['frameSize'] is not None:
            return guiItem['frameSize']
        else:
            if guiItem.guiItem.getFrame() is not None:
                return guiItem.guiItem.getFrame()
            # well... seems like this element just has no size.
            return guiItem.getBounds()
    return guiItem.getBounds()

def getRealWidth(guiItem):
    return (guiItem.getWidth() + 2 * getBorderSize(guiItem)[0]) * guiItem.getScale()[0]

def getRealHeight(guiItem):
    return (guiItem.getHeight() + 2 * getBorderSize(guiItem)[1]) * guiItem.getScale()[1]

def getRealLeft(guiItem):
    return (getBounds(guiItem)[0] - getBorderSize(guiItem)[0]) * guiItem.getScale()[0]

def getRealRight(guiItem):
    return (getBounds(guiItem)[1] + getBorderSize(guiItem)[0]) * guiItem.getScale()[0]

def getRealTop(guiItem):
    return (getBounds(guiItem)[3] + getBorderSize(guiItem)[1]) * guiItem.getScale()[1]

def getRealBottom(guiItem):
    return (getBounds(guiItem)[2] - getBorderSize(guiItem)[1]) * guiItem.getScale()[1]
