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
    DefDynGroups = ('value', 'dataNum')

    def __init__(self, parent = None, **kw):
        optiondefs = (
            # Define type of DirectGuiWidget
            ('data',           [],  self.refresh),
            ('numPosSteps',     0,          self.refresh),
            ('numPosStepsStep', 1,          self.refresh),
            ('numNegSteps',     0,          self.refresh),
            ('numNegStepsStep', 1,          self.refresh),
            ('numtextScale',    0.05,       self.refresh),
            ('showDataNumbers', False,      self.refresh),
            ('dataNumtextScale',0.05,       self.refresh),
            ('stepAccuracy',    2,          self.refresh),
            ('stepFormat',      float,      self.refresh),
            ('numberAreaWidth', 0.1,        self.refresh),
            ('numberAreaPad',   0.05,       self.refresh),
            #('numStates',      1,           None),
            #('state',          DGG.NORMAL,  None),
            ("frameSize",       (-0.5, 0.5, -0.5, 0.5), self.setFrameSize),
            ('pad',             (0.05, 0.05), self.__pad)
            )
        self.kw_args_copy = kw.copy()
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs, dynamicGroups=self.DefDynGroups)

        self.lines = None
        self.measureLines = None
        self.centerLine = None
        self.xDescriptions = []
        self.points = []

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectDiagram)

        self.refresh()

    def __pad(self):
        self.resetFrameSize()
        self.refresh()

    def setData(self, data):
        self["data"] = [float(value) for value in data]
        self.refresh()

    def refresh(self):
        # sanity check so we don't get here to early
        if not hasattr(self, "bounds"): return
        self.frameInitialiseFunc()

        textLeftSizeArea = self['numberAreaWidth']
        numberAreaPad = self["numberAreaPad"]
        # get the left and right edge of our frame
        left = DGH.getRealLeft(self) / self.getScale().x + self["pad"][0]
        right = DGH.getRealRight(self) / self.getScale().x - self["pad"][0]
        diagramLeft = left + textLeftSizeArea + numberAreaPad

        # If there is no data we can not calculate 'numPosSteps' and 'numNegSteps'
        if not self["data"] and self["numPosSteps"] <= 0:
            numPosSteps = 5
        else:
            numPosSteps = self['numPosSteps']

        if not self["data"] and self["numNegSteps"] <= 0:
            numNegSteps = 5
        else:
            numNegSteps = self['numNegSteps']

        xStep = (DGH.getRealWidth(self) / self.getScale().x - textLeftSizeArea - numberAreaPad - self["pad"][0]*2) / max(1, len(self['data'])-1)
        posYRes = numPosSteps if numPosSteps > 0 else int(max(self['data']))
        posYRes = (DGH.getRealTop(self) / self.getScale().z - self["pad"][1]) / (posYRes if posYRes != 0 else 1)
        negYRes = -numNegSteps if numNegSteps > 0 else int(min(self['data']))
        negYRes = (DGH.getRealBottom(self) / self.getScale().z + self["pad"][1]) / (negYRes if negYRes != 0 else 1)

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

        # Make sure to include any options set earlier
        itemKW = {}
        for i in self.kw_args_copy:
            if i.startswith("value_"):
                itemKW[i.removeprefix("value_")] = self.kw_args_copy[i]

        toRemove = ["text", "text_scale", "text_align", "pos", "relief", "state"]
        for r in toRemove:
            if r in itemKW:
                del itemKW[r]

        self.xDescriptions.append(
            self.createcomponent(
                'value0', (), "value",
                DirectLabel, (self,),
                text = "0",
                text_scale = self['numtextScale'],
                text_align = TextNode.ARight,
                pos = (diagramLeft - numberAreaPad, 0, -0.01),
                relief = None,
                state = 'normal',
                **itemKW
            )
        )

        # calculate the positive measure lines and add the numbers
        measureLineData = []
        numSteps = (numPosSteps if numPosSteps > 0 else math.floor(max(self['data']))) + 1
        for i in range(1, numSteps, self['numPosStepsStep']):
            measureLineData.append(
                (
                    (diagramLeft, 0, i*posYRes),
                    (right, 0, i*posYRes)
                )
            )

            calcBase = 1 / (DGH.getRealTop(self) / self.getScale().z - self["pad"][1])
            maxData = numPosSteps if numPosSteps > 0 else max(self['data'])
            value = self['stepFormat'](round(i * posYRes * calcBase * maxData, self['stepAccuracy']))
            y = i*posYRes
            self.xDescriptions.append(
                self.createcomponent(
                    'value{}'.format(value), (), "value",
                    DirectLabel, (self,),
                    text = str(value),
                    text_scale = self['numtextScale'],
                    text_align = TextNode.ARight,
                    pos = (diagramLeft - numberAreaPad, 0, y-0.025),
                    relief = None,
                    state = 'normal',
                    **itemKW
                )
            )

        # calculate the negative measure lines and add the numbers
        if numNegSteps > 0:
            numSteps = numNegSteps + 1
        elif min(self["data"]) >= 0:
            numSteps = 1
        else:
            numSteps = math.floor(abs(min(self['data']))) + 1
        for i in range(1, numSteps, self['numNegStepsStep']):
            measureLineData.append(
                (
                    (diagramLeft, 0, -i*negYRes),
                    (right, 0, -i*negYRes)
                )
            )

            calcBase = 1 / (DGH.getRealBottom(self) / self.getScale().z + self["pad"][1])
            maxData = numNegSteps if numNegSteps > 0 else abs(min(self['data']))
            value = self['stepFormat'](round(i * negYRes * calcBase * maxData, self['stepAccuracy']))
            y = -i*negYRes
            self.xDescriptions.append(
                self.createcomponent(
                    'value{}'.format(value), (), "value",
                    DirectLabel, (self,),
                    text = str(value),
                    text_scale = self['numtextScale'],
                    text_align = TextNode.ARight,
                    pos = (diagramLeft - numberAreaPad, 0, y+0.01),
                    relief = None,
                    state = 'normal',
                    **itemKW
                )
            )

        # Draw the lines
        self.measureLines.reset()
        self.measureLines.drawLines(measureLineData)
        self.measureLines.create()

        # Make sure to include any options set earlier in dataNum components
        itemKW = {}
        for i in self.kw_args_copy:
            if i.startswith("dataNum_"):
                itemKW[i.removeprefix("dataNum_")] = self.kw_args_copy[i]

        toRemove = ["text", "text_scale", "text_align", "pos", "relief", "state"]
        for r in toRemove:
            if r in itemKW:
                del itemKW[r]

        lineData = []
        for i in range(len(self['data'])):
            yResB = posYRes if self['data'][i] >= 0 else negYRes
            if i > 0:
                yResA = posYRes if self['data'][i-1] >= 0 else negYRes
                lineData.append(
                    (
                        # Point A
                        (diagramLeft+(i-1)*xStep, 0, self['data'][i-1] * yResA),
                        # Point B
                        (diagramLeft+i*xStep, 0, self['data'][i] * yResB)
                    )
                )

            if (self['showDataNumbers']):
                value = round(self['data'][i], self['stepAccuracy'])
                self.points.append(
                    self.createcomponent(
                        'dataLabel{}'.format(i), (), "dataLabel",
                        DirectLabel, (self,),
                        text = str(value),
                        text_scale = self['dataNumtextScale'],
                        text_align = TextNode.ARight,
                        pos = (diagramLeft + i * xStep, 0, self['data'][i] * yResB),
                        relief = None,
                        state = 'normal',
                        **itemKW
                    )
                )

        # Draw the lines
        self.lines.reset()
        self.lines.drawLines(lineData)
        self.lines.create()
