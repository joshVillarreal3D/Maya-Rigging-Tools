import maya.cmds as mc
import maya.OpenMayaUI as omui
import maya.mel as mel
from maya.OpenMaya import MVector
from PySide2.QtWidgets import QGridLayout, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSlider
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance

# commandPort -n "localhost:7001" -stp "mel";

class TrimSheetUVBuilderWidget(QWidget):
    def __init__(self):
        mayaMainWindow = TrimSheetUVBuilderWidget.GetMayaMainWindow()

        for existing in mayaMainWindow.findChildren(QWidget, TrimSheetUVBuilderWidget.GetWindowUniqueId()):
            existing.deleteLater()

        super().__init__(parent=mayaMainWindow)
        self.setWindowTitle("Trimsheet UV builder")
        self.setWindowFlags(Qt.Window)
        self.setObjectName(TrimSheetUVBuilderWidget.GetWindowUniqueId())

        self.shell = []

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.CreateInitializationSection()
        self.CreateManipulationSection()

    def FillShellToU1V1(self):
        width, height = self.GetShellSize()
        su = 1 / width
        sv = 1 / height
        self.ScaleShell(su, sv)
        self.MoveToOrigin()

    def GetShellSize(self):
        min, max = self.GetShellBound()
        height = max[1] - min[1]
        width = max[0] - min[0]

        return width, height

    def ScaleShell(self, u, v):
        mc.polyEditUV(self.shell, su = u, sv = v, r=True)

    def MoveShell(self, u, v):
        width, height = self.GetShellSize()
        uAmt = u * width
        vAmt = v * height
        mc.polyEditUV(self.shell, u = uAmt, v = vAmt)

    def CreateManipulationSection(self):
        sectionLayout = QVBoxLayout()
        self.masterLayout.addLayout(sectionLayout)
        turnBtn = QPushButton("Turn")
        turnBtn.clicked.connect(self.Turn)
        sectionLayout.addWidget(turnBtn)

        moveToOriginBtn = QPushButton("Move to Origin")
        moveToOriginBtn.clicked.connect(self.MoveToOrigin)
        sectionLayout.addWidget(moveToOriginBtn)

        fillU1V1Btn = QPushButton("Fill UV")
        fillU1V1Btn.clicked.connect(self.FillShellToU1V1)
        sectionLayout.addWidget(fillU1V1Btn)

        halfUBtn = QPushButton("Half U")
        halfUBtn.clicked.connect(lambda : self.ScaleShell(0.5, 1))
        sectionLayout.addWidget(halfUBtn)

        halfVBtn = QPushButton("Half V")
        halfVBtn.clicked.connect(lambda : self.ScaleShell(1, 0.5))
        sectionLayout.addWidget(halfVBtn)

        doubleUBtn = QPushButton("double U")
        doubleUBtn.clicked.connect(lambda : self.ScaleShell(2, 1))
        sectionLayout.addWidget(doubleUBtn)

        doubleVBtn = QPushButton("double V")
        doubleVBtn.clicked.connect(lambda : self.ScaleShell(1, 2))
        sectionLayout.addWidget(doubleVBtn)

        moveSection = QGridLayout()
        sectionLayout.addLayout(moveSection)

        moveUpBtn = QPushButton("^")        
        moveUpBtn.clicked.connect(lambda : self.MoveShell(0, 1))
        moveSection.addWidget(moveUpBtn, 0, 1)

        moveDownBtn = QPushButton("v")        
        moveDownBtn.clicked.connect(lambda : self.MoveShell(0, -1))
        moveSection.addWidget(moveDownBtn, 2, 1)

        moveLeftBtn = QPushButton("<")        
        moveLeftBtn.clicked.connect(lambda : self.MoveShell(-1, 0))
        moveSection.addWidget(moveLeftBtn, 1, 0)

        moveRightBtn = QPushButton(">")        
        moveRightBtn.clicked.connect(lambda : self.MoveShell(1, 0))
        moveSection.addWidget(moveRightBtn, 1, 2)


    def GetShellBound(self):
        uvs = mc.polyListComponentConversion(self.shell, toUV=True)
        uvs = mc.ls(uvs, fl=True)

        firstUVCoord = mc.polyEditUV(uvs[0], q=True)
        minU = firstUVCoord[0] 
        maxU = firstUVCoord[0]
        minV = firstUVCoord[1]
        maxV = firstUVCoord[1]

        for uv in uvs:
            uvCoord = mc.polyEditUV(uv, q=True)
            if uvCoord[0] < minU:
                minU = uvCoord[0]

            if uvCoord[0] > maxU:
                maxU = uvCoord[0]

            if uvCoord[1] < minV:
                minV = uvCoord[1]

            if uvCoord[1] > maxV:
                maxV = uvCoord[1]

        return [minU, minV], [maxU, maxV] 

    def MoveToOrigin(self):
        min, max = self.GetShellBound()
        mc.polyEditUV(self.shell, u = -min[0], v = -min[1])


    def Turn(self):
        mc.select(self.shell, r=True)
        mel.eval("polyRotateUVs 90 1")

    def CreateInitializationSection(self):
        sectionLayout = QHBoxLayout()
        self.masterLayout.addLayout(sectionLayout)

        selectShellBtn = QPushButton("Select Shell")
        selectShellBtn.clicked.connect(self.SelectShell)
        sectionLayout.addWidget(selectShellBtn)

        unfoldBtn = QPushButton("Unfold")
        unfoldBtn.clicked.connect(self.Unfold)
        sectionLayout.addWidget(unfoldBtn)

        cutAndUnfoldBtn = QPushButton("Cut and Unfold")
        cutAndUnfoldBtn.clicked.connect(self.CutAndUnfold)
        sectionLayout.addWidget(cutAndUnfoldBtn)

        unitizeBtn = QPushButton("Unitize")
        unitizeBtn.clicked.connect(self.Unitize)
        sectionLayout.addWidget(unitizeBtn)

    def Unitize(self):
        edges = mc.polyListComponentConversion(self.shell, toEdge=True)
        edges = mc.ls(edges, fl=True)

        sewedEdges = []
        for edge in edges:
            vertices = mc.polyListComponentConversion(edge, toVertex=True)
            vertices = mc.ls(vertices, fl=True)

            uvs = mc.polyListComponentConversion(edge, toUV = True)
            uvs = mc.ls(uvs, fl=True)

            if len(vertices) == len(uvs):
                sewedEdges.append(edge)

        mc.polyForceUV(self.shell, unitize=True) 
        mc.polyMapSewMove(sewedEdges)
        mc.u3dLayout(self.shell)


    def CutAndUnfold(self):
        edgesToCut = mc.ls(sl=True, fl=True)
        mc.polyProjection(self.shell, type="Planar", md="c")
        mc.polyMapCut(edgesToCut)
        mc.u3dUnfold(self.shell)
        mc.select(self.shell, r=True)
        mel.eval("texOrientShells")
        mc.u3dLayout(self.shell)


    def Unfold(self):
        mc.polyProjection(self.shell, type="Planar", md="c")
        mc.u3dUnfold(self.shell)
        mc.select(self.shell, r=True)
        mel.eval("texOrientShells")
        mc.u3dLayout(self.shell)

    def SelectShell(self):
        self.shell = mc.ls(sl=True)

    @staticmethod
    def GetMayaMainWindow():
        mayaMainWindow = omui.MQtUtil.mainWindow()
        return wrapInstance(int(mayaMainWindow), QMainWindow)

    @staticmethod
    def GetWindowUniqueId():
        return "aa581b1d171b358273ae811b261d0405"

def Run():
    TrimSheetUVBuilderWidget().show()