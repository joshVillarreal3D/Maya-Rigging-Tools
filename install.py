import os
import shutil
import maya.cmds as mc


def Run():
    projDir = os.path.dirname(os.path.abspath(__file__))
    mayaScriptPath = os.path.join (mc.internalVar(uad=True), "scripts")
    pluginName = os.path.split(projDir)[-1]

    pluginDestPath = os.path.join (mayaScriptPath, pluginName)

    if os.path.exists(pluginDestPath):
        shutil.rmtree(pluginDestPath)

    os.makedirs(pluginDestPath, exist_ok=True)

    srcDirName = "src"
    assetsDirname = "assets"

    shutil.copytree(os.path.join(projDir, srcDirName), os.path.join(pluginDestPath, srcDirName))
    shutil.copytree(os.path.join(projDir, assetsDirname), os.path.join(pluginDestPath, assetsDirname))

    def CreateShelfBtnForScript(scriptName):
        currentShelf = mc.tabLayout("ShelfLayout",q=True, selectTab=True)
        mc.setParent(currentShelf)
        iconImage = os.path.join(pluginDestPath, assetsDirname, scriptName +".png")
        mc.shelfButton(c=f"from {pluginName}.src import {scriptName}; {scriptName}.Run()", image = iconImage)


    CreateShelfBtnForScript("limb_rigging_tool")
    CreateShelfBtnForScript("TrimSheetUVBuilder")