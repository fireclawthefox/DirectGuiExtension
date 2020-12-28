"""This module contains the DirectBoxSizer class."""

__all__ = ['DirectGridSizer']

import calendar
import datetime
from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from . import DirectGuiHelper as DGH
from .DirectGridSizer import DirectGridSizer
from .DirectSpinBox import DirectSpinBox
from .DirectOptionMenu import DirectOptionMenu


class DirectDatePicker(DirectGridSizer):
    def __init__(self, parent = None, **kw):
        optiondefs = (
            ('year',    None,   self.refreshPicker),
            ('month',   None,   self.refreshPicker),
            ('day',     None,   self.refreshPicker),

            ('normalDayFrameColor', None, None),
            ('activeDayFrameColor', None, None),
            ('todayFrameColor', None, None),

            # Define type of DirectGuiWidget
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectGridSizer.__init__(self, parent, numRows=7, numColumns=8, autoUpdateFrameSize=True, itemMargin=[0.005, 0.005, 0.005, 0.005])

        # Call option initialization functions
        self.initialiseoptions(DirectDatePicker)

        # set up the calendar
        self.cal = calendar.Calendar()

        # normal day colors
        self['normalDayFrameColor'] = (
            (0.7,0.7,0.7,1),
            (0.7,0.7,0.7,1),
            (0.7,0.0,0.0,1),
            (0.6,0.6,0.6,1)
        ) if self['normalDayFrameColor'] is None else self['normalDayFrameColor']

        # selected day color
        self['activeDayFrameColor'] = (
            (0.8,0.8,0.8,1),
            (0.8,0.8,0.8,1),
            (0.8,0.0,0.0,1),
            (0.6,0.6,0.6,1)
        ) if self['activeDayFrameColor'] is None else self['activeDayFrameColor']

        # the systems current day color
        self['todayFrameColor'] = (
            (1.0,0.7,0.7,1),
            (0.8,0.8,0.8,1),
            (0.8,0.0,0.0,1),
            (0.6,0.6,0.6,1)
        ) if self['todayFrameColor'] is None else self['todayFrameColor']

        # current date
        now = datetime.datetime.now()

        # add the week header
        weekDays = calendar.weekheader(2).split(" ")
        self.headers = []
        for i in range(1, 8):
            lbl = self.createLabel(str(weekDays[i-1]))
            self.headers.append(lbl)
            self.addItem(lbl, 0, i)

        # add dummy week numbers
        self.weekNumbers = []
        for i in range(1, 7):
            lbl = self.createLabel("--")
            self.weekNumbers.append(lbl)
            self.addItem(lbl, i, 0)

        self.dateButtons = []
        day = 0
        for row in range(1, 7):
            self.dateButtons.append([])
            for column in range(1, 8):
                btn = self.createDateButton(day, False)
                self.dateButtons[row-1].append(btn)
                self.addItem(btn, row, column)
                day += 1

        self.ll = Point3(self["frameSize"][0], self["frameSize"][2])
        self.ur = Point3(self["frameSize"][1], self["frameSize"][3])

        # the year picker
        self.yearPicker = self.createcomponent(
            'yearPicker', (), None,
            DirectSpinBox, (self,),
            valueEntry_width=5,
            scale=0.05,
            minValue=1,
            maxValue=9999,
            repeatdelay=0.125,
            buttonOrientation=DGG.HORIZONTAL,
            valueEntry_text_align=TextNode.ACenter,
            borderWidth=(.1,.1),
            incButtonCallback=self.__changedYear,
            decButtonCallback=self.__changedYear,
            command=self.__changedYear)
        self.yearPicker.resetFrameSize()
        self.yearPicker.setPos(
            DGH.getRealLeft(self) + DGH.getRealWidth(self.yearPicker)/2,
            0,
            DGH.getRealTop(self) - DGH.getRealBottom(self.yearPicker))

        self.monthPicker = self.createcomponent(
            'monthPicker', (), None,
            DirectOptionMenu, (self,),
            items=calendar.month_name[1:],
            scale=0.05,
            command=self.setMonth,
            relief=DGG.FLAT)
        self.monthPicker.resetFrameSize()

        self.monthPicker.setPos(
            DGH.getRealRight(self) - DGH.getRealWidth(self.monthPicker),
            0,
            DGH.getRealTop(self) - DGH.getRealBottom(self.monthPicker) / 2)


        # set the current date if none is given at initialization
        self['year'] = now.year if self['year'] is None else self['year']
        self['month'] = now.month if self['month'] is None else self['month']
        self['day'] = now.day if self['day'] is None else self['day']

        self.yearPicker.setValue(self['year'])
        self.monthPicker.set(self['month']-1)

        self.refreshPicker()

    def createDateButton(self, day, enabled=True):
        return self.createcomponent(
            'day{}'.format(day), (), None,
            DirectButton, (self,),
            text=str(day),
            text_scale=0.05,
            relief=DGG.FLAT,
            borderWidth=(0.01, 0.01),
            state=DGG.NORMAL if enabled else DGG.DISABLED,
            frameColor=self['normalDayFrameColor'],
            frameSize=(-0.05,0.05,-0.035,0.0625),
            command=self.setDay,
            extraArgs=[day])

    def createLabel(self, txt):
        return self.createcomponent(
            'weekNumber', (), None,
            DirectLabel, (self,),
            text=txt,
            text_scale=0.05,
            frameColor=(0,0,0,0),
            frameSize=(-0.05,0.05,-0.035,0.0625)
        )

    def setDay(self, day):
        self['day'] = day
        self.refreshPicker()

    def getDay(self):
        return self['day']

    def __changedYear(self, year=None):
        year = int(self.yearPicker.get()) if year is None else int(year)
        if year > 9999: year = 9999
        if year < 1: year = 1
        self.setYear(year)

    def setMonth(self, month):
        if type(month) == str:
            self['month'] = calendar.month_name[:].index(month)
            if self.monthPicker.get() != self['month']-1:
                self.monthPicker.set(self['month']-1, fCommand=False)
        else:
            self['month'] = month
            if self.monthPicker.get() != self['month']-1:
                self.monthPicker.set(self['month']-1, fCommand=False)
        self.refreshPicker

    def getMonth(self):
        return self['month']

    def setYear(self, year):
        self['year'] = year
        self.refreshPicker()

    def getYear(self):
        return self['year']

    def getDate(self):
        return datetime.datetime(self['year'], self['month'], self['day'])

    def get(self):
        return self.getDate()

    def refreshPicker(self):
        # sanity check so we don't get here to early
        if self['year'] is None or self['month'] is None or self['day'] is None:
            return

        datesPrev = None
        if calendar.monthrange(self['year'], self['month'])[0] == 0:
            # get the previous dates for months that start with monday as first weekday and need one week prepended
            year = self['year'] if self['month'] > 1 else self['year']-1 if self['year'] > 0 else 1
            month = self['month']-1 if self['month'] > 1 else 12
            datesPrev = self.cal.monthdatescalendar(year,month)

        dates = self.cal.monthdatescalendar(self['year'],self['month'])

        datesNext = None
        if datesPrev is None and len(dates) < 7:
            # get the next dates for months that do not cover 6 lines of the calendar
            year = self['year'] if self['month'] < 12 else self['year']+1 if self['year'] < 9999 else 9999
            month = self['month']+1 if self['month'] < 12 else 1
            datesNext = self.cal.monthdatescalendar(year,month)


        def updateInfo(row, column, date):
            # update button
            btn = self.dateButtons[row][column]
            btn["text"] = str(date.day)
            btn["extraArgs"] = [date.day]
            btn["state"] = DGG.NORMAL if date.month == self['month'] else DGG.DISABLED
            now = datetime.datetime.now()
            isToday = now.day == date.day and now.month == date.month and now.year == date.year
            if isToday:
                # the current day
                btn["frameColor"] = self['todayFrameColor']
            if self['day'] == date.day:
                # the selected one
                btn["frameColor"] = self['activeDayFrameColor']
            elif not isToday:
                btn["frameColor"] = self['normalDayFrameColor']

            # update week numbers
            if column == 0:
                weeknumber = datetime.date(date.year, date.month, date.day).isocalendar()[1]
                self.weekNumbers[row]["text"] = str(weeknumber)

        for row in range(1, 7):
            r = row - 1
            column = 0
            if datesPrev and r == 0:
                for date in datesPrev[-1]:
                    updateInfo(r, column, date)
                    column += 1

            elif len(dates) > r - (1 if datesPrev else 0):
                hadPrev = 1 if datesPrev else 0
                for date in dates[r - hadPrev]:
                    updateInfo(r, column, date)
                    column += 1

            elif datesNext:
                idx = 1
                if dates[-1][-1].month == self['month']:
                    idx = 0

                for date in datesNext[idx]:
                    updateInfo(r, column, date)
                    column += 1

