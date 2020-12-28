# DirectGuiExtension
A set of extensions for the DirectGUI system of the Panda3D engine

## Features
Extends the DirectGUI system with the following features

Simple layout system
- DirectAutoSizer
- DirectBoxSizer
- DirectGridSizer

Widgets
- DirectDatePicker
- DirectDiagram
- DirectMenuItem
- DirectSpinBox
- DirectTooltip

Window system
- DirectScrolledWindowFrame

Helper Class
- DirectGuiHelper

## Install
Install the DirectGuiExtension via pip

```bash
pip install DirectGuiExtension
```

## How to use


### Layout System
#### DirectAutoSizer

The auto sizer will enlarge the frameSize of a widget to the size (frameSize or
bounds) of the given parent item. This can currently be either a gui
widget or NodePath.

Possible options are
<b>extendHorizontal</b> : Boolean
Determines if the sizer should extend on the horizontal or keep the frameSize in
this direction.

<b>extendVertical</b> : Boolean
Determines if the sizer should extend on the vertical or keep the frameSize in
this direction.

<b>minSize</b> : Tuple of 4 or LVecBase4f
The minimum size the sizer should be able to scale to.

<b>maxSize</b> : None, Tuple of 4 or LVecBase4f
The maximum size the sizer should be able to scale to. If None, the sizer can
grow indefinitely.

<b>updateOnWindowResize</b> : Boolean
If set to True, the sizer will be resized when the window is resized. This
should be enabled if the sizer is parented to None or the default gui parent to
keep it at the same size of the window even if the aspect ratio changes.

<b>childUpdateSizeFunc</b> : Function pointer
A function that will be called whenever the sizers' size gets changed. This
usually will be a function of the child element to refresh it accordingly. Some
of the widgets provided by this extension, like the DirectBoxSizer, should pass
their refresh function to update correctly. E.g.:

```python3
DirectAutoSizer(child=myBoxSizer, childUpdateSizeFunc=myBoxSizer.refresh)
```


#### DirectBoxSizer

The box sizer places all added items next to each other and aligns them.
It will just stack the items next to each other and won't limit their position
nor size, so it's up to you to resize the items, clip them by packing the sizer
in another container like a scrolled frame or similar.

<b>Options</b>

<b>items</b> : List of DirectItemContainer
This list contains all items that are added to the container. If you plan to add
items by this parameter, you should also reparent them to the box sizer.
The list will also be updated and elements reparented if they are passed by the
addItem command.

<b>orientation</b> : Any of DirectGuiGlobals.HORIZONTAL, VERTICAL, VERTICAL_INVERTED or HORIZONTAL_INVERTED
Note: HORIZONTAL_INVERTED is not given in the default DirectGuiGlobals but can
be defined as DirectGuiGlobals.HORIZONTAL_INVERTED = 'horizontal_inverted'

The orientation tells in which direction the items will be placed where
horizontal and vertical will go from left to right and top to bottom
respectively and the inverted ones will go from right to left and bottom to top.

<b>itemMargin</b> : Tuple of 4 or LVecBase4f
The margine controls the space between the items inside the box sizer.

<b>itemAlign</b> : Any of  DirectBoxSizer.A_Center, A_Left, A_Right, A_Middle, A_Top or A_Bottom
Center, Left and Right are used for Horizontal and Middle, Top and Bottom for
Vertical aligning of the given items. A Vertical and a horizontal alignment can
be combined by passing them with a bitwise or '|' like DirectBoxSizer.A_Left|DirectBoxSizer.A_Top

<b>autoUpdateFrameSize</b> : Boolean
If set to True, the frame size of the box sizer will be updated to the maximum
extend of all the items it contains. If set to False, the sizer will keep the
frameSize it was initially set to.

Note: If you plan to pack this element into a DirectAutoSizer, you should set
this to False.

<b>Functions</b>

addItem(widget)
Add another widget to the box sizer

removeItem(widget)
Removes the given widget from the box sizer. Returns 1 if the item was successfully
removed, 0 otherwise.


#### DirectGridSizer

Using the grid sizer, you can place multiple elements in a grid layout. Means
all elements are placed at a specific position within the grid and the rows and
columns will scale up to the largest element that they contain.

<b>Options</b>

<b>items</b> : List of DirectItemContainer
This list contains all items that are added to the container. If you plan to add
items by this parameter, you should also reparent them to the box sizer.
The list will also be updated and elements reparented if they are passed by the
addItem command.

<b>itemMargin</b> : Tuple of 4 or LVecBase4f
The margine controls the space between the items inside the grid sizer.

<b>numRows</b> : integer
The number of rows that are created for the grid

<b>numColumns</b> : integer
The number of columns that are created for the grid

<b>autoUpdateFrameSize</b> : Boolean
If set to True, the frame size of the grid sizer will be updated to the maximum
extend of all the items it contains. If set to False, the sizer will keep the
frameSize it was initially set to.

Note: If you plan to pack this element into a DirectAutoSizer, you should set
this to False.


<b>boxAlign</b> : any of TextNode.ALeft, ARight, ACenter


<b>Functions</b>

addItem(widget)
Add another widget to the box sizer

removeItem(widget)
Removes the given widget from the box sizer. Returns 1 if the item was successfully
removed, 0 otherwise.


### Widgets
#### DirectDatePicker
Simple date picker showing a month in a clickable grid layout.

<b>Options</b>
<b>year</b> : integer
The to be displayed year

<b>month</b> : integer
The to be displayed Month

<b>day</b> : integer
The to be selected day

<b>normalDayFrameColor</b> : Four-state color value
Color values for a normal, not-selected, not-current day

<b>activeDayFrameColor</b> : Four-state color value
Color values for the selected day

<b>todayFrameColor</b> : Four-state color value
Color values for the current (as of set in the system) day


<b>Functions</b>
<b>getDay
getMonth
getYear</b>
Return the respective selected day, month or year from the calendar

<b>setDay
setMonth
setYear</b>
Sets the currently selected day, month or year respectively

<b>getDate</b>
Returns the selcted date as a datetime object

<b>get</b>
returns the same as getDate


#### DirectDiagram
line diagram widget to show a range of values.

<b>data</b> : list
<b>numPosSteps</b> : number
<b>numPosStepsStep</b> : number
<b>numNegSteps</b> : number
<b>numNegStepsStep</b> : number
<b>numtextScale</b> : float
<b>showDataNumbers</b> : Boolean
<b>dataNumtextScale</b> : float
<b>stepAccuracy</b> : number
<b>stepFormat</b> : formater (e.g. float, int)
<b>numberAreaWidth</b> : float

#### DirectMenuItem
Menu widget dedicated for typical application menus with clickable entries and
sub-menu entries.

DirectMenuItemEntry

DirectMenuItemSubMenu

#### DirectSpinBox
Number entry with buttons to raise and lower the value. This widget also
supports changing the value by entering a text directly or scrolling with the
mousewheel.

#### DirectTooltip
Simple text frame that floats next to the mouse and stays within the screen.


### Window system
#### DirectScrolledWindowFrame
Movable frame with header bar to drag it around and close button. Other than
that it behaves like a normal DirectFrame.

### Helper Class
#### DirectGuiHelper
Some functions to get more accurate positions and sizes of DirectGui widgets
