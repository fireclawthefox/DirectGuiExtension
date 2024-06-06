"""This module contains the DirectTabbedFrame class.

It will create a frame with optionally closable tabs on top to switch between
multiple parented frames
"""

__all__ = ['DirectTabbedFrame']

from uuid import uuid4
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectRadioButton import DirectRadioButton
from . import DirectGuiHelper as DGH

class DirectTabbedFrame(DirectFrame):
    """
    A frame with tabs
    """
    DefDynGroups = ('tab', 'closeButton')

    notify = DirectNotifyGlobal.directNotify.newCategory('DirectTabbedFrame')

    def __init__(self, parent=None, **kw):
        optiondefs = (
            # Define type of DirectGuiWidget
            # The height of the area to drag the widget around
            ('tabHeight',                   0.1, self.__tabHeight),
            ('showCloseOnTabs',            True, self.__showCloseOnTabs),
            ('frameSize',           (-1,1,-1,1), None),
            ('selectedTabColor', (0.95, 0.95, 0.95, 1), self.__tabColor),
            ('unselectedTabColor', (.8, .8, .8, 1), self.__tabColor)
            )
        self.kw_args_copy = kw.copy()
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs, dynamicGroups=self.DefDynGroups)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        try:
            bw = kw["tab_borderWidth"]
        except KeyError:
            bw = (.1, .1)

        pos_x = self['frameSize'][0]
        pos_z = self['frameSize'][3]-self['tabHeight']/2 - bw[1]*self['tabHeight']
        self.prevTabButton = self.createcomponent(
            'prevTabButton', (), None,
            DirectButton,
            (self,),
            text='<',
            text_align=TextNode.ALeft,
            scale=self['tabHeight'],
            borderWidth=(0,0),
            pressEffect=False,
            pos=(pos_x, 0, pos_z),
            frameSize=(0,0.7,-0.5,0.5),
            text_pos=(0.1, -0.25),
            command=self.show_prev_tab,
        )

        pos_x = self['frameSize'][1]
        self.nextTabButton = self.createcomponent(
            'nextTabButton', (), None,
            DirectButton,
            (self,),
            text='>',
            text_align=TextNode.ARight,
            scale=self['tabHeight'],
            borderWidth=(0,0),
            pressEffect=False,
            pos=(pos_x, 0, pos_z),
            frameSize=(-0.7,0,-0.5,0.5),
            text_pos=(-0.1, -0.25),
            command=self.show_next_tab,
        )

        # Call option initialization functions
        self.initialiseoptions(DirectTabbedFrame)

        self.tab_index_from = 0
        self.tab_index_to = 0

        self.tab_list = []
        self._tab_number = 0
        self.selected_content = [None]
        self.current_content = None
        self.current_tab = None
        self.start_idx = 0

    def __tabHeight(self):
        if not hasattr(self, "tab_list"):  # We are here too early
            return

        try:
            bw = self["tab_borderWidth"]
        except KeyError:
            bw = (.1, .1)

        pos_x = self['frameSize'][0]
        pos_z = self['frameSize'][3] - self['tabHeight'] / 2 - bw[1]*self['tabHeight']
        self.prevTabButton.setScale(self["tabHeight"])
        self.prevTabButton.setPos(pos_x, 0, pos_z)

        pos_x = self['frameSize'][1]
        self.nextTabButton.setScale(self["tabHeight"])
        self.nextTabButton.setPos(pos_x, 0, pos_z)

        for tab in self.tab_list:
            tab.setScale(self["tabHeight"])

        self.reposition_tabs()

    def __tabColor(self):
        if not hasattr(self, "tab_list"):  # We are here too early
            return

        for other_tab in self.tab_list:
            other_tab['frameColor'] = self['unselectedTabColor']
            other_tab.closeButton['frameColor'] = self['unselectedTabColor']

        if self.current_tab is not None:
            self.current_tab['frameColor'] = self['selectedTabColor']
            self.current_tab.closeButton['frameColor'] = self['selectedTabColor']

    def __showCloseOnTabs(self):
        if not hasattr(self, "tab_list"):  # We are here too early
            return

        if self["showCloseOnTabs"]:
            for tab in self.tab_list:
                tab.closeButton.show()
        else:
            for tab in self.tab_list:
                tab.closeButton.hide()

    def show_prev_tab(self):
        if self.start_idx > 0:
            self.start_idx -= 1
            self.reposition_tabs()

    def show_next_tab(self):
        if self.start_idx < len(self.tab_list) - 1:
            self.start_idx += 1
            self.reposition_tabs()

    def _add_tab(self, content, tab_text, close_func=None):  # method used by DirectGuiDesigner to add tabs
        self.add_tab(tab_text, content, close_func)

    def add_tab(self, tab_text, content, close_func=None):
        # Make sure to include any options set earlier
        itemKW = {}
        for i in self.kw_args_copy:
            if i.startswith("tab_"):
                itemKW[i.removeprefix("tab_")] = self.kw_args_copy[i]

        toRemove = ["text", "text_align", "scale", "boxPlacement", "frameColor", "command", "variable", "value"]
        for r in toRemove:
            if r in itemKW:
                del itemKW[r]

        # create the new tab
        tab = self.createcomponent(
            f'tab{self._tab_number}', (), 'tab',
            DirectRadioButton,
            (self,),
            text=tab_text,
            text_align=TextNode.ALeft,
            scale=self['tabHeight'],
            boxPlacement='right',
            frameColor=self['unselectedTabColor'],
            command=self.switch_tab,
            variable=self.selected_content,
            value=[0],
            **itemKW
        )
        tab['extraArgs'] = [tab]
        # hide the radio button indicator
        tab.indicator.hide()
        tab['value'] = [content]
        # hide the tabs content by default
        content.hide()

        # get some details for the close button
        tab_height = DGH.getRealHeight(tab)
        x_pos = tab.indicator.get_pos()
        # x_pos.z = (tab_height - tab['borderWidth'][1]) / 2  # causes issues in pixel2d mode

        # Make sure to include any options set earlier
        itemKW = {}
        for i in self.kw_args_copy:
            if i.startswith("closeButton_"):
                itemKW[i.removeprefix("closeButton_")] = self.kw_args_copy[i]

        toRemove = ["text", "pos", "frameColor", "command", "extraArgs"]
        for r in toRemove:
            if r in itemKW:
                del itemKW[r]

        # create the close button
        tab.closeButton = self.createcomponent(
            f'closeButton{self._tab_number}', (), 'closeButton',
            DirectButton,
            (tab,),
            text='x',
            pos=x_pos,
            frameColor=self['unselectedTabColor'],
            command=self.close_tab,
            extraArgs=[tab, close_func],
            **itemKW
        )
        if not self['showCloseOnTabs']:
            tab.closeButton.hide()

        # add the tab to our list
        self.tab_list.append(tab)
        self._tab_number += 1

        # reposition all tabs
        self.reposition_tabs()

        # update all tabs with the new list
        for other_tab in self.tab_list:
            other_tab.setOthers(self.tab_list)

        return tab

    def switch_tab(self, tab):
        if self.current_content:
            self.current_content.hide()
        self.current_content = self.selected_content[0]
        if self.current_content:
            self.current_content.show()

        self.current_tab = tab

        # recolor tabs
        self.__tabColor()

    def close_tab(self, tab, close_func=None):
        # get the tabs index
        deleted_tab_idx = self.tab_list.index(tab)

        if close_func:
            close_func(tab)

        # store if it was the currently opened tab
        was_checked = tab['indicatorValue']

        # actually remove the tab from list and rendering
        del self.tab_list[deleted_tab_idx]
        if self.current_content == tab['value'][0]:
            self.current_content.hide()
            self.current_content = None
        tab.destroy()

        # update the other tabs with the new list
        for other_tab in self.tab_list:
            other_tab.setOthers(self.tab_list)

        # check tab selection
        if self.start_idx >= len(self.tab_list):
            # last tab from the list was deleted, move forward a bit
            self.start_idx = len(self.tab_list) - 1
            if self.start_idx < 0:
                # goodby very last tab
                self.start_idx = 0
            if len(self.tab_list) > 0 and was_checked:
                self.select_tab(self.tab_list[-1])
        elif len(self.tab_list) > deleted_tab_idx and was_checked:
            # select the new tab at that position, if we have any
            self.select_tab(self.tab_list[deleted_tab_idx])
        elif len(self.tab_list) > 0 and was_checked:
            # select the last available tab
            self.select_tab(self.tab_list[0])
            self.start_idx = 0

        # some sanity check
        if (self.start_idx >= len(self.tab_list) \
        and self.start_idx != 0) \
        or self.start_idx < 0:
            # something must have gone wrong, reset the start tab index
            self.start_idx = 0
            self.notify.info('Reset tab display start index')

        # reposition the existing tabs
        self.reposition_tabs()

    def reposition_tabs(self):
        # store some information we use in the repositioning
        next_x = DGH.getRealWidth(self.prevTabButton)
        show_tab = True
        next_button_width = DGH.getRealWidth(self.nextTabButton)

        # hide all tabs by default, they will be shown if they fit on the tab
        # list and are actually in the range of to be shown tabs
        for tab in self.tab_list:
            tab.hide()

        # move through all tabs, starting from the desired start index
        for tab in self.tab_list[self.start_idx:]:
            border_width_x = tab['borderWidth'][0]*tab.getScale().x
            border_width_z = tab['borderWidth'][1]*tab.getScale().z
            tab_bottom = DGH.getRealBottom(tab)
            tab_width = DGH.getRealWidth(tab)

            fs = self['frameSize']

            if fs[0] + next_x + tab_width > fs[1] - next_button_width:
                # this tab doesn't fit anymore, skip it and the next
                show_tab = False

            if not show_tab:
                continue

            # show this tab
            tab.show()
            # calculate the new position and place it there
            tab_pos = (
                fs[0]+next_x+border_width_x,
                0,
                fs[3]-tab_bottom-self['tabHeight']-2*border_width_z)
            tab.set_pos(tab_pos)

            # calculate the X start position shift for the next tab
            next_x += tab_width

    def select_tab(self, tab):
        tab.commandFunc(None)
