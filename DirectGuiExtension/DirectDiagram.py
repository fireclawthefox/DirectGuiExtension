"""This module contains the DirectDiagram class."""

__all__ = ['DirectDiagram']

import math
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from . import DirectGuiHelper as DGH
from direct.directtools.DirectGeometry import LineNodePath

class DirectDiagram(DirectFrame):

    def __init__(self, parent = None, **kw):
        optiondefs = (
            # Define type of DirectGuiWidget
            ('data',           [],          self.refresh),
            ('numPosSteps',     0,          self.refresh),
            ('numPosStepsStep', 1,          self.refresh),
            ('numNegSteps',     0,          self.refresh),
            ('numNegStepsStep', 1,          self.refresh),
            ('numtextScale',    0.05,       self.refresh),
            ('showDataNumbers', False,      self.refresh),
            ('dataNumtextScale',0.05,       self.refresh),
            ('stepAccuracy',    2,          self.refresh),
            ('stepFormat',      float,      self.refresh),
            ('numberAreaWidth', 0.15,          self.refresh),
            #('numStates',      1,           None),
            #('state',          DGG.NORMAL,  None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        self.lines = None
        self.measureLines = None
        self.centerLine = None
        self.xDescriptions = []
        self.points = []

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectDiagram)


    def refresh(self):
        # sanity check so we don't get here to early
        if not hasattr(self, "bounds"): return
        self.frameInitialiseFunc()

        textLeftSizeArea = self['numberAreaWidth']
        # get the left and right edge of our frame
        left = DGH.getRealLeft(self)
        right = DGH.getRealRight(self)
        diagramLeft = left + textLeftSizeArea

        xStep = (DGH.getRealWidth(self) - textLeftSizeArea) / (len(self['data'])-1)
        posYRes = DGH.getRealTop(self) / (self['numPosSteps'] if self['numPosSteps'] > 0 else max(self['data']))
        negYRes = DGH.getRealBottom(self) / (-self['numNegSteps'] if self['numNegSteps'] > 0 else min(self['data']))

        # remove old content
        if self.lines is not None:
            self.lines.removeNode()

        if self.measureLines is not None:
            self.measureLines.removeNode()

        if self.centerLine is not None:
            self.centerLine.removeNode()

        for text in self.xDescriptions:
            text.removeNode()
        self.xDescriptions = []

        for text in self.points:
            text.removeNode()
        self.points = []

        # prepare the line drawings
        self.lines = LineNodePath(parent=self, thickness=3.0, colorVec=(1, 0, 0, 1))
        self.measureLines = LineNodePath(parent=self, thickness=1.0, colorVec=(0, 0, 0, 1))
        self.centerLine = LineNodePath(parent=self, thickness=2.0, colorVec=(0, 0, 0, 1))

        # draw the center line
        self.centerLine.reset()
        self.centerLine.drawLines([((diagramLeft, 0, 0), (right, 0, 0))])
        self.centerLine.create()

        self.xDescriptions.append(
            self.createcomponent(
                'value0', (), None,
                DirectLabel, (self,),
                text = "0",
                text_scale = self['numtextScale'],
                text_align = TextNode.ARight,
                pos = (diagramLeft, 0, -0.01),
                relief = None,
                state = 'normal'))

        # calculate the positive measure lines and add the numbers
        measureLineData = []
        numSteps = (self['numPosSteps'] if self['numPosSteps'] >0 else math.floor(max(self['data']))) + 1
        for i in range(1, numSteps, self['numPosStepsStep']):
            measureLineData.append(
                (
                    (diagramLeft, 0, i*posYRes),
                    (right, 0, i*posYRes)
                )
            )

            calcBase = 1 / DGH.getRealTop(self)
            maxData = self['numPosSteps'] if self['numPosSteps'] >0 else max(self['data'])
            value = self['stepFormat'](round(i * posYRes * calcBase * maxData, self['stepAccuracy']))
            y = i*posYRes
            self.xDescriptions.append(
                self.createcomponent(
                    'value{}'.format(value), (), None,
                    DirectLabel, (self,),
                    text = str(value),
                    text_scale = self['numtextScale'],
                    text_align = TextNode.ARight,
                    pos = (diagramLeft, 0, y-0.025),
                    relief = None,
                    state = 'normal'))

        # calculate the negative measure lines and add the numbers
        numSteps = (self['numNegSteps'] if self['numNegSteps'] >0 else math.floor(abs(min(self['data'])))) + 1
        for i in range(1, numSteps, self['numNegStepsStep']):
            measureLineData.append(
                (
                    (diagramLeft, 0, -i*negYRes),
                    (right, 0, -i*negYRes)
                )
            )

            calcBase = 1 / DGH.getRealBottom(self)
            maxData = self['numPosSteps'] if self['numPosSteps'] >0 else max(self['data'])
            value = self['stepFormat'](round(i * negYRes * calcBase * maxData, self['stepAccuracy']))
            y = -i*negYRes
            self.xDescriptions.append(
                self.createcomponent(
                    'value{}'.format(value), (), None,
                    DirectLabel, (self,),
                    text = str(value),
                    text_scale = self['numtextScale'],
                    text_align = TextNode.ARight,
                    pos = (diagramLeft, 0, y+0.01),
                    relief = None,
                    state = 'normal'))

        # Draw the lines
        self.measureLines.reset()
        self.measureLines.drawLines(measureLineData)
        self.measureLines.create()

        lineData = []
        for i in range(1, len(self['data'])):
            yResA = posYRes if self['data'][i-1] >= 0 else negYRes
            yResB = posYRes if self['data'][i] >= 0 else negYRes
            lineData.append(
                (
                    # Point A
                    (diagramLeft+(i-1)*xStep, 0, self['data'][i-1] * yResA),
                    # Point B
                    (diagramLeft+i*xStep, 0, self['data'][i] * yResB)
                )
            )

            if (self['showDataNumbers']):
                value = round(self['data'][i-1], self['stepAccuracy'])
                self.points.append(
                    self.createcomponent(
                        'value{}'.format(value), (), None,
                        DirectLabel, (self,),
                        text = str(value),
                        text_scale = self['dataNumtextScale'],
                        text_align = TextNode.ARight,
                        pos = (diagramLeft+(i-1)*xStep, 0, self['data'][i-1] * yResA),
                        relief = None,
                        state = 'normal'))

        # Draw the lines
        self.lines.reset()
        self.lines.drawLines(lineData)
        self.lines.create()
