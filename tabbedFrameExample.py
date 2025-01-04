from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectFrame import DirectFrame
from DirectGuiExtension.DirectTabbedFrame import DirectTabbedFrame

ShowBase()

width = base.get_size()[0]
height = base.get_size()[1]

dtf = DirectTabbedFrame(
    base.pixel2d,
    frameSize = (0, width, -height, 0),
    tabHeight=24)

def onCloseFunc(tab):
    print(f"closed {tab}")

fillSize = (0, width, -height, -dtf["tabHeight"])

tab1frame = DirectFrame(dtf, frameSize=fillSize, frameColor=(1,0,0,1))
tab2frame = DirectFrame(dtf, frameSize=fillSize, frameColor=(0,1,0,1))
tab3frame = DirectFrame(dtf, frameSize=fillSize, frameColor=(0,0,1,1))
tab4frame = DirectFrame(dtf, frameSize=fillSize, frameColor=(1,0,1,1))
dtf.add_tab("Tab 1", tab1frame, onCloseFunc)
dtf.add_tab("Tab 2", tab2frame, None)
dtf.add_tab("Tab 3", tab3frame, None)
dtf.add_tab("Tab 4", tab4frame, onCloseFunc)

base.run()
