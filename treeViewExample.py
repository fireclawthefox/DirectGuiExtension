from direct.showbase.ShowBase import ShowBase
from DirectGuiExtension.DirectTreeView import DirectTreeView

ShowBase()

DirectTreeView(
    frameSize=[-0.5,0.5, -0.5,0.5],
    autoUpdateFrameSize=False,
    tree={
        "A":{"1":None,"2":None},
        "B":"C"
    })

base.run()
