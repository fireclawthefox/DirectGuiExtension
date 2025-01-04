from direct.showbase.ShowBase import ShowBase
from DirectGuiExtension.DirectTreeView import DirectTreeView, DirectTreeEntry

ShowBase()


DirectTreeView(
    frameSize=[-0.5,0.5, -0.5,0.5],
    autoUpdateFrameSize=False,
    tree={
        "A":{DirectTreeEntry("1"):{"X":"0"},"2":None},
        "B":"C",
        "D":{DirectTreeEntry("1"):{"Y":{"Z":"0"}}}
    })

base.run()
