

# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 22:18:20 2021

@author: ashoff

Version updated by jperezag
"""


import sys
import os
from PyQt5.QtCore import Qt
#from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QRadioButton,QCheckBox
from PyQt5.QtWidgets import QRadioButton,QCheckBox
from PyQt5.QtWidgets import QDesktopWidget
#from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap


import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import math

import xraydb
## PEEK material added to database gm/cm^3
xraydb.add_material('PEEK', 'C19H14O3', 1.32, categories=['polymer'])
## glassy carbon material added to database
xraydb.add_material('Glossy Carbon', 'C', 1.5, categories=['polymer'])

## Kanthal A-1 Wire material added to database
#https://www.kanthal.com/en/products/material-datasheets/strip/kanthal-a-1/#:~:text=Kanthal%C2%AE%20A%2D1%20is,and%20very%20good%20oxidation%20resistance.
xraydb.add_material('Kanthal A-1', 'Cr1.83AlFe6.139', 7.1, categories=['polymer'])

## NiCr Wire material added to database
xraydb.add_material('Nichrome', 'CrNi3.544', 8.4, categories=['polymer'])

## NiCr Wire material added to database
xraydb.add_material('Carbon Fiber', 'C3HN', 1.184, categories=['polymer'])

#version number request find on Google drive
# this name must be the name of the zip folder available for download
CatMassVersion = "CatMass 2023 v3"

#development version
#CatMassVersion = " V3"

#development version format
#from src import functions as fct

### Global Variables ###
''' Data containers '''
saver = [None] *65
saverlabel = [None]*65
angleconstants = [None]*4

samplesaver = [None]*6
complexsaver = [None]*6
calculateresult_num = 1
displaysizesW = []
displaysizesH = []
#activedisplay = 0



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#########STAFF USE ONLY
#try:
    #crystal_BL93_220_90 = open('si2209093.txt').read().splitlines()
    #crystal_BL93_220_00 = open('si220093.txt').read().splitlines()
#crystal_BL93_220_00 = open('si220073.txt').read().splitlines()
    #crystal_BL43_111_90 = open('si1119043.txt').read().splitlines()
    #crystal_BL43_111_00 = open('si111043.txt').read().splitlines()
#except:
    #crystal_BL93_220_90 = []
    #crystal_BL93_220_00 = []

    #crystal_BL43_111_90 = []
    #crystal_BL43_111_00 = []
    #pass
##############

'''' Determine screen size for scaling '''
#Must be placed outside classes for EXE conversion
app = QApplication(sys.argv)
#screen = app.primaryScreen()
#rect = screen.availableGeometry()
for displayNr in range(QDesktopWidget().screenCount()):
    sizeObject = QDesktopWidget().availableGeometry(displayNr)
    #print("Display: " + str(displayNr) + " Screen size : " + str(sizeObject.height()) + "x" + str(sizeObject.width()))
    displaysizesW.append(sizeObject.width())
    displaysizesH.append(sizeObject.height())
#screenW = rect .width()
#screenH = rect.height()
screenW = float(min(displaysizesW))
screenH = float(displaysizesH[displaysizesW.index(min(displaysizesW))])
activedisplay = displaysizesW.index(min(displaysizesW))

SampleDilutionBlockWidth = round(300/1290*screenW)
XrayInputBlockWidth = round(230/1290*screenW)
#XrayInputBlockHight = round(570/1162*screenH)
XrayInputBlockHight = round(520/1162*screenH)
XraytextboxW = round(90/1290*screenW)
XraytextboxH = round(27/1162*screenH)
XraytextboxW2 = round(45/1290*screenW)
#XrayInputBlockHight2 = round((570/1162+30/1162)*screenH)
XrayInputBlockHight2 = round((550/1162+30/1162)*screenH)
ResultsBlockWidth = round(220/1290*screenW)
#ResultsBlockWidth = round(280/1290*screenW)
PropertiesBlockWidth = round((230+50+20+10)/1290*screenW)
fontsize = round(11/1162*screenH)





#######################
##     MAIN VIEW     ##
#######################






# Create a subclass of QMainWindow to setup the calculator's  main GUI
class XASCalcUI(QMainWindow):
    
        
    '''XASCalc's View (GUI).'''
    def __init__(self):
        '''View Initializer'''
        super().__init__()
        
        
        ''' Main Window Properties'''
        self.title = 'CatMass - XAS Sample Mass Calculator'
        self.left = 100
        self.top = 100
        self.width = 80#640
        self.height = 40#480
        
        #set icon
        #setup EXE version
        self.setWindowIcon(QIcon(resource_path('CoACCESSScale_v6')))
        
        #python version
        #self.setWindowIcon(QIcon(os.path.join(os.getcwd(),'src','images','CoACCESSScale_v6.ico')))
        
        # Set main window's properties
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        XASCalcUI.setFixedHeight(self, XrayInputBlockHight+40)
        XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+40)
        
        # Set the central widgetand general layout
        self.generalLayout = QHBoxLayout()
        
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self._createSampleDilutionBlock()
        self._createXrayInputBlock()
        self._createResultsBlock()
        'loading window then hiding it in If statement'
        self._createPropertiesBlock()
        
        # Create menu bar
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu('File')
        editMenu = self.mainMenu.addMenu('Edit')
        #viewMenu = self.mainMenu.addMenu('View')
        #searchMenu = mainMenu.addMenu('Search')
        #toolsMenu = mainMenu.addMenu('Tools')
        resizemenu = self.mainMenu.addMenu('Resize')
        helpMenu = self.mainMenu.addMenu('Help')
       
        
        
        
        #add a open text file that is a previes saved sample mass calculation
        OpenAction = QAction(QIcon('open24.png'),'Open File', self)
        fileMenu.addAction(OpenAction)
        OpenAction.triggered.connect(self.opencatfile)
        #OpenAction.triggered.connect(self.PreviousSave)
        
        # save changes to file that was openned
        SaveAction = QAction(QIcon('save24.png'),'Save', self)
        SaveAction.setShortcut('Ctrl + S')
        fileMenu.addAction(SaveAction)
        SaveAction.triggered.connect(self.SaveResults)
        SaveAction.triggered.connect(self.Savetoopenfile)
        
        # save your current calculation as a text file to open in future
        SaveasAction = QAction(QIcon('saveas24.png'),'Save As', self)
        #SaveasAction.setShortcut('Ctrl + S')
        fileMenu.addAction(SaveasAction)
        SaveasAction.triggered.connect(self.textlabels)
        SaveasAction.triggered.connect(self.SaveResults)
        SaveasAction.triggered.connect(self.SaveAs)
        
        # Add Exit Button to File Menu + Action
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(QApplication.closeAllWindows)
        exitButton.triggered.connect(QApplication.quit)
        fileMenu.addAction(exitButton)
        
        OpenAction = QAction(QIcon('Documentation24.png'),'Documentation', self)
        helpMenu.addAction(OpenAction)
        OpenAction.triggered.connect(self.openInfo)
        
        OpenAction = QAction(QIcon('ResetValues24.png'),'Reset Values', self)
        editMenu.addAction(OpenAction)
        OpenAction.triggered.connect(self.Resetall)
        
        
        for displayNr in range(QDesktopWidget().screenCount()):
            #sizeObject = QDesktopWidget().availableGeometry(displayNr)
            #displaysizesW.append(sizeObject.width())
            #displaysizesH.append(sizeObject.height())
            ResizeAction = QAction(QIcon('Resize24.png'),'Display '+str(displayNr+1), self)
            resizemenu.addAction(ResizeAction)
            ResizeAction.triggered.connect(lambda state, x=displayNr: self.ResizeGUI(x))
            
        
    
    def _createPropertiesBlock(self):
        global Properties_frame
        '''Define QFrame'''
        Properties_frame = QFrame()
        Properties_frame.setFrameShape(QFrame.StyledPanel)
        Properties_frame.setLineWidth(1)
       
        self.generalLayout.addWidget(Properties_frame)
        Properties_frame.setFixedWidth(PropertiesBlockWidth)
        
        
        """Define Layout"""
        PropertiesLayout = QGridLayout()
    
        Properties_frame.setLayout(PropertiesLayout)
        
        'loadingwindows and hiding it until user selects to view it'
        if self.b3.isChecked()== False:
            Properties_frame.hide()
            
        else:
            Properties_frame.show()
        
            '''Text Labels'''
            # Create Header Label
            self.label_P00 = QLabel('X-ray Transmission & Total Absorption Through Materials at E0 + 50 eV')
            self.label_P00.setAlignment(Qt.AlignLeft)
            self.label_P00.setStyleSheet("font-weight: bold; text-decoration: underline")
            PropertiesLayout.addWidget(self.label_P00, 0, 0,1,5)
            self.label_P00.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.label_P08 = QLabel('X-ray Absorption Through Ion Chamber Gases at E0')
            self.label_P08.setAlignment(Qt.AlignLeft)
            self.label_P08.setStyleSheet("font-weight: bold; text-decoration: underline")
            PropertiesLayout.addWidget(self.label_P08, 7, 0, 1, 4)
            self.label_P08.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Common gases Label
            self.label_P01 = QLabel('Gases:')
            self.label_P01.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.label_P01, 1, 0)
            self.label_P01.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
            self.label_P01.setFixedSize(XraytextboxW2,XraytextboxH)
            
            # Create common materials Label
            self.label_P02 = QLabel('Materials:')
            self.label_P02.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.label_P02, 2, 0)
            self.label_P02.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
            self.label_P02.setFixedSize(XraytextboxW2,XraytextboxH)
        
            # Creat "Dummy" label for shifting textboxes up label
            self.label_P04 = QLabel(self)
            PropertiesLayout.addWidget(self.label_P04, 15, 0,14,3)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create unit header" Label
            #self.label_P05 = QLabel('%')
            #self.label_P05.setAlignment(Qt.AlignCenter)
            #PropertiesLayout.addWidget(self.label_P05, 0, 4)
            #self.label_P05.setWordWrap(True)
            #self.generalLayout.addLayout(PropertiesLayout)
            
            # Create solvent materials Label
            self.label_P06 = QLabel('Solvents:')
            self.label_P06.setAlignment(Qt.AlignCenter)
            self.label_P06.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P06, 3, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            self.label_P06.setFixedSize(XraytextboxW2,XraytextboxH)
            
            # Create solvent materials Label
            self.label_P07 = QLabel('Metals:')
            self.label_P07.setAlignment(Qt.AlignCenter)
            self.label_P07.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P07, 4, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            self.label_P07.setFixedSize(XraytextboxW2,XraytextboxH)
            
            # Create pressure label for ion chambers
            self.label_P09 = QLabel('Total Pressure:')
            self.label_P09.setAlignment(Qt.AlignCenter)
            self.label_P09.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P09, 10, 0,2,1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create label for chabmer length
            self.label_P10 = QLabel("Ion Chamber Length [cm]:")
            self.label_P10.setAlignment(Qt.AlignCenter)
            self.label_P10.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P10, 12, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create label for chabmer length
            self.label_P11 = QLabel("% Beam Absorbed:")
            self.label_P11.setAlignment(Qt.AlignCenter)
            self.label_P11.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P11, 12, 3,2,1)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create label for note
            self.label_P12 = QLabel("Note: All calculated values in this panel are ⊥ to Beam.")
            self.label_P12.setAlignment(Qt.AlignCenter)
            self.label_P12.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P12, 16, 0,1,5)
            self.generalLayout.addLayout(PropertiesLayout)
        
            """Input Fields"""
        
            # Create Text Box for thickness of material
            self.textbox_P02 = QLineEdit()
            self.textbox_P02.setPlaceholderText('Thickness')
            self.textbox_P02.setFixedSize(XraytextboxW2,XraytextboxH)
            PropertiesLayout.addWidget(self.textbox_P02, 1, 2)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Text Box for thickness of material
            self.textbox_P03 = QLineEdit()
            self.textbox_P03.setPlaceholderText('Thickness')
            self.textbox_P03.setFixedSize(XraytextboxW2,XraytextboxH)
            PropertiesLayout.addWidget(self.textbox_P03, 2, 2)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Text Box for thickness of solvent
            self.textbox_P04 = QLineEdit()
            self.textbox_P04.setPlaceholderText('Thickness')
            self.textbox_P04.setFixedSize(XraytextboxW2,XraytextboxH)
            PropertiesLayout.addWidget(self.textbox_P04, 3, 2)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Text Box for thickness of metal
            self.textbox_P05 = QLineEdit()
            self.textbox_P05.setPlaceholderText('Thickness')
            self.textbox_P05.setFixedSize(XraytextboxW2,XraytextboxH)
            PropertiesLayout.addWidget(self.textbox_P05, 4, 2)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Combobox (dropdown) in main window for materials
            self.combo2 = QComboBox()
            for name, m in xraydb.get_materials(categories=['ceramic','polymer']).items():
                self.combo2.addItem(name)
            self.combo2.setFixedSize(XraytextboxW,XraytextboxH)
            PropertiesLayout.addWidget(self.combo2, 2, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U2 = QComboBox()
            self.combo_U2.addItem('in')
            self.combo_U2.addItem('mils')
            self.combo_U2.addItem('cm')
            self.combo_U2.addItem('mm')
            self.combo_U2.addItem('μm')
            self.combo_U2.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo_U2.setCurrentIndex(4)
            PropertiesLayout.addWidget(self.combo_U2, 2, 3)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Combobox (dropdown) in main window for materials
            self.combo3 = QComboBox()
            for name, m in xraydb.get_materials(categories='gas').items():
                self.combo3.addItem(name)
            self.combo3.setCurrentIndex(8)
            self.combo3.setFixedSize(XraytextboxW,XraytextboxH)
            PropertiesLayout.addWidget(self.combo3, 1, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U3 = QComboBox()
            self.combo_U3.addItem('in')
            self.combo_U3.addItem('mils')
            self.combo_U3.addItem('cm')
            self.combo_U3.addItem('mm')
            self.combo_U3.addItem('μm')
            self.combo_U3.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo_U3.setCurrentIndex(2)
            PropertiesLayout.addWidget(self.combo_U3, 1, 3)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Combobox (dropdown) in main window for materials
            self.combo4 = QComboBox()
            for name, m in xraydb.get_materials(categories='solvent').items():
                self.combo4.addItem(name)
            self.combo4.setCurrentIndex(0)
            self.combo4.setFixedSize(XraytextboxW,XraytextboxH)
            PropertiesLayout.addWidget(self.combo4, 3, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U4 = QComboBox()
            self.combo_U4.addItem('in')
            self.combo_U4.addItem('mils')
            self.combo_U4.addItem('cm')
            self.combo_U4.addItem('mm')
            self.combo_U4.addItem('μm')
            self.combo_U4.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo_U4.setCurrentIndex(2)
            PropertiesLayout.addWidget(self.combo_U4, 3, 3)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Combobox (dropdown) in main window for materials
            self.combo5 = QComboBox()
            for name, m in xraydb.get_materials(categories='metal').items():
                self.combo5.addItem(name)
            self.combo5.setCurrentIndex(2)
            self.combo5.setFixedSize(XraytextboxW,XraytextboxH)
            PropertiesLayout.addWidget(self.combo5, 4, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U5 = QComboBox()
            self.combo_U5.addItem('in')
            self.combo_U5.addItem('mils')
            self.combo_U5.addItem('cm')
            self.combo_U5.addItem('mm')
            self.combo_U5.addItem('μm')
            self.combo_U5.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo_U5.setCurrentIndex(1)
            PropertiesLayout.addWidget(self.combo_U5, 4, 3)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            self.textboxP04 = QLineEdit()
            self.textboxP04.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP04.setAlignment(Qt.AlignRight)
            self.textboxP04.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP04, 1, 4)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Editable Textbox for result %trans
            self.textboxP05 = QLineEdit()
            self.textboxP05.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP05.setAlignment(Qt.AlignRight)
            self.textboxP05.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP05, 2, 4)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            self.textboxP06 = QLineEdit()
            self.textboxP06.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP06.setAlignment(Qt.AlignRight)
            self.textboxP06.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP06, 3, 4)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            self.textboxP07 = QLineEdit()
            self.textboxP07.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP07.setAlignment(Qt.AlignRight)
            self.textboxP07.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP07, 4, 4)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            #self.textboxP13 = QLineEdit()
            #self.textboxP13.setFixedSize(XraytextboxW2,XraytextboxH)
            #self.textboxP13.setAlignment(Qt.AlignRight)
            #self.textboxP13.setReadOnly(True)
            #PropertiesLayout.addWidget(self.textboxP13, 4, 5)
            #self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Combobox for ionchamber gas 1
            self.combo6 = QComboBox()
            self.combo6.setEditable(True)
            line_edit = self.combo6.lineEdit()
            for name, m in xraydb.get_materials(categories='gas').items():
                self.combo6.addItem(name)
            self.combo6.setCurrentIndex(1)
            self.combo6.setFixedSize(XraytextboxW,XraytextboxH)
            PropertiesLayout.addWidget(self.combo6, 8, 0,1,2)
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setReadOnly(True)
            self.generalLayout.addLayout(PropertiesLayout)
            self.combo6.currentTextChanged.connect(self.CalBeamabs)
            
            # Create Combobox for ionchamber gas 2
            self.combo7 = QComboBox()
            self.combo7.setEditable(True)
            line_edit = self.combo7.lineEdit()
            for name, m in xraydb.get_materials(categories='gas').items():
                self.combo7.addItem(name)
                
            self.combo7.setCurrentIndex(2)
            self.combo7.setFixedSize(XraytextboxW,XraytextboxH)
            PropertiesLayout.addWidget(self.combo7, 8, 3,1,2,Qt.AlignRight)
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setReadOnly(True)
            self.generalLayout.addLayout(PropertiesLayout)
            self.combo7.currentTextChanged.connect(self.CalBeamabs)
            
            self.combo_C1 = QComboBox()
            self.combo_C1.addItem('10')
            self.combo_C1.addItem('15')
            self.combo_C1.addItem('30')
            self.combo_C1.addItem('45')
            self.combo_C1.addItem('60')
            self.combo_C1.addItem('Other')
            self.combo_C1.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo_C1.setCurrentIndex(1)
            PropertiesLayout.addWidget(self.combo_C1, 12, 2,Qt.AlignCenter)
            self.generalLayout.addLayout(PropertiesLayout)
            self.combo_C1.currentTextChanged.connect(self.CalBeamabs)
        
            """Buttons"""
            # Create Button to percent beam
            self.button_P00 = QPushButton('Percent Beam Transmitted')
            PropertiesLayout.addWidget(self.button_P00, 6, 0,1,2)
            self.generalLayout.addLayout(PropertiesLayout)
            self.button_P00.clicked.connect(self.Calculatetransbeam)
            self.button_P00.setFixedHeight(round(XraytextboxH/0.95))
            
            # Create Button to reset
            self.button_P01 = QPushButton('Reset')
            PropertiesLayout.addWidget(self.button_P01, 15, 0,1,5)
            self.generalLayout.addLayout(PropertiesLayout)
            self.button_P01.clicked.connect(self.clearxrayprop)
            self.button_P01.setFixedHeight(round(XraytextboxH/0.95))
            # Create Button to percent beam
            self.button_P02 = QPushButton('Beam Absorbed (µx)')
            PropertiesLayout.addWidget(self.button_P02, 6, 3,1,2)
            self.generalLayout.addLayout(PropertiesLayout)
            self.button_P02.clicked.connect(self.Calculateabsbeam_materials)
            self.button_P02.setFixedHeight(round(XraytextboxH/0.95))
            
    
            "Slider for ion chambers"
            self.slider = QSlider(Qt.Horizontal)
            PropertiesLayout.addWidget(self.slider, 9, 1,1,3)
            self.generalLayout.addLayout(PropertiesLayout)
            self.slider.setMinimum(-100)
            self.slider.setMaximum(0)
            self.slider.setValue(-50)
            self.slider.valueChanged.connect(self.valuechange)
            self.slider.valueChanged.connect(self.CalBeamabs)
            
            
            self.slider2 = QSlider(Qt.Horizontal)
            PropertiesLayout.addWidget(self.slider2, 10, 1,1,3)
            self.generalLayout.addLayout(PropertiesLayout)
            self.slider2.setMinimum(0)
            self.slider2.setMaximum(2300)
            self.slider2.setValue(760)
            self.slider2.setSingleStep(20)
            self.slider2.setPageStep(20)
            self.slider2.valueChanged.connect(self.valuechange2)
            self.slider2.valueChanged.connect(self.CalBeamabs)
            
            self.textboxP08 = QLineEdit()
            self.textboxP08.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP08.setAlignment(Qt.AlignRight)
            self.textboxP08.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP08, 9, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP08.setText('{0:0.0f}'.format(-self.slider.value())+' %')
            
            self.textboxP09 = QLineEdit()
            self.textboxP09.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP09.setAlignment(Qt.AlignLeft)
            self.textboxP09.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP09, 9, 4,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP09.setText('{0:0.0f}'.format(100+self.slider.value())+' %')
            
            self.textboxP10 = QLineEdit()
            self.textboxP10.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP10.setAlignment(Qt.AlignLeft)
            self.textboxP10.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP10, 10, 4,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP10.setText('{0:0.0f}'.format(round(self.slider2.value(),-1))+' torr')
            
            self.textboxP11 = QLineEdit()
            self.textboxP11.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP11.setAlignment(Qt.AlignCenter)
            self.textboxP11.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP11, 12, 4,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.textboxP12 = QLineEdit()
            self.textboxP12.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP12.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.textboxP12, 12, 0,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP12.setText('0')
            self.textboxP12.hide()
            self.textboxP12.textEdited.connect(self.CalBeamabs)

    # definfe slifer functions to change variables or labels
    
    
    def valuechange(self):
        #size = self.slider.value()
        self.textboxP08.setText('{0:0.0f}'.format(-self.slider.value())+' %')
        self.textboxP09.setText('{0:0.0f}'.format(100+self.slider.value())+' %')
    
    def valuechange2(self):
        #size = self.slider.value()
        self.textboxP10.setText('{0:0.0f}'.format(round(self.slider2.value(),-1))+' torr')
    
    def valuechange_deg(self):
        #AL = self.textbox3.text()
        #print(AL)
        #size = self.slider.value()
        
        self.b2.setText("Sample at "+'{0:0.0f}'.format(round(self.slider_deg.value(),0))+"°")
        
        
        if round(self.slider_deg.value(),0)==0:
            self.label5.setText('Projected Sample Area // to Beam [cm<sup>2</sup>]:')
        elif round(self.slider_deg.value(),0)==90:
            self.label5.setText('Sample Area ⊥ to Beam [cm<sup>2</sup>]:')
        else:
            #self.label5.setText('Projected Sample Area ' +'{0:0.0f}'.format(round(self.slider_deg.value(),0))+"°" + ' to Beam [cm<sup>2</sup>]:')
            self.label5.setText('Projected Sample Area to Beam [cm<sup>2</sup>]:')
            
            self.textbox3.setText('{0:0.2f}'.format(float(angleconstants[1])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
            if self.textbox6.text() =='' or self.textbox6.text()=='N/A':
                ''
            else:
                self.textbox6.setText('{0:0.4f}'.format(float(angleconstants[0])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
                if float(self.textbox6.text()) >1:
                    self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
                else:
                    self.textbox6.setStyleSheet("background-color:rgb(255,255,255)") 
        
            
            #print('{0:0.2f}'.format(float(angleconstants[1])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
        
    
    def _createSampleDilutionBlock(self):
        '''Define QFrame'''
        global Diluent_frame
        Diluent_frame = QFrame()
        Diluent_frame.setFrameShape(QFrame.StyledPanel)
        Diluent_frame.setLineWidth(1)
                
        self.generalLayout.addWidget(Diluent_frame)
        Diluent_frame.setFixedWidth(SampleDilutionBlockWidth)
        Diluent_frame.setMinimumHeight(XrayInputBlockHight)
        
        """Define Layout"""
        DilutionLayout = QGridLayout()
        
        Diluent_frame.setLayout(DilutionLayout)
        
        '''Text Labels'''
        # Create Header Label
        self.label_dil00 = QLabel('Sample and Dilution Definition')
        self.label_dil00.setAlignment(Qt.AlignLeft)
        self.label_dil00.setStyleSheet("font-weight: bold; text-decoration: underline")
        DilutionLayout.addWidget(self.label_dil00, 0, 0, 1, 3)
        self.label_dil00.setWordWrap(True)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create "Sample" Label
        self.label_dil01 = QLabel('Sample')
        self.label_dil01.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil01, 2, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create "Diluent" Label
        self.label_dil02 = QLabel('Diluent')
        self.label_dil02.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil02, 2, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create "Stoichiometry" Label
        self.label_dil03 = QLabel('Stoichiometry:')
        self.label_dil03.setAlignment(Qt.AlignRight)
        DilutionLayout.addWidget(self.label_dil03, 3, 0)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Creat "Dilution Ratio" label
        self.label_dil04 = QLabel('Mass Dilution Ratio:')
        self.label_dil04.setAlignment(Qt.AlignRight)
        DilutionLayout.addWidget(self.label_dil04, 4, 0)
        self.generalLayout.addLayout(DilutionLayout)        
        
        
        """Input Fields"""
        # Create Text Box for Sample Formula
        self.textbox_dil01 = QLineEdit()
        self.textbox_dil01.setPlaceholderText('Chemical Formula')
        self.textbox_dil01.setFixedSize(XraytextboxW,XraytextboxH)
        DilutionLayout.addWidget(self.textbox_dil01, 3, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Diluent Formula
        self.textbox_dil02 = QLineEdit()
        self.textbox_dil02.setPlaceholderText('Chemical Formula')
        self.textbox_dil02.setFixedSize(XraytextboxW,XraytextboxH)
        DilutionLayout.addWidget(self.textbox_dil02, 3, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Sample Dilution Fraction
        self.textbox_dil03 = QLineEdit()
        self.textbox_dil03.setPlaceholderText('#')
        self.textbox_dil03.setAlignment(Qt.AlignCenter)
        self.textbox_dil03.setFixedSize(XraytextboxW2,XraytextboxH)
        DilutionLayout.addWidget(self.textbox_dil03, 4, 1,Qt.AlignCenter)
        self.generalLayout.addLayout(DilutionLayout)
                
        # Create Text Box for Diluent Dilution Fraction
        self.textbox_dil04 = QLineEdit()
        self.textbox_dil04.setPlaceholderText('#')
        self.textbox_dil04.setAlignment(Qt.AlignCenter)
        self.textbox_dil04.setFixedSize(XraytextboxW2,XraytextboxH)
        DilutionLayout.addWidget(self.textbox_dil04, 4, 2,Qt.AlignCenter)
        self.generalLayout.addLayout(DilutionLayout)
       
        # Creat "Dummy" label fo Co-ACCESS label
        self.label_dil07 = QLabel(self)
        self.label_dil07.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil07, 9, 0,4,3)
        #self.label_dil07.setStyleSheet("background-color:rgb(0,0,0)")
        self.label_dil07.setFixedSize(XraytextboxW2,XraytextboxH*6) 
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for File path of openned file
        self.textbox_dil06 = QLineEdit()
        self.textbox_dil06.setPlaceholderText('File Path')
        self.textbox_dil06.setAlignment(Qt.AlignCenter)
        self.textbox_dil06.setReadOnly(True)
        DilutionLayout.addWidget(self.textbox_dil06, 6, 0, 1,3)
        self.generalLayout.addLayout(DilutionLayout)      
        
        # Create Text Box for Diagnostics
        self.textbox_dil05 = QLineEdit()
        self.textbox_dil05.setPlaceholderText('Diagnostics')
        self.textbox_dil05.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.textbox_dil05, 7, 0, 1,3)
        self.generalLayout.addLayout(DilutionLayout)
        
        self.label_dil05 = QLabel(self)
        #pixmap = QPixmap('co_access_logo_text.png')
        pixmap = QPixmap(resource_path('co_access_logo_text.png'))
        #pixmap = QPixmap(os.path.join(os.getcwd(),'src','images','co_access_logo_text.png'))
        self.label_dil05.setPixmap(pixmap)
        self.label_dil05.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil05, 8, 0,30,3)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Creat "Dummy" label fo Co-ACCESS label
        self.label_dil06 = QLabel(self)
        self.label_dil06.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil06, 30, 0,4,3)
        self.label_dil06.setFixedSize(XraytextboxW2,XraytextboxH*6) 
        self.generalLayout.addLayout(DilutionLayout)
        
        linkTemplate = '<a href={0}>{1}</a>'
        self.label_dil07 = QLabel(self)
        
        #development version
        #self.label_dil07.setText(linkTemplate.format('https://github.com/ahoffm02/catMass','There is a New Development Version of CatMass Available Online!'))
        
        self.label_dil07.setText(linkTemplate.format('https://drive.google.com/drive/folders/1cn_cJd070a3L08fOBYLkGOVSRvuPCsi7','There is a New Version of CatMass Available Online!'))
        self.label_dil07.setAlignment(Qt.AlignCenter)
        self.label_dil07.setWordWrap(True)
        self.label_dil07.setOpenExternalLinks(True)
        DilutionLayout.addWidget(self.label_dil07, 40, 0, 1,3)
        self.generalLayout.addLayout(DilutionLayout)
    
    
    
        
        import requests
        try:
            r = requests.get("https://drive.google.com/drive/folders/1cn_cJd070a3L08fOBYLkGOVSRvuPCsi7")
            versionx = r.text.find(CatMassVersion)
            #development version on Github
            #r = requests.get("https://github.com/ahoffm02/catMass/tree/main/catmass")
            #versionx = r.text.find(CatMassVersion)
            if versionx==-1:
                #QMessageBox.about(self, "CatMass", linkTemplate.format('https://drive.google.com/drive/folders/1cn_cJd070a3L08fOBYLkGOVSRvuPCsi7','New Version of CatMass Available!'))
                self.label_dil07.show()
            else:
                self.label_dil07.hide()
        except:
            pass
        
        # Creat label fo Newest version
        
        
        
    
        ''
        """Buttons"""
        # Create Button to Open Sample Builder
        self.button_dil00 = QPushButton('Sample Builder')
        DilutionLayout.addWidget(self.button_dil00, 1, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil00.clicked.connect(self.openSampleBuilder)
        self.button_dil00.setFixedSize(XraytextboxW,XraytextboxH)   
       
        
        # Create Button to Reset all Text Fields
        self.button_dil01 = QPushButton('Reset')
        DilutionLayout.addWidget(self.button_dil01, 5, 0)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil01.clicked.connect(self.clearDilutionInput)
        self.button_dil01.setFixedSize(XraytextboxW,XraytextboxH)
        
        # Create Button to Calculate Diluted Sample Chemical Formula 
        self.button_dil02 = QPushButton('Calculate Diluted Sample Chemical Formula')
        DilutionLayout.addWidget(self.button_dil02, 5, 1, 1, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil02.clicked.connect(self.calculateSampleComp)
        self.button_dil02.setFixedSize(round(XraytextboxW*2.1),XraytextboxH)
        
        
    def _createXrayInputBlock(self):
        '''Define QFrame'''
        global XrayInputFrame
        global activedisplay
        XrayInputFrame = QFrame()
        XrayInputFrame.setFrameShape(QFrame.StyledPanel)
        XrayInputFrame.setLineWidth(1)
                
        self.generalLayout.addWidget(XrayInputFrame)
        
        """Define Layout"""
        InputLayout = QGridLayout()
        XrayInputFrame.setLayout(InputLayout)
        XrayInputFrame.setFixedWidth(XrayInputBlockWidth)
        XrayInputFrame.setMinimumHeight(XrayInputBlockHight)
        #XrayInputFrame.setFixedHeight(XrayInputBlockHight)       
        """Text Labels"""
        #Create header
        self.label0 = QLabel('Edge Scan and Absorption Properties Definition')
        self.label0.setStyleSheet("font-weight: bold; text-decoration: underline")
        self.label0.setAlignment(Qt.AlignLeft)
        self.label0.setWordWrap(True)
        InputLayout.addWidget(self.label0, 0, 0, 1, 2)
        
        # Create Label for Sample Input
        self.label1 = QLabel('Diluted Sample Chemical Formula:')
        self.label1.setAlignment(Qt.AlignRight)
        self.label1.setWordWrap(True)
        InputLayout.addWidget(self.label1, 4, 0,2,1)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Label for Element of Interest
        self.label2 = QLabel('Element to be Scanned:')
        self.label2.setAlignment(Qt.AlignRight)
        self.label2.setWordWrap(True)
        InputLayout.addWidget(self.label2, 8, 0,1,1)
        self.generalLayout.addLayout(InputLayout)
        
        
        #Create Label for Element of Interest
        self.label3 = QLabel('Edge to be Scanned:')
        self.label3.setAlignment(Qt.AlignRight)
        self.label3.setWordWrap(True)
        InputLayout.addWidget(self.label3, 12, 0,1,1)
        self.generalLayout.addLayout(InputLayout)
        
        #Create Label for edge to be scanned
        self.label12 = QLabel('Energy to Calculate Sample Mass [eV]:')
        self.label12.setAlignment(Qt.AlignRight)
        self.label12.setWordWrap(True)
        InputLayout.addWidget(self.label12, 16, 0,2,1)
        self.generalLayout.addLayout(InputLayout)
        self.label12.hide()
        
        
        # Create Lable for Desired Absorption Length
        self.label4 = QLabel('Catalyst Sample Absorption at E0 + 50 eV:')
        self.label4.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label4, 56, 0,2,1)
        self.label4.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        self.label4.hide()
        
        # Create Lable for Desired Absorption Length
        self.label14 = QLabel('Catalyst Sample Absorption at E0 + 50 eV:')
        self.label14.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label14, 44, 0,2,1)
        self.label14.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        #self.label6 = QLabel('')
        #self.label6.setAlignment(Qt.AlignCenter)
        #InputLayout.addWidget(self.label6, 28, 0,2,1)
        #self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        self.label7 = QLabel('XAS Cells:')
        self.label7.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label7, 20, 0,1,2)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        #self.label8 = QLabel('')
        #self.label8.setAlignment(Qt.AlignCenter)
        #InputLayout.addWidget(self.label8, 36, 0,2,1)
        #self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for bed legnth
        self.label11 = QLabel('Bed length [1 cm]:')
        self.label11.setAlignment(Qt.AlignCenter)
        self.label11.setWordWrap(True)
        InputLayout.addWidget(self.label11, 28, 0,1,1)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Desired Area
        self.label5 = QLabel('Sample Area ⊥ to Beam [cm<sup>2</sup>]:')
        self.label5.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label5, 52, 0,2,1)
        #self.label5.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        self.label5.hide()
        
        # Create Lable for Desired Area
        self.label13 = QLabel('Sample Area ⊥ to Beam [cm<sup>2</sup>]:')
        self.label13.setAlignment(Qt.AlignCenter)
        self.label13.setWordWrap(True)
        InputLayout.addWidget(self.label13, 40, 0,1,1)
        #self.label5.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        
        
        # Create Lable for plot lower limit
        self.label17 = QLabel('Lower Limit of μ Average Plot:')
        self.label17.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label17, 64, 0,1,1)
        self.label17.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        self.label17.hide()
        
        # Create Lable for plot upper limit
        self.label18 = QLabel('Upper Limit of μ Average Plot:')
        self.label18.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label18, 68, 0,1,1)
        self.label18.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        self.label18.hide()
        
        # Create DUMMY Lable for plot spacing
        #self.label15 = QLabel('')
        #self.label15.setAlignment(Qt.AlignCenter)
        #InputLayout.addWidget(self.label15, 63, 0, 1, 2)
        #self.label10.setWordWrap(True)
        #self.generalLayout.addLayout(InputLayout)
        #self.label15.setFixedSize(round(XraytextboxW*2.21),round(XraytextboxH/1.5))
        
        # Create DUMMY Lable for plot cell area
        #self.label16 = QLabel('')
        #self.label16.setAlignment(Qt.AlignCenter)
        #InputLayout.addWidget(self.label16, 25, 0, 10, 2)
        #self.label10.setWordWrap(True)
        #self.generalLayout.addLayout(InputLayout)
        #self.label16.setFixedSize(round(XraytextboxW),round(XraytextboxH))
        
        """Input Fields"""
        
        # Create Editable Textbox for Sample Stoichiometry
        self.textbox1 = QLineEdit()
        self.textbox1.setPlaceholderText('Defined Left')
        self.textbox1.setStyleSheet("background-color:rgb(224,224,224)")
        self.textbox1.setReadOnly(True)
        self.textbox1.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox1, 4, 1,2,1)
        self.generalLayout.addLayout(InputLayout)

        # Create Editable Textbox for Element to be Scanned
        self.textbox2 = QLineEdit()
        self.textbox2.setPlaceholderText('Element Symbol')
        self.textbox2.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox2, 8, 1,1,1)
        self.generalLayout.addLayout(InputLayout)

        # Create Combobox (dropdown) in main window for Edge to Scan
        self.combo = QComboBox()
        #self.combo.setEditable(True)
        self.combo.addItem('K')
        self.combo.addItem('L1')
        self.combo.addItem('L2')
        self.combo.addItem('L3')
        self.combo.addItem('Other')
        #line_edit = self.combo.lineEdit()
        self.combo.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.combo, 12, 1,1,1)
        #line_edit.setAlignment(Qt.AlignCenter)
        #line_edit.setReadOnly(True)
        self.generalLayout.addLayout(InputLayout)
        self.combo.currentTextChanged.connect(self.on_combobox_changed)
        #self.combo.currentTextChanged.connect(self.mousePressEvent)
        try:
            self.combo.currentTextChanged.connect(self.ResizeGUI(activedisplay))
        except:
            pass
        
        self.textbox14 = QLineEdit()
        self.textbox14.setPlaceholderText('Energy')
        self.textbox14.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox14, 16, 1,2,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox14.hide()
        
        
        #checkbox to show results with cell at 45 degrees
        self.b2 = QCheckBox()
        InputLayout.addWidget(self.b2, 48, 0,1,1)
        #self.b1.setAlignment(Qt.AlignCenter)
        self.b2.setText("Sample at 45°")
        self.b2.toggled.connect(self.b1_function)
        self.b2.toggled.connect(self.setarea)
        self.b2.setStyleSheet('QCheckBox::indicator { width: 12px; height: 12px;};')
 
        
        # Create Editable Textbox for Desired Absorption Length
        self.textbox3 = QLineEdit()
        self.textbox3.setPlaceholderText('Target Absorption Length')
        self.textbox3.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox3, 56, 1,2,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox3.setText('2.6')
        self.textbox3.setReadOnly(True)
        self.textbox3.setEnabled(False)
        self.textbox3.hide()
        
        # Create Editable Textbox for Desired Absorption Length 90
        self.textbox15 = QLineEdit()
        self.textbox15.setPlaceholderText('Target Absorption Length')
        self.textbox15.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox15, 44, 1,2,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox15.setText('2.6')
        self.textbox15.textEdited.connect(self.setAL)
        
        # Radio button for Capillaries
        self.radioButton1 = QRadioButton(self)
        InputLayout.addWidget(self.radioButton1, 24, 0,1,1) #19
        self.radioButton2 = QRadioButton()
        InputLayout.addWidget(self.radioButton2, 32, 0,1,1)
        self.radioButton3 = QRadioButton()
        InputLayout.addWidget(self.radioButton3, 36, 0,1,1)
        self.radioButton1.setText("Capillary Diameter [mm]")
        self.radioButton2.setText("Pellet Diameter [mm]")
        self.radioButton3.setText("Other")
        self.radioButton1.toggled.connect(self.radioButton1_function) 
        self.radioButton2.toggled.connect(self.radioButton2_function) 
        self.radioButton3.toggled.connect(self.radioButton3_function)
        self.radioButton1.toggled.connect(self.setarea) 
        self.radioButton2.toggled.connect(self.setarea) 
        self.radioButton3.toggled.connect(self.setarea)
        
        
        self.radioButton1.setStyleSheet('QRadioButton::indicator { width: 11px; height: 11px;};')
        self.radioButton2.setStyleSheet('QRadioButton::indicator { width: 11px; height: 11px;};')
        self.radioButton3.setStyleSheet('QRadioButton::indicator { width: 11px; height: 11px;};')
        
        
        # Create Combobox (dropdown) in main window for capillary diameters to select
        self.combo_cap = QComboBox()
        self.combo_cap.addItem('1')
        self.combo_cap.addItem('2')
        self.combo_cap.addItem('3')
        self.combo_cap.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.combo_cap, 24, 1,1,1)
        self.combo_cap.setCurrentIndex(2)
        self.generalLayout.addLayout(InputLayout)
        self.combo_cap.setEditable(True)
        self.combo_cap.currentTextChanged.connect(self.setarea)
        self.combo_cap.setEnabled(False)
        
        # Create Combobox (dropdown) in main window for pellet diameters to select
        self.combo_pel = QComboBox()
        self.combo_pel.addItem('5')
        self.combo_pel.addItem('7')
        self.combo_pel.addItem('10')
        self.combo_pel.addItem('13')
        self.combo_pel.setCurrentIndex(1)
        self.combo_pel.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.combo_pel, 32, 1,1,1)
        self.generalLayout.addLayout(InputLayout)
        self.combo_pel.setEditable(True)
        self.combo_pel.currentTextChanged.connect(self.setarea)
        self.combo_pel.setEnabled(False)
    
        
        
        # Create Editable Textbox bed length
        self.textbox13 = QLineEdit()
        self.textbox13.setPlaceholderText('1')
        self.textbox13.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox13, 28, 1,1,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox13.setText('1')
        self.textbox13.textEdited.connect(self.setarea)
                   
        # Create Editable Textbox for Desired Area
        self.textbox4 = QLineEdit()
        self.textbox4.setPlaceholderText('Sample Area')
        self.textbox4.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox4, 52, 1,2,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox4.setEnabled(False)
        self.textbox4.hide()
        
        
        # Create Editable Textbox for Desired Area 90
        self.textbox16 = QLineEdit()
        self.textbox16.setPlaceholderText('Sample Area')
        self.textbox16.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox16, 40, 1,1,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox16.textEdited.connect(self.setarea)
        
        "Slider for 45 deg chambers"
        self.slider_deg = QSlider(Qt.Horizontal)
        InputLayout.addWidget(self.slider_deg, 48, 1,1,1)
        self.generalLayout.addLayout(InputLayout)
        self.slider_deg.setMinimum(0)
        self.slider_deg.setMaximum(90)
        self.slider_deg.setValue(45)
        self.slider_deg.setFixedSize(XraytextboxW,XraytextboxH)
        self.slider_deg.valueChanged.connect(self.valuechange_deg)
        self.slider_deg.valueChanged.connect(self.setarea)
        #self.slider_deg.valueChanged.connect(self.b1_function)
        self.slider_deg.hide()
        
        # Create Editable Textbox for Plot lower limit
        self.textbox11 = QLineEdit()
        self.textbox11.setPlaceholderText('-200')
        self.textbox11.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox11, 64, 1,1,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox11.setText('-200')
        self.textbox11.hide()
        
        # Create Editable Textbox for Plot upper limit
        self.textbox12 = QLineEdit()
        self.textbox12.setPlaceholderText('1000')
        self.textbox12.setFixedSize(XraytextboxW,XraytextboxH)
        InputLayout.addWidget(self.textbox12, 68, 1,1,1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox12.setText('1000')
        self.textbox12.hide()
        
        #checkbox to show plot
        self.b1 = QCheckBox()
        InputLayout.addWidget(self.b1, 60, 0,1,1)
        self.b1.setText("Show Plot")
        self.b1.setStyleSheet('QCheckBox::indicator { width: 12px; height: 12px;};')
        self.b1.toggled.connect(self.showlimits)
        
        #checkbox to show Xray transmission block
        #self.b3 = QCheckBox()
        #InputLayout.addWidget(self.b3, 56, 0,4,1)
        #self.b3.setText("X-ray transmission  \n through media")
        #self.b3.toggled.connect(self.b3_function)
        #self.b3.setStyleSheet('QCheckBox::indicator { width: 12px; height: 12px;};')
        
        
       
        # Create Editable Textbox for Diagnostics
        #self.textbox_Xray_05 = QLineEdit()
        #.textbox_Xray_05.setPlaceholderText('Diagnostics')
        #.textbox_Xray_05.setAlignment(Qt.AlignCenter)
        #InputLayout.addWidget(self.textbox_Xray_05, 63, 0,1,2,Qt.AlignCenter)
        #self.generalLayout.addLayout(InputLayout)
        #self.textbox_Xray_05.setFixedSize(round(XraytextboxW*2.2),round(XraytextboxH/1.5))
    
        '''Buttons'''
        #Create Reset Button to Clear X-ray Input Field
        self.button_Input01 = QPushButton('Reset')
        InputLayout.addWidget(self.button_Input01, 72, 0,1,2,Qt.AlignCenter)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input01.clicked.connect(self.clearDisplay)
        self.button_Input01.setFixedSize(XraytextboxW,XraytextboxH)
        self.button_Input01.setFixedSize(round(XraytextboxW*2.15),round(XraytextboxH*.9))
        
        #Create Button to Calcualte sample mass and step
        #self.button_Input02 = QPushButton('Calculate Sample Mass')
        #InputLayout.addWidget(self.button_Input02 ,61, 1,2,1)
        #self.generalLayout.addLayout(InputLayout)
        #self.button_Input02.clicked.connect(self.calculateResult)
        #self.button_Input02.setFixedSize(XraytextboxW,XraytextboxH)
        
        #starting values for radio button
        self.radioButton2.setChecked(True)
        self.setarea()
        
    def radioButton1_function(self):
        self.combo_cap.setEnabled(True)
        self.combo_pel.setEnabled(False)
        self.textbox13.setEnabled(True)
        #self.textbox4.setReadOnly(True)
        #self.textbox4.setEnabled(False)
        self.textbox16.setReadOnly(True)
        self.textbox16.setEnabled(False)
            
    def setarea(self):
        try:
            
            if self.b2.isChecked()== False:
                if self.radioButton1.isChecked() and self.textbox13.text()!= ''and self.textbox13.text()!= '.':
                    crossarea = float(self.combo_cap.currentText())*float(self.textbox13.text())/10
                    self.textbox16.setText(str('{0:0.2f}'.format(crossarea)))
                    self.textbox4.setText(str('{0:0.2f}'.format(crossarea)))
                if self.radioButton2.isChecked():
                    crossarea = (math.pi/4)*float(self.combo_pel.currentText())**2/100
                    self.textbox16.setText(str('{0:0.2f}'.format(crossarea)))
                    self.textbox4.setText(str('{0:0.2f}'.format(crossarea)))
                if self.radioButton3.isChecked():
                    #crossarea = float(self.textbox4.text())
                    crossarea = float(self.textbox16.text())
                    #self.textbox16.setText(str('{0:0.2f}'.format(crossarea)))
                    self.textbox4.setText(str('{0:0.2f}'.format(crossarea)))
            if self.b2.isChecked()== True:
                if self.radioButton1.isChecked() and self.textbox13.text()!= ''and self.textbox13.text()!= '.':
                    #crossarea = float(self.combo_cap.currentText())*float(self.textbox13.text())/10/math.sqrt(2)
                    self.textbox16.setText(str('{0:0.2f}'.format(float(self.combo_cap.currentText())*float(self.textbox13.text())/10)))
                    crossarea = float(self.combo_cap.currentText())*float(self.textbox13.text())/10*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
                    self.textbox4.setText(str('{0:0.2f}'.format(crossarea)))
                if self.radioButton2.isChecked():
                    self.textbox16.setText(str('{0:0.2f}'.format((math.pi/4)*float(self.combo_pel.currentText())**2/100)))
                    crossarea = (math.pi/4)*float(self.combo_pel.currentText())**2/100*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
                    self.textbox4.setText(str('{0:0.2f}'.format(crossarea)))
                if self.radioButton3.isChecked():
                    crossarea = float(self.textbox16.text())*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
                    #crossarea = float(self.textbox4.text())*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
                    self.textbox4.setText(str('{0:0.2f}'.format(crossarea)))
            #needed when XAS changes and needs to be new value but cannot be changed when sliding with current slider area
            if angleconstants[3]!= float(self.combo_cap.currentText())+float(self.combo_pel.currentText())+float(self.textbox13.text()):
                #area change for tansmission when xas cell changes 
                angleconstants[2] = '{0:0.2f}'.format(crossarea/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360))
                #redifine sum of xas cells to be new unchanged value until new change occurs
                angleconstants[3] = float(self.combo_cap.currentText())+float(self.combo_pel.currentText())+float(self.textbox13.text())
            #print("set area ")
            #print( angleconstants)
            
            
        except:
            pass
    
    
    def setAL(self): 
        try:
            #angleconstants[1] = float(self.textbox15.text())
            if self.b2.isChecked()== True:
                self.textbox3.setText('{0:0.2f}'.format(float(self.textbox15.text())/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
            else:
                self.textbox3.setText('{0:0.2f}'.format(float(self.textbox15.text())))
        except:
            pass
        


    def radioButton2_function(self):
        self.combo_cap.setEnabled(False)
        self.combo_pel.setEnabled(True)
        self.textbox13.setEnabled(False)
        #self.textbox4.setEnabled(False)
        self.textbox16.setEnabled(False)
        

    def radioButton3_function(self):
        self.combo_cap.setEnabled(False)
        self.combo_pel.setEnabled(False)
        self.textbox13.setEnabled(False)
        #self.textbox4.setEnabled(True)
        #self.textbox4.setReadOnly(False)
        self.textbox16.setEnabled(True)
        self.textbox16.setReadOnly(False)
    
    def showlimits(self):
        if self.b1.isChecked()== False:
            self.label17.hide()
            self.label18.hide()
            self.textbox11.hide()
            self.textbox12.hide()
        else:
            self.label17.show()
            self.label18.show()
            self.textbox11.show()
            self.textbox12.show()
    
    'deal with 45 degree checkmarked when uploading saved information'
    def b1_function_previoussave(self):
        if self.b2.isChecked()== False:
            self.label4.setText('Catalyst Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Sample Area ⊥ to Beam [cm<sup>2</sup>]:')
            self.label5.setWordWrap(False)
            self.label7.setText('Estimated Edge Step:')
        else:
            self.label4.setText('Projected Catalyst Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Projected Sample Area to Beam [cm<sup>2</sup>]:')
            self.label5.setWordWrap(True)
            self.label7.setText('Projected Estimated Edge Step:')
            
    
    '45 degree options that changes variables'
    def b1_function(self):
        
        
        
        'Pending Error'
        'if blank then return error in diagnostic'        
        if self.b2.isChecked()== False:
            self.slider_deg.hide()
            self.slider_deg.setValue(45)
            #stp = self.textbox6.text()
            #AL = self.textbox3.text()
            #Area = self.textbox4.text()
            #angleconstants[0] = stp
            #angleconstants[1] =AL
            #angleconstants[2] = Area
            #self.textbox3.setText('{0:0.2f}'.format(float(AL)/math.sqrt(2)))
            #self.textbox3.setText('{0:0.2f}'.format(float(angleconstants[1])*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
            try:
                self.textbox3.setText('{0:0.2f}'.format(float(angleconstants[1])))
            except:
                pass
            #self.textbox4.setText('{0:0.2f}'.format(float(Area)*math.sqrt(2)))
            #self.textbox4.setText('{0:0.2f}'.format(float(angleconstants[2])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
            self.textbox4.setText('{0:0.2f}'.format(float(angleconstants[2])))
            
            self.b2.setText("Sample at "+'{0:0.0f}'.format(round(self.slider_deg.value(),0))+"°")
            self.label4.setText('Catalyst Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Sample Area ⊥ to Beam [cm<sup>2</sup>]:')
            self.label5.setWordWrap(False)
            self.label7.setText('Estimated Edge Step:')
            if self.textbox6.text() =='' or self.textbox6.text()=='N/A':
                ''
            else:
                #self.textbox6.setText('{0:0.4f}'.format(float(stp)/math.sqrt(2)))
                try:
                    self.textbox6.setText('{0:0.4f}'.format(float(angleconstants[0])))
                except:
                    pass
            
            self.textbox3.hide()
            self.textbox4.hide()
            self.label4.hide()
            self.label5.hide()
            
        else:
            self.slider_deg.show()
            self.textbox3.show()
            self.textbox4.show()
            self.label4.show()
            self.label5.show()
            stp = self.textbox6.text()
            self.textbox3.setText(self.textbox15.text())
            AL = self.textbox3.text()
            Area = self.textbox4.text()
            angleconstants[0] = stp
            angleconstants[1] =AL
            angleconstants[2] = Area
            #if changes made only to XAS cell parameters value to be used in setting area
            angleconstants[3] = float(self.combo_cap.currentText())+float(self.combo_pel.currentText())+float(self.textbox13.text())
            #self.textbox3.setText('{0:0.2f}'.format(float(AL)*math.sqrt(2)))
            try:
                self.textbox3.setText('{0:0.2f}'.format(float(angleconstants[1])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
            except:
                pass
            #self.textbox4.setText('{0:0.2f}'.format(float(Area)/math.sqrt(2)))
            self.textbox4.setText('{0:0.2f}'.format(float(angleconstants[2])*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
            self.label4.setText('Projected Catalyst Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Projected Sample Area to Beam [cm<sup>2</sup>]:')
            self.label5.setWordWrap(True)
            self.label7.setText('Projected Estimated Edge Step:')
            
            if  self.textbox6.text() =='' or self.textbox6.text()=='N/A':
                ''
            else:
                #self.textbox6.setText('{0:0.4f}'.format(float(stp)*math.sqrt(2)))
                self.textbox6.setText('{0:0.4f}'.format(float(angleconstants[0])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)))
        if self.textbox6.text() =='' or self.textbox6.text()=='N/A':
            ''
        else:
            if float(self.textbox6.text()) >1:
                self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
            else:
                self.textbox6.setStyleSheet("background-color:rgb(255,255,255)") 
        
        #print("set 45 ")
        #print(angleconstants)
        
    def b3_function(self):
        
        global SampleDilutionBlockWidth
        global XrayInputBlockWidth
        global XrayInputBlockHight
        global XraytextboxW
        global XraytextboxH
        global XraytextboxW2
        global XrayInputBlockHight2
        global ResultsBlockWidth
        global PropertiesBlockWidth  
        
        if self.b3.isChecked()== False:
        
            " Handles the hiding of the panel and markers "
            layercount = self.generalLayout.count()-1
            #print(layercount)
            child = self.generalLayout.takeAt(layercount)
           
            child.widget().hide()
            
            XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+40)
            
        else:
            XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+PropertiesBlockWidth+40)
            self._createPropertiesBlock()
            self.ResizeGUI(activedisplay)
            
    def on_combobox_previoussave(self):
        if self.combo.currentIndex() == 4:
            self.textbox2.setStyleSheet("background-color:rgb(224,224,224)")
            self.textbox2.setText('N/A')
            self.textbox2.setReadOnly(True)
            self.textbox6.setText('N/A')
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight2+40)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight2)
            Properties_frame.setFixedHeight(XrayInputBlockHight2)
            Diluent_frame.setFixedHeight(XrayInputBlockHight2)
            ResultsFrame.setFixedHeight(XrayInputBlockHight2)
        else:
            self.textbox14.hide()
            self.label12.hide()
            self.textbox2.setStyleSheet("background-color:rgb(255,255,255)")
            self.textbox2.setReadOnly(False)
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight+40)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight)
            Properties_frame.setFixedHeight(XrayInputBlockHight)
            Diluent_frame.setFixedHeight(XrayInputBlockHight)
            ResultsFrame.setFixedHeight(XrayInputBlockHight)
    
    # changes layout when other edge is selected 
    def on_combobox_changed(self):
        if self.combo.currentIndex() == 4:
           self.textbox14.show()
           self.label12.show()
           self.textbox15.setText('1.5')
           #self.textbox3.setText('1.5')
           self.textbox11.setText('-1000')
           self.textbox2.setStyleSheet("background-color:rgb(224,224,224)")
           self.textbox2.setText('N/A')
           self.textbox2.setReadOnly(True)
           self.textbox6.setText('N/A')
           self.textbox6.setStyleSheet("background-color:rgb(224,224,224)")
           XASCalcUI.setFixedHeight(self, XrayInputBlockHight2+40)
           XrayInputFrame.setFixedHeight(XrayInputBlockHight2)
           Properties_frame.setFixedHeight(XrayInputBlockHight2)
           Diluent_frame.setFixedHeight(XrayInputBlockHight2)
           ResultsFrame.setFixedHeight(XrayInputBlockHight2)
        else:
            self.textbox14.hide()
            self.label12.hide()
            
            #self.textbox3.setText('2.6')
            self.textbox15.setText('2.6')
            self.textbox11.setText('-200')
           
            if self.textbox2.text() =='N/A':
                self.textbox2.setStyleSheet("background-color:rgb(255,255,255)")
                self.textbox2.clear()
                self.textbox6.clear()
                self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
            self.textbox2.setReadOnly(False)
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight+40)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight)
            Properties_frame.setFixedHeight(XrayInputBlockHight)
            Diluent_frame.setFixedHeight(XrayInputBlockHight)
            ResultsFrame.setFixedHeight(XrayInputBlockHight)
        
        
    def _createResultsBlock(self):
        global ResultsFrame
        global activedisplay
        '''Define QFrame'''
        ResultsFrame = QFrame()
        ResultsFrame.setFrameShape(QFrame.StyledPanel)
        ResultsFrame.setLineWidth(1)
                
        self.generalLayout.addWidget(ResultsFrame)
           
        """Define Layout"""
        OutputLayout = QGridLayout()
        ResultsFrame.setLayout(OutputLayout)
        ResultsFrame.setFixedWidth(ResultsBlockWidth)
        ResultsFrame.setMinimumHeight(XrayInputBlockHight)
        #ResultsFrame.setFixedHeight(XrayInputBlockHight) 
        """Text Labels"""
        #Create Header Label
        self.label_Result01 = QLabel('Results')
        self.label_Result01.setAlignment(Qt.AlignLeft)
        self.label_Result01.setStyleSheet("font-weight: bold; text-decoration: underline")
        OutputLayout.addWidget(self.label_Result01, 0, 0, 0 ,1)
        self.generalLayout.addLayout(OutputLayout)
        
        
        
        # Create Label for Total Mass
        self.label6 = QLabel('Diluted Sample Mass [mg]:')
        self.label6.setAlignment(Qt.AlignRight)
        self.label6.setWordWrap(True)
        OutputLayout.addWidget(self.label6, 1, 0,1,1)
        self.generalLayout.addLayout(OutputLayout)
        self.label6.setFixedSize(XraytextboxW,XraytextboxH)
        
        
        # Create Label for Estimated Edge Step
        self.label7 = QLabel('Estimated Edge Step:')
        self.label7.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label7, 2, 0,1,1)
        self.label7.setWordWrap(True)
        self.generalLayout.addLayout(OutputLayout)
        self.label7.setFixedSize(XraytextboxW,XraytextboxH)
        
        #Create Label for Sample Mass
        self.label8 = QLabel('Sample Mass [mg]:')
        self.label8.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label8, 3, 0,1,1)
        self.generalLayout.addLayout(OutputLayout)
        self.label8.setFixedSize(XraytextboxW,XraytextboxH)
        
        # Create Lable for Diluent Mass
        self.label9 = QLabel('Diluent Mass [mg]:')
        self.label9.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label9, 4, 0,1,1)
        self.generalLayout.addLayout(OutputLayout)
        self.label9.setFixedSize(XraytextboxW,XraytextboxH)
        
        # Create Label for Edge Energy
        self.label10 = QLabel('Edge Energy [eV]:')
        self.label10.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label10, 5, 0,1,1)
        self.generalLayout.addLayout(OutputLayout)
        self.label10.setFixedSize(XraytextboxW,XraytextboxH)
        
        # Create Editable Textbox for Diagnostics
        self.textbox_Xray_05 = QLineEdit()
        self.textbox_Xray_05.setPlaceholderText('Diagnostics')
        self.textbox_Xray_05.setAlignment(Qt.AlignCenter)
        OutputLayout.addWidget(self.textbox_Xray_05, 7, 0,1,2)
        self.generalLayout.addLayout(OutputLayout)
        self.textbox_Xray_05.setFixedSize(round(XraytextboxW*2.15),round(XraytextboxH/1.5))
        
        self.label11 = QLabel(self)
        #pixmap = QPixmap('SSRL_logo.png')
        #pixmap = QPixmap('SSRL_logo_2021.png')
        #pixmap = QPixmap(os.path.join(os.getcwd(),'src','images','SSRL_logo_2021.png'))
        pixmap = QPixmap(resource_path('SSRL_logo_2021.png'))
        self.label11.setPixmap(pixmap)
        self.label11.setAlignment(Qt.AlignCenter)
        OutputLayout.addWidget(self.label11, 8, 0,5,2)
        
        self.generalLayout.addLayout(OutputLayout) 
        
        "Buttons"
        self.button_Input02 = QPushButton('Calculate Sample Mass')
        OutputLayout.addWidget(self.button_Input02 ,0, 1,1,1)
        self.generalLayout.addLayout(OutputLayout)
        self.button_Input02.clicked.connect(self.calculateSampleComp)
        self.button_Input02.clicked.connect(self.calculateResult)
        self.button_Input02.setFixedSize(XraytextboxW,XraytextboxH)
        
        
        #self.b1 = QCheckBox()
        #OutputLayout.addWidget(self.b1, 0, 0,2,1)
        #self.b1.setText("Show Plot")
        #self.b1.setStyleSheet('QCheckBox::indicator { width: 12px; height: 12px;};')
        #self.b1.toggled.connect(self.showlimits)
        
        #checkbox to show Xray transmission block
        self.b3 = QCheckBox()
        #self.b3.setLayoutDirection(Qt.RightToLeft)
        OutputLayout.addWidget(self.b3, 6, 0,1,2)
        self.b3.setText("X-ray transmission through media")
        self.b3.toggled.connect(self.b3_function)
        #self.b3.toggled.connect(self.mousePressEvent)
        #self.b3.toggled.connect(self.ResizeGUI(activedisplay))
            
        
        self.b3.setStyleSheet('QCheckBox::indicator { width: 12px; height: 12px;};')
        
        """Output Fields"""
        # Create Editable Textbox for Total Sample Mass
        self.textbox5 = QLineEdit()
        self.textbox5.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox5.setAlignment(Qt.AlignRight)
        self.textbox5.setReadOnly(True)
        OutputLayout.addWidget(self.textbox5, 1, 1)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Editable Textbox for Estimated Edge Step 
        self.textbox6 = QLineEdit()
        self.textbox6.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox6.setAlignment(Qt.AlignRight)
        self.textbox6.setReadOnly(True)
        OutputLayout.addWidget(self.textbox6, 2, 1)
        self.generalLayout.addLayout(OutputLayout)
        
        
        # Create Editable Textbox for Sample Mass
        self.textbox7 = QLineEdit()
        self.textbox7.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox7.setAlignment(Qt.AlignRight)
        self.textbox7.setReadOnly(True)
        OutputLayout.addWidget(self.textbox7, 3, 1)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Editable Textbox for Diluent Mass
        self.textbox8 = QLineEdit()
        self.textbox8.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox8.setAlignment(Qt.AlignRight)
        self.textbox8.setReadOnly(True)
        OutputLayout.addWidget(self.textbox8, 4, 1)
        self.generalLayout.addLayout(OutputLayout)

        # Create Editable Textbox for Edge Enrgy
        self.textbox9 = QLineEdit()
        self.textbox9.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox9.setAlignment(Qt.AlignRight)
        self.textbox9.setReadOnly(True)
        OutputLayout.addWidget(self.textbox9, 5, 1)
        self.generalLayout.addLayout(OutputLayout)
    
    def ResizeGUI(self,displaydex):
        global activedisplay
        global SampleDilutionBlockWidth
        global XrayInputBlockWidth
        global XrayInputBlockHight
        global XraytextboxW
        global XraytextboxH
        global XraytextboxW2
        global XrayInputBlockHight2
        global ResultsBlockWidth
        global PropertiesBlockWidth     
                
        
        for displayNr in range(QDesktopWidget().screenCount()):
            sizeObject = QDesktopWidget().availableGeometry(displayNr)
            #print("Display: " + str(displayNr) + " Screen size : " + str(sizeObject.height()) + "x" + str(sizeObject.width()))
            displaysizesW[displayNr] = sizeObject.width()
            displaysizesH[displayNr] = sizeObject.height()
        
        screenW = displaysizesW[displaydex]
        screenH = displaysizesH[displaydex]
        
        SampleDilutionBlockWidth = round(300/1290*screenW)
        XrayInputBlockWidth = round(230/1290*screenW)
        #XrayInputBlockHight = round(570/1162*screenH)
        XrayInputBlockHight = round(520/1162*screenH)
        XraytextboxW = round(90/1290*screenW)
        XraytextboxH = round(27/1162*screenH)
        XraytextboxW2 = round(45/1290*screenW)
        #XrayInputBlockHight2 = round((570/1162+30/1162)*screenH)
        XrayInputBlockHight2 = round((550/1162+30/1162)*screenH)
        ResultsBlockWidth = round(220/1290*screenW)
        PropertiesBlockWidth = round((230+50+20+10)/1290*screenW)
        fontsize = round(11/1162*screenH)
        
       
        if self.combo.currentIndex() == 4:
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight2+40)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight2)
        else:
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight+40)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight)
        
        
        
        Properties_frame.setFixedWidth(PropertiesBlockWidth)
        XrayInputFrame.setFixedWidth(XrayInputBlockWidth)
        Diluent_frame.setFixedWidth(SampleDilutionBlockWidth)
        ResultsFrame.setFixedWidth(ResultsBlockWidth)
        
        if self.combo.currentIndex() == 4:
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight2+40)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight2)
            Properties_frame.setFixedHeight(XrayInputBlockHight2)
            Diluent_frame.setFixedHeight(XrayInputBlockHight2)
            ResultsFrame.setFixedHeight(XrayInputBlockHight2)
        else:
            Properties_frame.setFixedHeight(XrayInputBlockHight)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight)
            Diluent_frame.setFixedHeight(XrayInputBlockHight)
            ResultsFrame.setFixedHeight(XrayInputBlockHight)
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight+40)
        
        
        self.mainMenu.setStyleSheet(''' font-size: '''+str(fontsize)+'''px; ''')
        Properties_frame.setStyleSheet(''' font-size: '''+str(fontsize)+'''px; ''')
        XrayInputFrame.setStyleSheet(''' font-size: '''+str(fontsize)+'''px; ''')
        Diluent_frame.setStyleSheet(''' font-size: '''+str(fontsize)+'''px; ''')
        ResultsFrame.setStyleSheet(''' font-size: '''+str(fontsize)+'''px; ''')
        
        if self.b3.isChecked()== True:
            self.label_P01.setFixedSize(XraytextboxW2,XraytextboxH)
            self.label_P02.setFixedSize(XraytextboxW2,XraytextboxH)
            self.label_P06.setFixedSize(XraytextboxW2,XraytextboxH)
            self.label_P07.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textbox_P02.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textbox_P03.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textbox_P04.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textbox_P05.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo2.setFixedSize(XraytextboxW,XraytextboxH)
            self.combo_U2.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo3.setFixedSize(XraytextboxW,XraytextboxH)
            self.combo_U3.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo4.setFixedSize(XraytextboxW,XraytextboxH)
            self.combo_U4.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo5.setFixedSize(XraytextboxW,XraytextboxH)
            self.combo_U5.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP04.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP05.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP06.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP07.setFixedSize(XraytextboxW2,XraytextboxH)
            self.combo6.setFixedSize(XraytextboxW,XraytextboxH)
            self.combo7.setFixedSize(XraytextboxW,XraytextboxH)
            self.combo_C1.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP08.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP09.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP10.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP11.setFixedSize(XraytextboxW2,XraytextboxH)
            self.textboxP12.setFixedSize(XraytextboxW2,XraytextboxH)
        #if self.b3.isChecked()== True:
            XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+PropertiesBlockWidth+40)
        else:
            XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+40)
            
        
        self.textbox_dil01.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox_dil02.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox_dil03.setFixedSize(XraytextboxW2,XraytextboxH)
        self.textbox_dil04.setFixedSize(XraytextboxW2,XraytextboxH)
        #self.label_dil07.setFixedSize(XraytextboxW2,XraytextboxH*6) 
        #self.label_dil06.setFixedSize(XraytextboxW2,XraytextboxH*6) 
        self.button_dil00.setFixedSize(XraytextboxW,XraytextboxH)   
        self.button_dil01.setFixedSize(XraytextboxW,XraytextboxH)
        self.button_dil02.setFixedSize(round(XraytextboxW*2.1),XraytextboxH)
                                                                              
        self.textbox1.setFixedSize(XraytextboxW,XraytextboxH)                                                                                                                                                                                                                                                                                                                               
        self.textbox2.setFixedSize(XraytextboxW,XraytextboxH)
        self.combo.setFixedSize(XraytextboxW,XraytextboxH) 
        self.textbox14.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox3.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox15.setFixedSize(XraytextboxW,XraytextboxH)
        self.combo_cap.setFixedSize(XraytextboxW,XraytextboxH)
        self.combo_pel.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox13.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox4.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox16.setFixedSize(XraytextboxW,XraytextboxH)
        self.slider_deg.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox11.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox12.setFixedSize(XraytextboxW,XraytextboxH)
        #self.button_Input01.setFixedSize(XraytextboxW,XraytextboxH)
        self.button_Input01.setFixedSize(round(XraytextboxW*2.3),round(XraytextboxH*.9))
                                                                                                        
        
        self.label6.setFixedSize(XraytextboxW,XraytextboxH)
        self.label7.setFixedSize(XraytextboxW,XraytextboxH)
        self.label8.setFixedSize(XraytextboxW,XraytextboxH)
        self.label9.setFixedSize(XraytextboxW,XraytextboxH)
        self.label10.setFixedSize(XraytextboxW,XraytextboxH)
        self.button_Input02.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox5.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox6.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox7.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox8.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox9.setFixedSize(XraytextboxW,XraytextboxH)
        self.textbox_Xray_05.setFixedSize(round(XraytextboxW*2.15),round(XraytextboxH/1.5))      
        
        activedisplay = displaydex 
        
    def textlabels(self):
        saverlabel[0] = 'Support:'
        saverlabel[1] = 'Metal Site #1:'
        saverlabel[2] = 'Metal Site #1 wt%:'
        saverlabel[3] = 'Metal Site #2:'
        saverlabel[4] = 'Metal Site #2 wt%:'
        saverlabel[5] = 'Support:'
        saverlabel[6] = 'Metal Complex:'
        saverlabel[7] = 'Complex wt%:'
        saverlabel[8] = 'Metal Loading wt%:'
        saverlabel[9] = 'Metal Center:'
        saverlabel[10] = 'Sample Stoichiometry:'
        saverlabel[11] = 'Diluent:'
        saverlabel[12] = 'Sample Ratio:'
        saverlabel[13] = 'Diluent Ratio:'
        saverlabel[14] = 'Diluent Sample Mass Formula:'
        saverlabel[15] = 'Element to be Scanned:'
        saverlabel[16] = 'Edge to be Scanned:'
        saverlabel[17] = 'Energy to Calculate Sample Mass:'
        'need to at 45 to saver and checkmark if statements to correct'
        saverlabel[18] = 'Sample at 45 deg:'
        saverlabel[19] = 'Projected Total Sample Absorptoin at E0 ± 50 eV:'
        'add radio button state to saver'
        saverlabel[20] = 'Capillary/Pellet index:'
        saverlabel[21] = 'Bed Length:'
        saverlabel[22] = 'Sample Area Perpendicular to Beam:'
        saverlabel[23] = 'Lower Limit of mu Average Plot:'
        saverlabel[24] = 'Upper Limit of mu Average Plot:'
        saverlabel[25] = 'Diluted Sample Mass:'
        saverlabel[26] = 'Estimated Edge Step:'
        saverlabel[27] = 'Sample Mass:'
        saverlabel[28] = 'Diluent Mass:'
        saverlabel[29] = 'Edge Energy:'
        'xray transmission media checked'
        saverlabel[30] = 'X-Ray Transmission Checked:'
        saverlabel[31] = 'Common Gas:'
        saverlabel[32] = 'Thickness:'
        saverlabel[33] = 'Unit:'
        saverlabel[34] = '% Transmitted:'
        saverlabel[35] = 'Common Material:'
        saverlabel[36] = 'Thickness:'
        saverlabel[37] = 'Unit:'
        saverlabel[38] = '% Transmitted:'
        saverlabel[39] = 'Common Solvent:'
        saverlabel[40] = 'Thickness:'
        saverlabel[41] = 'Unit:'
        saverlabel[42] = '% Transmitted:'
        saverlabel[43] = 'Common Metal:'
        saverlabel[44] = 'Thickness:'
        saverlabel[45] = 'Unit:'
        saverlabel[46] = '% Transmitted:'
        saverlabel[47] = 'IC Gas 1:'
        saverlabel[48] = 'IC Gas 2:'
        saverlabel[49] = 'IC Gas 1 %:'
        saverlabel[50] = 'Total Pressure:'
        saverlabel[51] = 'IC Length:'
        saverlabel[52] = '% Beam Absorbed:'
        saverlabel[53] = 'Degree value:'
        saverlabel[54] = 'XAS Cell index:'
        saverlabel[55] = 'transmission stp:'
        saverlabel[56] = 'Transmission AL:'
        saverlabel[57] = 'Transmission Area:'
        saverlabel[58] = 'Cal results clicks:'
        saverlabel[59] = 'SUM of XAS  Cells:'
        saverlabel[60] = 'Total Sample Absorptoin at E0 ± 50 eV:'
        #
        
        #print(saverlabel)
        
    
    def SaveResults(self):
        saver[0] = samplesaver[1]
        saver[53] = samplesaver[1]
        saver[1] = samplesaver[2]
        saver[2] = samplesaver[3]
        saver[3] = samplesaver[4]
        saver[4] = samplesaver[5]
        saver[5] = complexsaver[1]
        saver[6] = complexsaver[2]
        saver[7] = complexsaver[3]
        saver[8] = complexsaver[4]
        saver[9] = complexsaver[5]
        saver[10] = self.textbox_dil01.text() 
        saver[11] = self.textbox_dil02.text()
        saver[12] = self.textbox_dil03.text()
        saver[13] = self.textbox_dil04.text()
        saver[14] = self.textbox1.text()
        saver[15] = self.textbox2.text()
        'K L1 to L3 combo and other index'
        saver[16] = self.combo.currentIndex()
        'edge to be scanned needs to be floated'
        saver[17] = self.textbox14.text() 
        'need to at 45 to saver and checkmark if statements to correct'
        saver[18] = self.b2.checkState()
        if self.b2.isChecked()== True:
            saver[53] = self.slider_deg.value()
            saver[55] = angleconstants[0]
            saver[56] = angleconstants[1]
            saver[57] = angleconstants[2]
            saver[59] = angleconstants[3]
        saver[19] = self.textbox3.text()
        saver[60] = self.textbox15.text()
        'radio butnn checkstate'
        
        if self.radioButton1.isChecked():
            saver[20] = 1
            saver[54] = int(self.combo_cap.currentText())
        if self.radioButton2.isChecked():
            saver[20] = 2
            saver[54] = int(self.combo_pel.currentText())
        if self.radioButton3.isChecked():
            saver[20] = 3
        saver[21] = self.textbox13.text()
        saver[22] = self.textbox4.text()
        saver[23] = self.textbox11.text()
        saver[24] = self.textbox12.text()
        saver[25] = self.textbox5.text()
        saver[26] = self.textbox6.text()
        saver[27] = self.textbox7.text()
        saver[28] = self.textbox8.text()
        saver[29] = self.textbox9.text()
        saver[30] = self.b3.checkState()
        if self.b3.isChecked()== True:
            saver[31] = self.combo3.currentIndex()
            saver[32] = self.textbox_P02.text()
            saver[33] = self.combo_U3.currentIndex()
            saver[34] = self.textboxP04.text()
            saver[35] = self.combo2.currentIndex()
            saver[36] = self.textbox_P03.text()
            saver[37] = self.combo_U2.currentIndex()
            saver[38] = self.textboxP05.text()
            saver[39] = self.combo4.currentIndex()
            saver[40] = self.textbox_P04.text()
            saver[41] = self.combo_U4.currentIndex()
            saver[42] = self.textboxP06.text()
            saver[43] = self.combo5.currentIndex()
            saver[44] = self.textbox_P05.text()
            saver[45] = self.combo_U5.currentIndex()
            saver[46] = self.textboxP07.text()
            saver[47] = self.combo6.currentIndex()
            saver[48] = self.combo7.currentIndex()
            saver[49] = self.slider.value()
            saver[50] = self.slider2.value()
            saver[51] = self.combo_C1.currentIndex()
            saver[52] = self.textboxP11.text()
        
        
        saver[58] = int(calculateresult_num)
        
            
        
   
    def opencatfile(self):
       global filePath
       filePath = QFileDialog.getOpenFileName(self)[0]
       if filePath =='':
           self.textbox_dil05.setText('No File Imported')
       else:
           i = 1
           'read file contents and place values on calculator'
           with open (filePath,'r') as f:
               myline = f.readline()
               for myline in f:
                   myline = myline.split('\n')[0]
                   saver[i] = myline.split('\t ')[1]
                   if saver[i] == 'None':
                       saver[i] = ''
                   i=i+1
           self.textbox_dil06.setText(filePath)    
           print(saver)
           f.close()
                   
           print('File Openned')
           self.PreviousSave()
       
       
      
       
    def SaveAs(self):
        global filePath
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "",
						"txt(*.txt);;All Files(*.*) ")
        try:
        #data = np.concatenate(saver,saverlabel)  
            with open (filePath,'w') as f:
                #for i in saver:
                    #f.write('\n%s' % i)
                #f.close()
                
                for i in range(len(saver)):
                    #f.write(f'{saverlabel[i]}' +'\t'*6 + '{saver[i]}\n')
                    f.write('%-50s| \t %s\n' % (saverlabel[i] , saver[i]))
                    #f.write("%s \t\t\t\t\t\t %s\n" % (saverlabel[i], saver[i]))
                f.close()  
            print('File created')
            self.textbox_dil06.setText(filePath)
        except:
            pass
        
        
    
    def Savetoopenfile(self):
        self.textlabels()
        global filePath
        filePath = self.textbox_dil06.text()
        if filePath != '':
            with open (filePath,'w') as f:
                for i in range(len(saver)):
                    
                    f.write('%-50s| \t %s\n' % (saverlabel[i] , saver[i]))
                    
                    #f.write("%s \t\t%s\n" % (saverlabel[i], saver[i]))
                f.close()
                #for i in saver:
                    #f.write('\n%s' % i)
                #f.close()
                print('File overwritten')
        else:
            print('No File openned')
            #for i in range(len(saver)):
                #f.write(f"{saver[i]}\n")
                #f.write(str(saver[i]))
                
            #f.writelines("%s" % l for l in lines)
        #print(f)
        
		
		
    
    def PreviousSave(self):
        samplesaver[1] = saver[53] 
        samplesaver[2] = saver[1]
        samplesaver[3] = saver[2]
        samplesaver[4] = saver[3]
        samplesaver[5] = saver[4]
        complexsaver[1] = saver[5]
        complexsaver[2] = saver[6]
        complexsaver[3] = saver[7]
        complexsaver[4] = saver[8]
        complexsaver[5] = saver[9]
        self.textbox_dil01.setText(saver[10])
        self.textbox_dil02.setText(saver[11])
        self.textbox_dil03.setText(saver[12])
        self.textbox_dil04.setText(saver[13])
        self.textbox1.setText(saver[14])
        self.textbox2.setText(saver[15])
        self.combo.setCurrentIndex(int(saver[16]))
        self.textbox14.setText(saver[17])
        ' 45 deg check state'
        if float(saver[18]) != self.b2.checkState():
            #self.b2.setCheckState(2)
            if float(saver[18]) == 0:
                self.b2.setCheckState(0)
            else:
                self.b2.setCheckState(2) 
                self.slider_deg.setValue(int(saver[53])) 
                angleconstants[0] = saver[55] 
                angleconstants[1] = saver[56]
                angleconstants[2] = saver[57]
                angleconstants[3] = saver[59]
            #self.b2.click()
        self.b1_function_previoussave()
        self.textbox3.setText(saver[19])
        self.textbox15.setText(saver[60])
        if saver[20] != '':
            if float(saver[20]) == 1:
                self.radioButton1.click()
                self.combo_cap.setCurrentText(saver[54])
            if float(saver[20]) == 2:
                self.radioButton2.click()
                self.combo_pel.setCurrentText(saver[54])
            if float(saver[20]) == 3:
                self.radioButton3.click()
        self.textbox13.setText(saver[21])
        self.textbox4.setText(saver[22])
        self.textbox11.setText(saver[23])
        self.textbox12.setText(saver[24])
        self.textbox5.setText(saver[25])
        self.textbox6.setText(saver[26])
        self.textbox7.setText(saver[27])
        self.textbox8.setText(saver[28])
        self.textbox9.setText(saver[29])
        self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
        #print(saver[18])
        #print(self.b2.checkState())
        
        if saver[26] != '':
            if saver[26] != 'N/A':
                if float(saver[26]) >1:
                    self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
                else:
                    self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
            else:
                self.textbox6.setStyleSheet("background-color:rgb(224,224,224)")
        self.on_combobox_previoussave()
       
        
       
        #checkstate of xray properties, if not correct click so data fields can be populated
        if float(saver[30]) != self.b3.checkState():
            self.b3.setCheckState(2)
            
        
        if float(saver[30]) == 2:
            self.combo3.setCurrentIndex(int(saver[31]))
            self.textbox_P02.setText(saver[32])
            self.combo_U3.setCurrentIndex(int(saver[33]))
            self.textboxP04.setText(saver[34])
            self.combo2.setCurrentIndex(int(saver[35]))
            self.textbox_P03.setText(saver[36])
            self.combo_U2.setCurrentIndex(int(saver[37]))
            self.textboxP05.setText(saver[38])
            self.combo4.setCurrentIndex(int(saver[39]))
            self.textbox_P04.setText(saver[40])
            self.combo_U4.setCurrentIndex(int(saver[41]))
            self.textboxP06.setText(saver[42])
            self.combo5.setCurrentIndex(int(saver[43]))
            self.textbox_P05.setText(saver[44])
            self.combo_U5.setCurrentIndex(int(saver[45]))
            self.textboxP07.setText(saver[46])
            self.combo6.setCurrentIndex(int(saver[47]))
            self.combo7.setCurrentIndex(int(saver[48]))
            self.slider.setValue(int(saver[49]))
            self.slider2.setValue(int(saver[50]))
            self.combo_C1.setCurrentIndex(int(saver[51]))
            self.textboxP11.setText(saver[52])
        else:
            self.b3.setCheckState(0)
        
       
        global calculateresult_num
        calculateresult_num = int(saver[58])  
        
        print('File imported')
        #print(ksavingcounter)
        
        
        
    
        
        
    def calculateSampleComp(self):
        """Evaluate expressions"""
        Sample = self.textbox_dil01.text()
        Diluent = self.textbox_dil02.text()
        Sample_DR = self.textbox_dil03.text()
        Diluent_DR = self.textbox_dil04.text()
        
        Error_message, Result = XASStoichCalc(Sample, Diluent, Sample_DR, Diluent_DR)
        if "ERROR" in Error_message:
            self.textbox_dil05.setText(Result)
        else:
            self.textbox1.setText(Result)
            self.textbox_dil05.setText(Error_message)
        
        
    def calculateResult(self):
        """Evaluate expressions."""
        
        #display both y1 y2 coordinates for 1st plot  
        def make_format(current, other):
        # current and other are axes
            def format_coord(x, y):
                # x, y are data coordinates
                # convert to display coords
                display_coord = current.transData.transform((x,y))
                inv = other.transData.inverted()
                # convert back to data coords with respect to ax
                ax_coord = inv.transform(display_coord)
                coords = [ax_coord, (x, y)]
                return ('Sample Absorption: {:<40}    Crystal Glitches: {:<}'.format(*['({:.3f}, {:.3f})'.format(x, y) for x,y in coords]))
            return format_coord
        
        
        
        Sample = self.textbox1.text()
        Element = self.textbox2.text()
        if self.combo.currentIndex() == 4:
            Edge = self.textbox14.text()
        else:
            Edge = self.combo.currentText()
        AL = self.textbox3.text()
        #AL = self.textbox15.text()
        Area = self.textbox4.text()
        
        self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
        
        #Area = self.combo2.currentText()
        if self.textbox_dil03.text() == '':
            A = 1
        else:
            A = float(self.textbox_dil03.text())
        
        
        if self.textbox_dil04.text() == '':
            B= 0
        else:
            B = float(self.textbox_dil04.text())
        
        MF_Samp = A/(A+B)
        MF_Dil = 1-MF_Samp
        
        Result, Enot, ms, stp,muave = XASMassCalc(Sample, Element, Edge, Area, AL)
        
        # correction when edge step negative due to slope in backgound
        whilecount = 1
        while stp<=0 and whilecount<49:
            #global whilecount
            
            Result_stp, Enot_stp, ms_stp, stp,muave_stp = XASMassCalc(Sample, Element, Edge, Area, AL,50-10*whilecount,50-10*whilecount)
            whilecount +=1
            newsetp = 50-whilecount
            #print(whilecount)
        
        #if 45 deg selected and 1st time in calculation define value for stp vector.
        global calculateresult_num
        #print(calculateresult_num)
        
        # if starrting with 45 degree fix
        if calculateresult_num ==1 and self.b2.isChecked()== True:
            angleconstants[0] = stp
        calculateresult_num += 1
        import math
       
        ''''''
        if 'ERROR' in Result:
            self.textbox_Xray_05.setText(Result)
        else:
            'Pending Error'
            if self.b2.isChecked()== False:
                ''
            else:
                #stp45 = stp*math.sqrt(1)
                stp45 = stp
                
            #AL45 = float(AL)*math.sqrt(1)
            #self.textbox3.setText('{0:0.2f}'.format(float(AL)*math.sqrt(2)))
                if angleconstants[1] != self.textbox15.text():
                    angleconstants[1] = float(self.textbox15.text())
                    #AL45 = float(AL)
                    AL45 = float(angleconstants[1])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
                    #angleconstants[1]  = '{0:0.1f}'.format(AL45) 
                    #angleconstants[1] = '{0:0.1f}'.format(AL45*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360))
                    #stp change when changing AL at degree
                    stp45 = float(stp45)
                    angleconstants[0] = stp45*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
                    #print('{0:0.2f}'.format(angleconstants[0]))
                else:
                    AL45 = float(AL)
                    ''
                    #AL45 = float(angleconstants[1])/math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
            
            #Area45 = float(Area)/math.sqrt(1)
            #self.textbox4.setText('{0:0.2f}'.format(float(Area)/math.sqrt(2)))
                Area45 = float(angleconstants[2])*math.sin(round(self.slider_deg.value(),0)*2*math.pi/360)
            
            
            
            self.textbox5.setText('{0:0.2f}'.format(ms))
            if self.b2.isChecked()== False:
                self.textbox6.setText('{0:0.4f}'.format(stp))
                if stp >1:
                    self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
            else:
                self.textbox6.setText('{0:0.4f}'.format(stp45))
                self.textbox3.setText('{0:0.2f}'.format(AL45))
                self.textbox4.setText('{0:0.2f}'.format(Area45))
                #print("calc result " )
                #print(angleconstants)
                #print('{0:0.2f}'.format(AL45))
                
                
            
            if self.b2.isChecked()== True  and self.textbox6.text() != '':
                if float(self.textbox6.text()) >1:
                    self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")                
            self.textbox7.setText('{0:0.2f}'.format(ms*MF_Samp))
            self.textbox8.setText('{0:0.2f}'.format(ms*MF_Dil))
            self.textbox9.setText('{0:0.0f}'.format(Enot))
            self.textbox_Xray_05.clear()
        
            
                        
        
        #if self.textbox11.text() == '' or self.textbox12.text() == '':
        if self.b1.isChecked()== False:
            self.textbox_Xray_05.setText(Result)
            if whilecount !=1 and self.b2.isChecked()== False:
                self.textbox_Xray_05.setText('Note: Edge step at: E0 ± ' + str(newsetp) +' eV, consider fluorescence')
            if whilecount !=1 and self.b2.isChecked()== True:
                self.textbox_Xray_05.setText('Note: Edge step at: E0 ± ' + str(newsetp) +' eV')
            if whilecount >=48:
                self.textbox_Xray_05.setText('Background Level Edge Step')
            
        if 'ERROR' in Result:
            self.textbox_Xray_05.setText(Result)
        if self.b1.isChecked()== True:
            if whilecount !=1 and self.b2.isChecked()== False:
                self.textbox_Xray_05.setText('Note: Edge step at: E0 ± ' + str(newsetp) +' eV, consider fluorescence')
            if whilecount !=1 and self.b2.isChecked()== True:
                self.textbox_Xray_05.setText('Note: Edge step at: E0 ± ' + str(newsetp) +' eV')
            if whilecount >=48:
                self.textbox_Xray_05.setText('Background Level Edge Step')
            else:
                ''
                #self.textbox_Xray_05.clear()
            #section to ensure plot auto appears as new window
            
            ################################
            ###must comment out for auto py to exe to not have EXE crash
            #from IPython import get_ipython
            #get_ipython().run_line_magic('matplotlib','qt5')
            ########################################
           
            #Create plot of AL over energy range kspace over energy range and list reulsts table in last fig
            
            
            kspaceedges, atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols = XASEZero(Sample,Enot)
            
            atomicedgesall,atomicsymbolsall,atomicnumbersall,atomicedgesymbolsall = XASEZeroList(Sample)
            
            #ploting limits
            delta1 = float(self.textbox11.text())
            delta2 = float(self.textbox12.text())
            start = delta1
            interval = 0.5
            stop = delta2+interval
            figure, axis = plt.subplots(1, 3,figsize=(18,5))
            
            
            #create vector for x axis of fig 1 and fif 2
            x = np.arange(start, stop, interval)
            x2 = np.arange(1, stop, interval)
            #define how long the vectors are
            length = len(x)
            length2 = len(x2)
            length3 = len(kspaceedges)
            length4 = len(atomicsymbolsall)
            #define blank y values to be populated by later functions
            y  = [None] * length #list of modified muave
            y2  = [None] * length2 #list of zeros fro kspace plot ( should be glitches)
            y3 = [None] * length3 #list of edges from sample
            
            
            yedges = [None]* length4
            muaves = [None]*length4 #list of muave for edge label in E plot
            Enots = [None]*length4
            yedges2 = [None]* length4
            Enots2 = [None]*length4
            muaves2 = [None]*length4 #list of muave for edge label in E plot
            kspace  = [None] *length2
        
            #kpace plot y values for now
            for i in range(length3):
                y3[i]=0
            #kspace  y value points are edges of element in sample that could show up in kspace
            for i in range(length2):
                kspace[i] = kspacecalc(x2[i])
                #y2[i] = fct.XASPLOTTER(Sample, Element, Edge, Area, AL, x2[i],delta1)
                #y2[i] =float(y2[i])*(ms/float(Area))/1000
                #y2[i] = (y2[i]-float(AL))/float(AL)
                #y2[i] = 0
            #plot of cystal glitches
            
            x_xrayf_lines = []
            y_xrayf_lines = []
            xrayf_lines_name = []
            #STAFF ONLY#####################
            axis2 = axis[0].twinx()
            
            axis2.format_coord = make_format(axis2, axis[0])
           
            try:
                crystal_BL93_220_90 = open('si2209093.txt').read().splitlines()
                crystal_BL93_220_00 = open('si220093.txt').read().splitlines()
                crystal_BL43_111_90 = open('si1119043.txt').read().splitlines()
                crystal_BL43_111_00 = open('si111043.txt').read().splitlines()
            
            
                crystal_BL93_220_90_x = []
                crystal_BL93_220_00_x = []
                crystal_BL93_220_90_y = []
                crystal_BL93_220_00_y = []
                
                crystal_BL43_111_90_x = []
                crystal_BL43_111_00_x = []
                crystal_BL43_111_90_y = []
                crystal_BL43_111_00_y = []
    
                plot_crystal_BL93_220_90_x = []
                plot_crystal_BL93_220_00_x = []
                plot_crystal_BL93_220_90_y = []
                plot_crystal_BL93_220_00_y = []
                kspace__crystal_BL93_220_90 = []
                kspace__crystal_BL93_220_90_y = []
                kspace__crystal_BL93_220_00 = []
                kspace__crystal_BL93_220_00_y = []
                
                plot_crystal_BL43_111_90_x = []
                plot_crystal_BL43_111_00_x = []
                plot_crystal_BL43_111_90_y = []
                plot_crystal_BL43_111_00_y = []
                kspace__crystal_BL43_111_90 = []
                kspace__crystal_BL43_111_90_y = []
                kspace__crystal_BL43_111_00 = []
                kspace__crystal_BL43_111_00_y = []
                
                
    
                for i in range(len(crystal_BL93_220_90)):
                    crystal_BL93_220_90_x.append(crystal_BL93_220_90[i].split(" ")[0])
                    crystal_BL93_220_90_y.append(crystal_BL93_220_90[i].split(" ")[len(crystal_BL93_220_90[i].split(" "))-1])
                for i in range(len(crystal_BL93_220_00)):    
                    crystal_BL93_220_00_x.append(crystal_BL93_220_00[i].split(" ")[0])
                    crystal_BL93_220_00_y.append(crystal_BL93_220_00[i].split(" ")[len(crystal_BL93_220_00[i].split(" "))-1])
                
                for i in range(len(crystal_BL43_111_90)):
                    crystal_BL43_111_90_x.append(crystal_BL43_111_90[i].split(" ")[0])
                    crystal_BL43_111_90_y.append(crystal_BL43_111_90[i].split(" ")[len(crystal_BL43_111_90[i].split(" "))-1])
                for i in range(len(crystal_BL43_111_00)):    
                    crystal_BL43_111_00_x.append(crystal_BL43_111_00[i].split(" ")[0])
                    crystal_BL43_111_00_y.append(crystal_BL43_111_00[i].split(" ")[len(crystal_BL43_111_00[i].split(" "))-1])
                
                    
                for i in range(len(crystal_BL93_220_90_x)):
                    if float(start)+Enot<float(crystal_BL93_220_90_x[i])<=float(stop)+Enot:
                        plot_crystal_BL93_220_90_x.append(float(crystal_BL93_220_90_x[i]))
                        plot_crystal_BL93_220_90_y.append(float(crystal_BL93_220_90_y[i]))
                        if Enot<float(crystal_BL93_220_90_x[i])<=float(stop)+Enot:
                            kspace__crystal_BL93_220_90.append(kspacecalc(float(crystal_BL93_220_90_x[i])-Enot))
                            kspace__crystal_BL93_220_90_y.append(float(crystal_BL93_220_90_y[i]))
                
                for i in range(len(crystal_BL93_220_00_x)):
                    if float(start)+Enot<float(crystal_BL93_220_00_x[i])<=float(stop)+Enot:
                        plot_crystal_BL93_220_00_x.append(float(crystal_BL93_220_00_x[i]))
                        plot_crystal_BL93_220_00_y.append(float(crystal_BL93_220_00_y[i]))
                        if Enot<float(crystal_BL93_220_00_x[i])<=float(stop)+Enot:
                            kspace__crystal_BL93_220_00.append(kspacecalc(float(crystal_BL93_220_00_x[i])-Enot))
                            kspace__crystal_BL93_220_00_y.append(float(crystal_BL93_220_00_y[i]))
                
                for i in range(len(crystal_BL43_111_90_x)):
                    if float(start)+Enot<float(crystal_BL43_111_90_x[i])<=float(stop)+Enot:
                        plot_crystal_BL43_111_90_x.append(float(crystal_BL43_111_90_x[i]))
                        plot_crystal_BL43_111_90_y.append(float(crystal_BL43_111_90_y[i]))
                        if Enot<float(crystal_BL43_111_90_x[i])<=float(stop)+Enot:
                            kspace__crystal_BL43_111_90.append(kspacecalc(float(crystal_BL43_111_90_x[i])-Enot))
                            kspace__crystal_BL43_111_90_y.append(float(crystal_BL43_111_90_y[i]))
                
                for i in range(len(crystal_BL43_111_00_x)):
                    if float(start)+Enot<float(crystal_BL43_111_00_x[i])<=float(stop)+Enot:
                        plot_crystal_BL43_111_00_x.append(float(crystal_BL43_111_00_x[i]))
                        plot_crystal_BL43_111_00_y.append(float(crystal_BL43_111_00_y[i]))
                        if Enot<float(crystal_BL43_111_00_x[i])<=float(stop)+Enot:
                            kspace__crystal_BL43_111_00.append(kspacecalc(float(crystal_BL43_111_00_x[i])-Enot))
                            kspace__crystal_BL43_111_00_y.append(float(crystal_BL43_111_00_y[i]))
            except:
                pass
            ######print(kspace__crystal_BL93_220_90)
            ######print(kspace__crystal_BL93_220_90_y)
            ##################################
            ###################################
            ###################################
            
            #plot of modified mu average (Absorption length over energy range)
            
            for i in range(length):
                if self.b2.isChecked()== False:
                    y[i] = XASPLOTTER(Sample, Element, Edge, Area, AL, x[i],delta1)
                    y[i] =float(y[i])*(ms/float(Area))/1000
                else:
                    y[i] = XASPLOTTER(Sample, Element, Edge, Area, str(AL45), x[i],delta1) 
                    #y[i] =float(y[i])*(ms/float(Area))*math.sqrt(1) /1000
                    y[i] =float(y[i])*(ms/float(Area))/1000
            #redefining x axis to absolute scale
            x = np.arange(start, stop, interval)+Enot
            
            #fluoresence lines for all elements in sample
            wt_sym = []
            wt = list(xraylib.CompoundParser(Sample)['massFractions'])
            wtelem = list(xraylib.CompoundParser(Sample)['Elements'])
            #print(wt)
            #print(wtelem)
            for i, line in enumerate(wtelem):
                wt_sym.append(xraydb.atomic_symbol(wtelem[i]))
            #print(wt_sym)
            for i in range(length4):
                for name, line in xraydb.xray_lines(atomicsymbolsall[i], atomicedgesymbolsall[i]).items():
                    #print(line[0])
                    xrayf_lines_name.append(name + " " + atomicsymbolsall[i] + " " + atomicedgesymbolsall[i]) 
                    x_xrayf_lines.append(line[0])
                    #print(wt_sym.index(atomicsymbolsall[i]))
                    #y_xrayf_lines.append(line[1]*wt[wt_sym.index(atomicsymbolsall[i])])
                    y_xrayf_lines.append(line[1])
                    #print(line[1])
                #print(atomicsymbolsall)
                #print(x_xrayf_lines)
                #print(y_xrayf_lines)
            
            #print(range(xraylib.CompoundParser(Sample)['Elements']))
            
                #print(line)
                #print(i)
            
            #print(xraylib.CompoundParser(Sample)['massFractions'])
            #print(xraylib.CompoundParser(Sample)['Elements'])
            #print(wt)
            #print(wt_sym)
            #print(atomicsymbolsall)
            #print(atomicedgesymbolsall)
            #print(xrayf_lines_name)
            
            #print(xrayf_lines_name.index('Ka1'+' '+Element+' '+Edge))
            #defining plot names, axis labels and plot colors
            axis[0].plot(x, y, color = 'b', linestyle= '-',label="Total Sample Abs.") #label="XXXX \nI am Trying To Add a New Line of Text"
            
            
            
            
            axis[0].set_xlabel(r"Photon Energy (eV)")
            axis[0].set_xlim([Enot+delta1, Enot+delta2])
            #axis[0].set_ylim([0, float(muave)*(ms/float(Area))/1000*1.5])
            axis[0].set_ylim([0, max(y)*1.5])
            axis[0].set_ylabel(r"Sample Absorption ($µ_{average}$ • Mass/Area)")
    
            axis[1].set_xlim([0, kspacecalc(delta2)])
            
            #axis[1].yaxis.set_visible(False)
            axis[1].set_yticklabels([])
            axis[1].set_ylabel(r"Metal Edge Position(s)")
            #axis[2].xaxis.set_visible(False)
            axis[2].set_ylabel(r"Fluorescence Line Intensity")
            try:
                axis[2].set_xlabel(r"Photon Energy (eV)")
                axis[2].set_xlim([x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]-800, x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]+800])
                axis[2].set_ylim([0, max(y_xrayf_lines)*1])
                #axis[2].fill_between(x_xrayf_lines,y_xrayf_lines,0, where = (x_xrayf_lines>8000) & (x_xrayf_lines<8200), color='g')
                axis[2].fill_between([x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]-250,x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]+250],max(y_xrayf_lines),0, color="#E0E0E0")
            except:
                axis[2].set_xlim([int(Edge)-800, int(Edge)+800])
                axis[2].set_ylim([0, max(y_xrayf_lines)*1])
                pass
            #import matplotlib.ticker as mtick
            #axis[1].yaxis.set_major_formatter(mtick.PercentFormatter())
            
            axis[1].plot(kspace, y2,color = 'b', linestyle= '-')
            axis[1].plot(kspaceedges, y3,color = 'g', linestyle="",marker="o")
            axis[1].set_xlabel(r"$k$ ($\AA$⁻¹)")
            
            #STAFF ONLY#####################
            try:
                import matplotlib.ticker as mtick
                #############axis2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
                label_crystal_BL93_220_90, = axis2.plot(plot_crystal_BL93_220_90_x, plot_crystal_BL93_220_90_y, color = 'r', linestyle= '-',label="Si(220), Φ = 90°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                label_crystal_BL93_220_00, = axis2.plot(plot_crystal_BL93_220_00_x, plot_crystal_BL93_220_00_y, color = 'black', linestyle= '-',label="Si(220), Φ = 0°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                label_crystal_BL43_111_90, = axis2.plot(plot_crystal_BL43_111_90_x, plot_crystal_BL43_111_90_y, color = 'indigo', linestyle= '-',label="Si(111), Φ = 90°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                label_crystal_BL43_111_00, = axis2.plot(plot_crystal_BL43_111_00_x, plot_crystal_BL43_111_00_y, color = 'lime', linestyle= '-',label="Si(111), Φ = 0°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                
                #1st plot y axis limits
                axis2.set_ylim([-7, 7])
                axis2.set_yticklabels([])
                #axis2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
                #2nd plot axis limits
                axis[1].set_ylim(-7, 7)
                #axis[1].set_ylim(min((float(kspace__crystal_BL93_220_90_y.extend(plot_crystal_BL93_220_00_y)))*1.2,max(float(kspace__crystal_BL93_220_90_y.extend(plot_crystal_BL93_220_00_y))))*1.2)
                label_crystal_BL93_220_90_k, = axis[1].plot(kspace__crystal_BL93_220_90, kspace__crystal_BL93_220_90_y, color = 'r', linestyle= '-',label="Si(220), Φ = 90°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                label_crystal_BL93_220_00_k, = axis[1].plot(kspace__crystal_BL93_220_00, kspace__crystal_BL93_220_00_y, color = 'black', linestyle= '-',label="Si(220), Φ = 0°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                label_crystal_BL43_111_90_k, = axis[1].plot(kspace__crystal_BL43_111_90, kspace__crystal_BL43_111_90_y, color = 'indigo', linestyle= '-',label="Si(111), Φ = 90°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                label_crystal_BL43_111_00_k, = axis[1].plot(kspace__crystal_BL43_111_00, kspace__crystal_BL43_111_00_y, color = 'lime', linestyle= '-',label="Si(111), Φ = 0°",linewidth=0.30) #label="XXXX \nI am Trying To Add a New Line of Text"
                
                
                legend_k = axis[1].legend(loc="lower right")
                legend_crystal_BL93_220_90_k,legend_crystal_BL93_220_00_k,legend_crystal_BL43_111_90_k,legend_crystal_BL43_111_00_k = legend_k.get_lines()
                
                legend_crystal_BL93_220_90_k.set_picker(True)
                legend_crystal_BL93_220_00_k.set_picker(True)
                legend_crystal_BL93_220_90_k.set_pickradius(10)
                legend_crystal_BL93_220_00_k.set_pickradius(10)
                legend_crystal_BL43_111_90_k.set_picker(True)
                legend_crystal_BL43_111_00_k.set_picker(True)
                legend_crystal_BL43_111_90_k.set_pickradius(10)
                legend_crystal_BL43_111_00_k.set_pickradius(10)
                
                
                graph_eV = {}
                graph_eV[legend_crystal_BL93_220_90_k] = label_crystal_BL93_220_90
                graph_eV[legend_crystal_BL93_220_00_k] = label_crystal_BL93_220_00
                graph_eV[legend_crystal_BL43_111_90_k] = label_crystal_BL43_111_90
                graph_eV[legend_crystal_BL43_111_00_k] = label_crystal_BL43_111_00
                
                graphs_k = {}
                graphs_k[legend_crystal_BL93_220_90_k] = label_crystal_BL93_220_90_k
                graphs_k[legend_crystal_BL93_220_00_k] = label_crystal_BL93_220_00_k
                graphs_k[legend_crystal_BL43_111_90_k] = label_crystal_BL43_111_90_k
                graphs_k[legend_crystal_BL43_111_00_k] = label_crystal_BL43_111_00_k
                
                label_crystal_BL43_111_90.set_visible(False)
                label_crystal_BL43_111_00.set_visible(False)
                label_crystal_BL43_111_90_k.set_visible(False)
                label_crystal_BL43_111_00_k.set_visible(False)
                
                def on_pick(event):
                    leg_k = event.artist
                    #print(min(plot_crystal_BL93_220_90_y))
                    isVisible = leg_k.get_visible()
                    graphs_k[leg_k].set_visible(not isVisible)
                    graph_eV[leg_k].set_visible(not isVisible)
                    leg_k.set_visible(not isVisible)
                    #axis[1].autoscale(enable=True, axis="y", tight=None)
                    figure.canvas.draw()
                    #figure.canvas.draw_idle()
                
                axis[1].yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
                plt.connect('pick_event',on_pick)
            except:
                pass
            
            ##################################
            
            #defining labels for edges that might show up in kspace region
            for i, txt in enumerate(atomicedgesymbols):
                axis[1].annotate(txt, (kspaceedges[i], y3[i]), # these are the coordinates to position the label
                textcoords="offset points", # how to position the text
                xytext=(10.7,22), # distance from text to points (x,y)
                ha='center',rotation = 45) # horizontal alignment can be left, right or center
          
            #defining labels for edges that might show up in kspace region
            for i, txt in enumerate(atomicsymbols):
                axis[1].annotate(txt, (kspaceedges[i], y3[i]), # these are the coordinates to position the label
                textcoords="offset points", # how to position the text
                xytext=(0,10), # distance from text to points (x,y)
                ha='center',rotation = 45)
            
            ####################staff only###########
            #axis[0].plot(x_xrayf_lines, y_xrayf_lines,color = 'r', linestyle="",marker="o",label="Fluorescence line(s)")
            
            axis[2].vlines(x_xrayf_lines,0, y_xrayf_lines,color = '#EEAD0E',label="Fluorescence line(s)")
            
            for i, txt in enumerate(xrayf_lines_name):
                #change for even or odd for spacing of labels
                if (i % 2) == 0:
                    axis[2].annotate(txt, (x_xrayf_lines[i], y_xrayf_lines[i]), # these are the coordinates to position the label
                textcoords="offset points", # how to position the text
                xytext=(0,y_xrayf_lines[i]*2), # distance from text to points (x,y)
                ha='center',rotation = 0,size=float(round(fontsize*0.8)))
                else:
                    axis[2].annotate(txt, (x_xrayf_lines[i], y_xrayf_lines[i]), # these are the coordinates to position the label
                textcoords="offset points", # how to position the text
                xytext=(0,y_xrayf_lines[i]*2), # distance from text to points (x,y)
                ha='center',rotation = 0,size=float(round(fontsize*0.8)))
            
           
           ####################################################
            
            
            #listing results values in 3 figure
            left = 0.01
            width = 0.01
            bottom  = 0.01
            height = .95
            right = left + width
            top = bottom + height
            
            
            
            axis[2].text(right, top, "Catalyst Sample Absorption:",ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right, top-.05, "Estimated Edge Step:",ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right, top-.1, "Sample mass[mg]:",ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right, top-.15, "Diluent mass[mg]:",ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right, top-.2, "Cell:",ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right+0.7, top, self.textbox3.text(),ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right+0.7, top-0.05, self.textbox6.text(),ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right+0.7, top-0.1, self.textbox7.text(),ha='left', va='top', transform=axis[2].transAxes)
            axis[2].text(right+0.7, top-0.15, self.textbox8.text(),ha='left', va='top', transform=axis[2].transAxes)
            if self.radioButton1.isChecked():
                axis[2].text(right+0.7, top-0.2, "Capillary Cell",ha='left', va='top', transform=axis[2].transAxes)
            if self.radioButton2.isChecked():
                axis[2].text(right+0.7, top-0.2, "Pellet",ha='left', va='top', transform=axis[2].transAxes)
            if self.radioButton3.isChecked():
                axis[2].text(right+0.7, top-0.2, "Other",ha='left', va='top', transform=axis[2].transAxes)
        
            for i in range(length4):
                if self.b2.isChecked()== False:
                    
                    Result1, Enots[i], ms1, yedges[i],muaves[i] = XASMassCalc(Sample, atomicsymbolsall[i], atomicedgesymbolsall[i], Area, AL)
                    
                    muaves[i] =float(muaves[i])*(ms/float(Area))/1000
                    Result2, Enots2[i], ms1, yedges2[i],muaves2[i] = XASMassCalc(Sample, atomicsymbolsall[i], Enots[i], Area, muaves[i])
                    yedges[i]='{0:0.3f}'.format(yedges2[i])
                else:
                    Result1, Enots[i], ms1, yedges[i],muaves[i] = XASMassCalc(Sample, atomicsymbolsall[i], atomicedgesymbolsall[i], Area, str(AL45))
                    muaves[i] =float(muaves[i])*(ms/float(Area))/1000
                    Result2, Enots2[i], ms1, yedges2[i],muaves2[i] = XASMassCalc(Sample, atomicsymbolsall[i], Enots[i], Area, muaves[i])
                    yedges[i]='{0:0.3f}'.format(yedges2[i])
            
            axis[0].plot(Enots, muaves,color = 'g', linestyle="",marker="o",label="Est. Edge Step(s)")
            
           
            axis[0].legend(loc="lower right")
            
            for i, txt in enumerate(yedges):
                axis[0].annotate(txt, (Enots[i], muaves[i]), # these are the coordinates to position the label
                textcoords="offset points", # how to position the text
                xytext=(30,8), # distance from text to points (x,y)
                ha='right',rotation = 0) # horizontal alignment can be left, right or center
            
            #axis[0].set_facecolor("#E0E0E0")
            axis[0].figure.set_facecolor("#E0E0E0")
            #axis[1].set_facecolor("#E0E0E0")
            #axis[2].set_facecolor("#E0E0E0")
            #plt.figure(1)
            #open new figures every time
            plt.get_current_fig_manager().window.setWindowIcon(QIcon(resource_path('CoACCESSScale_v6')))
            
            plt.show
            #replace figure aleady open
            plt.show(block=False)
            
            #code the allow for figure to be copied to clipboard
            import io
            from PyQt5.QtGui import QImage
            from PyQt5.QtWidgets import QApplication
            def add_figure_to_clipboard(event):
                if event.key == "ctrl+c":
                   with io.BytesIO() as buffer:
                        figure.savefig(buffer)
                        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

            figure.canvas.mpl_connect('key_press_event', add_figure_to_clipboard)

        
           
    def clearDilutionInput(self):
        
        #print(self.generalLayout.count())
        #widget= []
        #for i in range(self.generalLayout.count()):
            #print(self.generalLayout.itemAt(i).widget())
            #item = self.generalLayout.itemAt(i).widget()
            #print(self.generalLayout.itemAt(i).widget().children())
            #item2 = self.generalLayout.itemAt(i).widget().findChildren(QLineEdit)
            #print(item2)
            #print(len(self.generalLayout.itemAt(i).widget().children()))
            #for j in len(self.generalLayout.itemAt(i).widget().children()):
            
                #if isinstance(widget[j],QLabel):
                    #print(item2.text)
           
            #print(self.generalLayout.widget().itemAt(2))
        """Clear the Sample and Dilutino Input displays"""
        self.textbox_dil01.clear()
        self.textbox_dil02.clear()
        self.textbox_dil03.clear()
        self.textbox_dil04.clear()
        self.textbox_dil05.clear()
        self.textbox_dil06.clear()
                    
    
    def clearDisplay(self):
        """Clear the input display. and results """
        self.textbox1.clear()
        self.textbox2.clear()
        #self.textbox3.setText('2.5')
        self.combo.setCurrentIndex(0)
        self.radioButton2.setChecked(True)
        self.combo_cap.setCurrentIndex(2)
        self.combo_pel.setCurrentIndex(1)
        self.b1.setChecked(False)
        self.b2.setChecked(False)
        self.textbox3.setText('2.6')
        self.textbox15.setText('2.6')
        #self.textbox4.clear()
        self.textbox5.clear()
        self.textbox6.clear()
        self.textbox7.clear()
        self.textbox8.clear()
        self.textbox_Xray_05.clear()
        self.textbox11.setText('-200')
        self.textbox12.setText('1000')
        self.textbox13.setText('1')
        self.textbox14.clear()
        self.slider_deg.setValue(45)
        self.textbox5.clear()
        self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
        self.textbox7.clear()
        self.textbox8.clear()
        self.textbox9.clear()

    def clearxrayprop(self):
        """Clear the input display."""
        self.textbox_P02.clear()
        self.textbox_P03.clear()
        self.textbox_P04.clear()
        self.textbox_P05.clear()
        self.textboxP04.clear()
        self.textboxP05.clear()
        self.textboxP06.clear()
        self.textboxP07.clear()
        self.combo2.setCurrentIndex(0)
        self.combo_U2.setCurrentIndex(4)
        self.combo3.setCurrentIndex(8)
        self.combo_U3.setCurrentIndex(2)
        self.combo4.setCurrentIndex(0)
        self.combo_U4.setCurrentIndex(2)
        self.combo5.setCurrentIndex(2)
        self.combo_U5.setCurrentIndex(1)
        self.combo6.setCurrentIndex(1)
        self.combo7.setCurrentIndex(2)
        self.combo_C1.setCurrentIndex(1)
        self.slider.setValue(-50)
        self.slider2.setValue(760)
        self.textboxP11.clear()
      
    def Resetall(self):
        
        self.clearDisplay()
        self.clearDilutionInput()
        for i in range(len(samplesaver)):
            samplesaver[i] = ''
            complexsaver[i] = ''
        for i in range(len(angleconstants)):
            angleconstants[i] = ''
        if self.b3.isChecked()== True:
            self.clearxrayprop()
        
    
    def openInfo(self):
        #self.dialog = CatMassInfo(self)
        self.dialog = InfoWindow()
        self.dialog.show()    
        
    def openSampleBuilder(self):
        self.dialog = SampleBuilder(self)
        self.dialog.show()

    
    def Calculatetransbeam(self):
        
        Materialgases = self.combo3.currentText()
        Enot = self.textbox9.text()
        Materialwall = self.combo2.currentText()
        Materialsolvent = self.combo3.currentText()
        Materialmetal = self.combo4.currentText()
        thicknessgas = self.textbox_P02.text()
        thicknesswall = self.textbox_P03.text()
        thicknesssolvent = self.textbox_P04.text()
        thicknessmetal = self.textbox_P05.text()
                
        import numpy as np
        if thicknessgas !='':
            thicknessgas = unitconvert(thicknessgas,self.combo_U3.currentIndex())
            transgas = np.exp(-float(thicknessgas) *  xraydb.material_mu(Materialgases,float(Enot)+50))*100
            self.textboxP04.setText('{0:0.1f}'.format(transgas)+ '%')
        if thicknesswall !='':
            thicknesswall = unitconvert(thicknesswall,self.combo_U2.currentIndex())
            transwall = np.exp(-float(thicknesswall) *  xraydb.material_mu(Materialwall,float(Enot)+50))*100
            self.textboxP05.setText('{0:0.1f}'.format(transwall)+ '%')
        if thicknesssolvent !='':
            thicknesssolvent = unitconvert(thicknesssolvent,self.combo_U4.currentIndex())
            transsolvent = np.exp(-float(thicknesssolvent) *  xraydb.material_mu(Materialsolvent,float(Enot)+50))*100
            self.textboxP06.setText('{0:0.1f}'.format(transsolvent)+ '%')
        if thicknessmetal !='':
            thicknessmetal = unitconvert(thicknessmetal,self.combo_U5.currentIndex())
            transmetal = np.exp(-float(thicknessmetal) *  xraydb.material_mu(Materialmetal,float(Enot)+50))*100
            self.textboxP07.setText('{0:0.1f}'.format(transmetal)+ '%')
    
    def Calculateabsbeam_materials(self):
        
        Materialgases = self.combo3.currentText()
        Enot = self.textbox9.text()
        Materialwall = self.combo2.currentText()
        Materialsolvent = self.combo3.currentText()
        Materialmetal = self.combo4.currentText()
        thicknessgas = self.textbox_P02.text()
        thicknesswall = self.textbox_P03.text()
        thicknesssolvent = self.textbox_P04.text()
        thicknessmetal = self.textbox_P05.text()
                
        if thicknessgas !='':
            thicknessgas = unitconvert(thicknessgas,self.combo_U3.currentIndex())
            transgas = np.exp(-float(thicknessgas) *  xraydb.material_mu(Materialgases,float(Enot)+50))*100
            absgas = -np.log(transgas/100)
            self.textboxP04.setText('{0:0.1f}'.format(absgas))
        if thicknesswall !='':
            thicknesswall = unitconvert(thicknesswall,self.combo_U2.currentIndex())
            transwall = np.exp(-float(thicknesswall) *  xraydb.material_mu(Materialwall,float(Enot)+50))*100
            abswall = -np.log(transwall/100)
            self.textboxP05.setText('{0:0.1f}'.format(abswall))
        if thicknesssolvent !='':
            thicknesssolvent = unitconvert(thicknesssolvent,self.combo_U4.currentIndex())
            transsolvent = np.exp(-float(thicknesssolvent) *  xraydb.material_mu(Materialsolvent,float(Enot)+50))*100
            abssolvent = -np.log(transsolvent/100)
            self.textboxP06.setText('{0:0.1f}'.format(abssolvent))
        if thicknessmetal !='':
            thicknessmetal = unitconvert(thicknessmetal,self.combo_U5.currentIndex())
            transmetal = np.exp(-float(thicknessmetal) *  xraydb.material_mu(Materialmetal,float(Enot)+50))*100
            absmetal = -np.log(transmetal/100)
            self.textboxP07.setText('{0:0.1f}'.format(absmetal))
    
    
    def CalBeamabs(self):
        if self.textbox9.text()=='':
            self.textboxP11.setText("Error")
        else:
            ionchamberdensityy = ionchamberdensity(self.slider2.value(),self.combo6.currentText(),self.combo7.currentText(),-self.slider.value()/100)
            Enot = self.textbox9.text()

            if self.combo_C1.currentIndex() == 5:
                self.textboxP12.show()
                if self.textboxP12.text() !='':
                    ionchambergas1 =  -self.slider.value()/100*float(self.textboxP12.text())*xraydb.material_mu(self.combo6.currentText(),float(Enot),density=ionchamberdensityy)
                    ionchambergas2 =  (100+self.slider.value())/100*float(self.textboxP12.text())*xraydb.material_mu(self.combo7.currentText(),float(Enot),density=ionchamberdensityy)
                    transionchamber = np.exp(-(ionchambergas1+ionchambergas2))*100
                    self.textboxP11.setText('{0:0.2f}'.format(100-transionchamber))
          
            else:
                self.textboxP12.hide()
                ionchambergas1 =  -self.slider.value()/100*float(self.combo_C1.currentText())*xraydb.material_mu(self.combo6.currentText(),float(Enot),density=ionchamberdensityy)
                ionchambergas2 =  (100+self.slider.value())/100*float(self.combo_C1.currentText())*xraydb.material_mu(self.combo7.currentText(),float(Enot),density=ionchamberdensityy)
                transionchamber = np.exp(-(ionchambergas1+ionchambergas2))*100
                self.textboxP11.setText('{0:0.2f}'.format(100-transionchamber))
        
            #self.textboxP11.setText('{0:0.2f}'.format(100-transionchamber))
        
        
        #print(MaterialP,trans)
        
        
        
    

  
#########################
##     SECOND VIEW     ##
#########################        

#create a subclss of QMainWindow to set up sample calculator builder GUI
        
class SampleBuilder(QMainWindow):
    def __init__(self, parent = None):
        '''View Initializer'''
        super(SampleBuilder, self).__init__(parent)
        ''' Main Window Properties'''
        self.title = 'Sample Builder'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200

        # Set main window's properties
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        #self.show()
        
        
class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"x wt% Metals on Support")
        self.tabs.addTab(self.tab2,"Supported Metal Complexes")
        
        # Create first tab
        """Define Layout"""
        Tab1Layout = QGridLayout()

        
        """Text Labels"""
        # Create Label for Support Input
        self.label_tab1_01 = QLabel('Support:')
        self.label_tab1_01.setAlignment(Qt.AlignRight)
        Tab1Layout.addWidget(self.label_tab1_01, 0, 0)
        self.tab1.setLayout(Tab1Layout)
                
        # Create Label for Metal Site(s) Definition
        self.label_tab1_02 = QLabel('Metal Site #1 [e.g. Pt, PtO2, Pt1Sn3]:')
        self.label_tab1_02.setAlignment(Qt.AlignRight)
        Tab1Layout.addWidget(self.label_tab1_02, 1, 0)
        self.tab1.setLayout(Tab1Layout)
        
        self.label_tab1_03 = QLabel('Metal Site #1 Loading [wt%]:')
        self.label_tab1_03.setAlignment(Qt.AlignRight)
        Tab1Layout.addWidget(self.label_tab1_03, 2, 0)
        self.tab1.setLayout(Tab1Layout)
        
        self.label_tab1_04 = QLabel('Metal Site #2 [e.g. Pt, PtO2, Pt1Sn3]:')
        self.label_tab1_04.setAlignment(Qt.AlignRight)
        Tab1Layout.addWidget(self.label_tab1_04, 3, 0)
        self.tab1.setLayout(Tab1Layout)
        
        self.label_tab1_05 = QLabel('Metal Site #2 Loading [wt%]:')
        self.label_tab1_05.setAlignment(Qt.AlignRight)
        Tab1Layout.addWidget(self.label_tab1_05, 4, 0)
        self.tab1.setLayout(Tab1Layout)
        
        # Create Label for Notes
        self.label_tab1_06 = QLabel('Note: wt% must reflect the entire metal site.')
        self.label_tab1_06.setAlignment(Qt.AlignLeft)
        Tab1Layout.addWidget(self.label_tab1_06, 7, 0, 1,2)
        self.tab1.setLayout(Tab1Layout)
        
        self.label_tab1_07 = QLabel('Note: Metal Site 2 is an optional field.')
        self.label_tab1_07.setAlignment(Qt.AlignLeft)
        Tab1Layout.addWidget(self.label_tab1_07, 8, 0, 1,2)
        self.tab1.setLayout(Tab1Layout)
        
        
        
        """Input Fields"""
        # Create Text Box for Support Input
        self.textbox_tab101 = QLineEdit()
        self.textbox_tab101.setPlaceholderText('Support Formula')
        self.textbox_tab101.setFixedSize(150, 35)
        self.textbox_tab101.setObjectName("SupportFormula")
        Tab1Layout.addWidget(self.textbox_tab101, 0, 1)
        self.tab1.setLayout(Tab1Layout)
        
        # Create Text Box for Metal Site 1 Formula Imput
        self.textbox_tab102 = QLineEdit()
        self.textbox_tab102.setPlaceholderText('Metal Site 1 Formula')
        self.textbox_tab102.setFixedSize(150, 35)
        Tab1Layout.addWidget(self.textbox_tab102, 1, 1)
        self.tab1.setLayout(Tab1Layout)
        
        # Create Text Box for Metal Site 1 Loading Input
        self.textbox_tab103 = QLineEdit()
        self.textbox_tab103.setPlaceholderText('Metal Site 1 Loading')
        self.textbox_tab103.setFixedSize(150, 35)
        Tab1Layout.addWidget(self.textbox_tab103, 2, 1)
        self.tab1.setLayout(Tab1Layout)
        
        # Create Text Box for Metal Site 2 Formula Input
        self.textbox_tab104 = QLineEdit()
        self.textbox_tab104.setPlaceholderText('Metal Site 2 Formula')
        self.textbox_tab104.setFixedSize(150, 35)
        Tab1Layout.addWidget(self.textbox_tab104, 3, 1)
        self.tab1.setLayout(Tab1Layout)
        
        # Create Text Box for Metal Site 2 Loading Input
        self.textbox_tab105 = QLineEdit()
        self.textbox_tab105.setPlaceholderText('Metal Site 2 Loading')
        self.textbox_tab105.setFixedSize(150, 35)
        Tab1Layout.addWidget(self.textbox_tab105, 4, 1)
        self.tab1.setLayout(Tab1Layout)
        
        # Create Text Box for Feedback
        self.textbox_tab106 = QLineEdit()
        self.textbox_tab106.setPlaceholderText('Diagnostic')
        self.textbox_tab106.setAlignment(Qt.AlignCenter)
        #self.textbox_tab106.setFixedSize(150, 35)
        Tab1Layout.addWidget(self.textbox_tab106, 6, 0, 1, 2)
        self.tab1.setLayout(Tab1Layout)
        #complexsaver
        if samplesaver[1]!= '':
            self.textbox_tab101.setText(samplesaver[1])
            self.textbox_tab102.setText(samplesaver[2])
            self.textbox_tab103.setText(samplesaver[3])
            self.textbox_tab104.setText(samplesaver[4])
            self.textbox_tab105.setText(samplesaver[5])
        
        
        """Buttons"""
        self.button_tab1_01 = QPushButton("Update Sample")
        Tab1Layout.addWidget(self.button_tab1_01, 5, 1)
        self.tab1.setLayout(Tab1Layout)
        self.button_tab1_01.clicked.connect(self.UpdateSampleMetal)
        
        #Create Reset Button to Clear X-ray Input Field
        self.button_tab1_02 = QPushButton('Reset')
        Tab1Layout.addWidget(self.button_tab1_02, 5, 0)
        self.tab1.setLayout(Tab1Layout)
        self.button_tab1_02.clicked.connect(self.clearSampleBuildertab1)
        
                                         
 
        # Create second tab
        """Define Layout"""
        Tab2Layout = QGridLayout()
               
        """Text Labels"""
        # Create Label for Support Input
        self.label_tab2_01 = QLabel('Support:')
        self.label_tab2_01.setAlignment(Qt.AlignRight)
        Tab2Layout.addWidget(self.label_tab2_01, 0, 0)
        self.tab2.setLayout(Tab2Layout)
                
        # Create Label for Metal Complex Definition
        self.label_tab2_02 = QLabel('Metal Complex:')
        self.label_tab2_02.setAlignment(Qt.AlignRight)
        Tab2Layout.addWidget(self.label_tab2_02, 1, 0)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Label for Metal Site Loading - Complex Loading
        self.label_tab2_03 = QLabel('Complex Loading [wt%]:')
        self.label_tab2_03.setAlignment(Qt.AlignRight)
        Tab2Layout.addWidget(self.label_tab2_03, 2, 0)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Label for Metal Site Loading - Metal Loading
        self.label_tab2_04 = QLabel('Metal Loading [wt%]:')
        self.label_tab2_04.setAlignment(Qt.AlignRight)
        Tab2Layout.addWidget(self.label_tab2_04, 3, 0)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Label for Metal Site Loading - Metal Definition
        self.label_tab2_05 = QLabel('Metal Center:')
        self.label_tab2_05.setAlignment(Qt.AlignRight)
        Tab2Layout.addWidget(self.label_tab2_05, 4, 0)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Label for Notes
        self.label_tab2_06 = QLabel('Note: for metal oxides or organometallic complexes')
        self.label_tab2_06.setAlignment(Qt.AlignLeft)
        Tab2Layout.addWidget(self.label_tab2_06, 7, 0, 1,2)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Label for Notes
        self.label_tab2_07 = QLabel('Note: only define complex loading OR metal loading')
        self.label_tab2_07.setAlignment(Qt.AlignLeft)
        Tab2Layout.addWidget(self.label_tab2_07, 8, 0, 1,2)
        self.tab2.setLayout(Tab2Layout)
        
        
        """Input Fields"""
        # Create Text Box for Support Input
        self.textbox_tab2_01 = QLineEdit()
        self.textbox_tab2_01.setPlaceholderText('Support Formula')
        self.textbox_tab2_01.setFixedSize(150, 35)
        Tab2Layout.addWidget(self.textbox_tab2_01, 0, 1)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Text Box for Metal Complex Definition
        self.textbox_tab2_02 = QLineEdit()
        self.textbox_tab2_02.setPlaceholderText('Metal Complex')
        self.textbox_tab2_02.setFixedSize(150, 35)
        Tab2Layout.addWidget(self.textbox_tab2_02, 1, 1)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Text Box for Metal Site Loading - Complex Loading
        self.textbox_tab2_03 = QLineEdit()
        self.textbox_tab2_03.setPlaceholderText('Complex Loading')
        self.textbox_tab2_03.setFixedSize(150, 35)
        Tab2Layout.addWidget(self.textbox_tab2_03, 2, 1)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Text Box for Metal Site Loading - Metal Loading
        self.textbox_tab2_04 = QLineEdit()
        self.textbox_tab2_04.setPlaceholderText('Metal Loading')
        self.textbox_tab2_04.setFixedSize(150, 35)
        Tab2Layout.addWidget(self.textbox_tab2_04, 3, 1)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Text Box for Doagnostic
        self.textbox_tab2_05 = QLineEdit()
        self.textbox_tab2_05.setPlaceholderText('Element')
        self.textbox_tab2_05.setFixedSize(150, 35)
        Tab2Layout.addWidget(self.textbox_tab2_05, 4, 1)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Text Box for Doagnostic
        self.textbox_tab2_06 = QLineEdit()
        self.textbox_tab2_06.setPlaceholderText('Diagnostic')
        self.textbox_tab2_06.setAlignment(Qt.AlignCenter)
        #self.textbox_tab2_06.setFixedSize(150, 35)
        Tab2Layout.addWidget(self.textbox_tab2_06, 6, 0, 1, 2)
        self.tab2.setLayout(Tab2Layout)
        #complexsaver[1]!= '':
        if complexsaver[5]!= '':
            self.textbox_tab2_01.setText(complexsaver[1])
            self.textbox_tab2_02.setText(complexsaver[2])
            self.textbox_tab2_03.setText(complexsaver[3])
            self.textbox_tab2_04.setText(complexsaver[4])
            self.textbox_tab2_05.setText(complexsaver[5])
        
        """Buttons"""
        self.button_tab2_01 = QPushButton("Update Sample")
        Tab2Layout.addWidget(self.button_tab2_01, 5, 1)
        self.tab2.setLayout(Tab2Layout)
        self.button_tab2_01.clicked.connect(self.UpdateSampleComplex)
                
        #Create Reset Button to Clear X-ray Input Field
        self.button_tab2_02 = QPushButton('Reset')
        Tab2Layout.addWidget(self.button_tab2_02, 5, 0)
        self.tab2.setLayout(Tab2Layout)
        self.button_tab2_02.clicked.connect(self.clearSampleBuildertab2)
        
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
    

        
        
       
    def clearSampleBuildertab1(self):
        "Clear the sample builder tab of inputs"
        self.textbox_tab101.clear()
        self.textbox_tab102.clear()
        self.textbox_tab103.clear()
        self.textbox_tab104.clear()
        self.textbox_tab105.clear()
        
    def clearSampleBuildertab2(self):
        "Clear the sample builder tab of inputs"
        self.textbox_tab2_01.clear()
        self.textbox_tab2_02.clear()
        self.textbox_tab2_03.clear()
        self.textbox_tab2_04.clear()
        self.textbox_tab2_05.clear()  
        
    def UpdateSampleMetal(self):
        Support = self.textbox_tab101.text()
        Metal_Site1 = self.textbox_tab102.text()
        Metal1_Loading = self.textbox_tab103.text()
        Metal_Site2 = self.textbox_tab104.text()
        Metal2_Loading = self.textbox_tab105.text()
            
        Result = metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support)
        
        if 'ERROR' in Result:
            self.textbox_tab106.setText(Result) 
        
        else:
            #samplesaver = [None]*6            
            samplesaver[1] = self.textbox_tab101.text()
            samplesaver[2] = self.textbox_tab102.text()
            samplesaver[3] = self.textbox_tab103.text()
            samplesaver[4] = self.textbox_tab104.text()
            samplesaver[5] = self.textbox_tab105.text()
            self.parent().parent().textbox_dil01.setText(Result)
            self.parent().close()


    def UpdateSampleComplex(self):
        #Complex Loading defined, Metal Loading, Element doesnt matter
        if self.textbox_tab2_03.text() != '' and self.textbox_tab2_04.text() == '' :
            Support = self.textbox_tab2_01.text()
            Metal_Site1 = self.textbox_tab2_02.text()
            Metal1_Loading = self.textbox_tab2_03.text()
            Metal_Site2 = ''
            Metal2_Loading = ''
            
            Result = metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support)
            
            if 'ERROR' in Result:
                self.textbox_tab2_06.setText(Result) 
        
            else:
                #complexsaver = [None]*6 
                complexsaver[1] = self.textbox_tab2_01.text()
                complexsaver[2] = self.textbox_tab2_02.text()
                complexsaver[3] = self.textbox_tab2_03.text()
                complexsaver[4] = self.textbox_tab2_04.text()
                complexsaver[5] = self.textbox_tab2_05.text()
                self.parent().parent().textbox_dil01.setText(Result)
                self.parent().close()
        
        
        #Metal Loading defined, Complex Loading not, Element defined
        elif self.textbox_tab2_03.text() == '' and self.textbox_tab2_04.text() != '' and self.textbox_tab2_05.text() != '' :
            Support = self.textbox_tab2_01.text()
            Complex = self.textbox_tab2_02.text()
            Metal_Loading = self.textbox_tab2_04.text()
            Metal_Site = self.textbox_tab2_05.text()
            
            Result = ComplexCalculateSample(Complex, Metal_Loading, Metal_Site, Support)
            
            if 'ERROR' in Result:
                self.textbox_tab2_06.setText(Result) 
        
            else:
                complexsaver[1] = self.textbox_tab2_01.text()
                complexsaver[2] = self.textbox_tab2_02.text()
                complexsaver[3] = self.textbox_tab2_03.text()
                complexsaver[4] = self.textbox_tab2_04.text()
                complexsaver[5] = self.textbox_tab2_05.text()
                self.parent().parent().textbox_dil01.setText(Result)
                self.parent().close()
        
        # Loadings not defined or improperly defined
        else:
            self.textbox_tab2_06.setText('COMPLEX LODAING/METAL LOADING/METAL CENTER INCORRECTLY DEFINED')
            
#########################
##     THIRD VIEW     ##
#########################
class InfoWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        ''' Main Window Properties'''
        self.title = 'CatMass Information'
        self.left = 100
        self.top = 100
        self.width = 640#640
        self.height = 640#480
        InfoWindow.setFixedWidth(self, 900)
        # Set main window's properties
        self.setWindowTitle(self.title)
        layout = QGridLayout()
        
        self.setWindowIcon(QIcon(resource_path('CoACCESSScale_v6')))
        
        
        self.label_Info00 = QLabel('Python Libraries')
        self.label_Info00.setAlignment(Qt.AlignLeft)
        self.label_Info00.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info00, 13, 0, 1, 4)
        self.label_Info00.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info01 = QLabel('xraydb')
        self.label_Info01.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info01, 14, 0)
        self.label_Info01.setWordWrap(True)
        self.setLayout(layout)
        
        
        
        self.label_Info02 = QLabel('xraylib')
        self.label_Info02.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info02, 14, 1)
        self.label_Info02.setWordWrap(True)
        self.setLayout(layout)
        
        
        linkTemplate = '<a href={0}>{1}</a>'
        self.label_Info03 = QLabel()
        self.label_Info03.setText(linkTemplate.format('https://web.slac.stanford.edu/coaccess','Co-ACCESS Information'))
        self.label_Info03.setAlignment(Qt.AlignLeft)
        self.label_Info03.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info03, 0, 0, 1, 4)
        self.label_Info03.setWordWrap(True)
        self.label_Info03.setOpenExternalLinks(True)
        self.setLayout(layout)
        
   
        self.label_Info04 = QLabel()
        self.label_Info04.setText('Co-ACCESS, is supported by the U.S. Department of Energy, Office of Basic Energy Sciences, Chemical Sciences, Geosciences and Biosciences. We thank the SSRL Spectroscopy Staff for providing the'+" " + linkTemplate.format('https://www-ssrl.slac.stanford.edu/smbin/dataextractnew.pl',' crystal glitch library')+'.')
        self.label_Info04.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info04, 1, 0,1,10)
        self.label_Info04.setWordWrap(True)
        self.label_Info04.setOpenExternalLinks(True)
        self.setLayout(layout)
        
        self.label_Info23 = QLabel('Author Information: Jorge E. Perez-Aguilar, Adam S. Hoffman')
        self.label_Info23.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info23, 2, 0,1,10)
        self.label_Info23.setWordWrap(True)
        self.setLayout(layout)
        
        
        
        self.label_Info05 = QLabel('Common Co-ACCESS XAS Cell Information')
        self.label_Info05.setAlignment(Qt.AlignLeft)
        self.label_Info05.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info05, 5, 0, 1, 6)
        self.label_Info05.setWordWrap(True)
        self.setLayout(layout)
        
        
        #link to paper
        self.label_Info06 = QLabel()
        self.label_Info06.setText(linkTemplate.format('https://onlinelibrary.wiley.com/iucr/doi/10.1107/S160057752300615X','CatMass Manuscript'))
        self.label_Info06.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info06, 3, 0,2,6)
        self.label_Info06.setWordWrap(True)
        self.label_Info06.setOpenExternalLinks(True)
        self.setLayout(layout)
        
        self.label_Info21 = QLabel('Wall Thickness [μm]')
        self.label_Info21.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info21, 6, 1,1,2)
        self.label_Info21.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info07 = QLabel('1 mm')
        self.label_Info07.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info07, 8, 0,1,1)
        self.label_Info07.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info08 = QLabel('3 mm')
        self.label_Info08.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info08, 9, 0,1,1)
        self.label_Info08.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info09 = QLabel('Kapton')
        self.label_Info09.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info09, 7, 1,1,1)
        self.setLayout(layout)
        
        self.label_Info10 = QLabel('80')
        self.label_Info10.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info10, 8,1,1,1)
        self.setLayout(layout)
        
        self.label_Info11 = QLabel('87')
        self.label_Info11.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info11, 9,1,1,1)
        self.setLayout(layout)
        
        self.label_Info12 = QLabel('Quartz')
        self.label_Info12.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info12, 7, 2,1,1)
        self.setLayout(layout)
        
        self.label_Info13 = QLabel('10 or 20')
        self.label_Info13.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info13, 8,2,1,1)
        self.setLayout(layout)
        
        self.label_Info14 = QLabel('200')
        self.label_Info14.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info14, 9,2,1,1)
        self.setLayout(layout)
        
        self.label_Info15 = QLabel('Misc')
        self.label_Info15.setAlignment(Qt.AlignLeft)
        self.label_Info15.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info15, 10, 0, 1, 4)
        self.setLayout(layout)
        
        self.label_Info16 = QLabel('Kapton Shield [mils]')
        self.label_Info16.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info16, 11, 0,1,2)
        self.setLayout(layout)
        
        self.label_Info17 = QLabel('2')
        self.label_Info17.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info17, 11, 2,1,2)
        self.setLayout(layout)
        
        self.label_Info18 = QLabel('Mylar [μm]')
        self.label_Info18.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info18, 12, 0,1,2)
        self.setLayout(layout)
        
        self.label_Info19 = QLabel('3.5')
        self.label_Info19.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info19, 12, 2,1,2)
        self.setLayout(layout)
        
        self.label_Info20 = QLabel('Diameter')
        self.label_Info20.setWordWrap(True)
        self.label_Info20.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info20, 7, 0,1,1)
        self.setLayout(layout)
        
        self.label_Info22 = QLabel(self)
        pixmap = QPixmap(resource_path('Workflow.png'))
        #pixmap = QPixmap(os.path.join(os.getcwd(),'src','images','Workflow.png'))'))
        self.label_Info22.setPixmap(pixmap)       
        self.label_Info22.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_Info22, 5, 7,10,1)
        self.setLayout(layout)
        
      
    
    
      
        
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 15:06:18 2021

@author: ashoff
"""

############################
#   Packages and Modules   #
############################

#import numpy as np
import xraylib


##################
#    FUNCTIONS   #
##################


def XASMassCalc(Sample, Element, Edge, Area, AL, gamma = 50 ,delta = 50):
    '''
    

    Parameters
    ----------
    Sample : TYPE
        DESCRIPTION.
    Element : TYPE
        DESCRIPTION.
    Edge : TYPE
        DESCRIPTION.
    Area : TYPE
        DESCRIPTION.
    AL : TYPE, optional
        DESCRIPTION. The default is 2.6.
    delta : TYPE, optional
        DESCRIPTION. The default is 50.

    Returns
    -------
    Error_Statement : TYPE
        DESCRIPTION.
    E0 : TYPE
        DESCRIPTION.
    mass : TYPE
        DESCRIPTION.
    step : TYPE
        DESCRIPTION.

    '''
    
    '''
    Calculates the Edge energy [eV], sample mass [mg] and transmission edge step
    based upon a stoichiometric sample composition, the element and corresponding
    edge to be probed, the perpendicular cross-sectional area of the sample to
    the beam, desired total absorption lenght "delta" eV above the edge.
    
    delta is used to calcualte the absorption coefficient at E0+/-delta to determine
    the edge step

    Parameters
    ----------
    Sample : STR
        Chemcial formula of the sample. parentheses can be used. Numbers of 
        atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Element : STR
        Element in the sample at whihc to caluclate the absorption properties around.
    Edge : STR
        ['K', 'L1', 'L2', 'L3'] used to determine the edge energy of Element.
    Area : FLOAT
        [units = cm^2] cross-sectional area of sample in the X-ray beam. When
        determining sample mass, assume cross-sectional area of entire sample
        area in sample holder is being illuminated.
    AL : FLOAT, optional
        Desired total absorption cross-section of the sample at delta eV above
        the edge. Tthe default is 2.6.
    delta : FLOAT, optional
        Energy [eV] aove the edge energy to calcualte the sampel mass at and energy
        around the edge energy [E0+/- delta] to calcualte the tranmission edge
        step. The default is 50.

    Returns
    -------
    Error_Statement : STR
        Error message to diagnose input failures.
    E0 : FLOAT
        Energy [eV] of the absopriton edge of the Element
    mass : FLOAT
        Mass [mg] calcuated based upon sample composition, energy, area, and total absorption
    step : FLOAT
        Estimated edge step of the element assuming transmission geometry

    '''
    
    ERROR1 = 'ERROR - Sample not Defined'
    ERROR2 = 'ERROR - Element to be Scanned not Defined'
    ERROR3 = 'ERROR - Absorption Length not Defined'
    ERROR4 = 'ERROR - Sample Area not Defined'
    ERROR5 = 'ERROR - Absorption Length not Defined'
    #delta = 50 #eV
    
    delta = delta/1000  #converted to keV forxraylib
    gamma = gamma/1000
    
    Error_Statement = 'None'
    E0 = 0
    mass = 0
    step = 0
    #AL = 0
       

    if Sample == '':
        Error_Statement = ERROR1
        return Error_Statement, E0, mass, step, AL
    
    elif Element == '':
        Error_Statement = ERROR2
        return Error_Statement, E0, mass, step, AL
    
    elif AL == '':
        Error_Statement = ERROR3
        return Error_Statement, E0, mass, step, AL
    
    elif Area == '':
        Error_Statement = ERROR4
        return Error_Statement, E0, mass, step, AL
    elif AL == '':
        Error_Statement = ERROR5
        return Error_Statement, E0, mass, step, AL
    
    else:
    
        #Convert Strings to Floats
        
        
        Al = float(AL)
        
        
        
        
        
        #if Area == '3 mm Capillary':
            #Area = '0.3'
        #elif Area == '1 mm Capillary':
            #Area = '0.1'
        #elif Area == 'Pellet':
            #Area = '0.38'       
        #elif Area == 'Other':
           # Area = Area  
        
        area = float(Area)
        
        #Extract Chemcial Information from Sample
        Elements = xraylib.CompoundParser(Sample)

        #Identify Edge Energy
        if Edge == 'K':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),0)
        elif Edge == 'L1':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),1)
        elif Edge == 'L2':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),2)        
        elif Edge == 'L3':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),3)  
        else:
            E0 = float(Edge)/1000




        if Elements['nElements']>1:
            # Determine Photabsorption Cross Sections for each element at E0 +/- 50 eV
            Photo_XS = []
            for x in range(0,Elements['nElements']):
                if x == 0:
                    Photo_XS = [xraylib.CS_Photo(Elements['Elements'][x], E0-delta), xraylib.CS_Photo(Elements['Elements'][x], E0+gamma)]
                else:
                    newPXS = [xraylib.CS_Photo(Elements['Elements'][x], E0-delta),xraylib.CS_Photo(Elements['Elements'][x], E0+gamma)]
                    Photo_XS = np.vstack((Photo_XS,newPXS)) 

            # Calcualte Mass Weighted Photo Absorption Cross Section:
            mu_tot = []
            for x in range(0,Elements['nElements']):
                if x ==0:
                    mu_tot = np.multiply(Photo_XS[x,:],Elements['massFractions'][x])
                else:
                    new_mu = np.multiply(Photo_XS[x,:],Elements['massFractions'][x])
                    mu_tot = np.vstack((mu_tot, new_mu))
                    
            mu_ave = np.sum(mu_tot, axis = 0)

            # Calculate Sample mass @ E0 + 50 eV and edge step

            mass = Al*area/mu_ave[1]
            E0 = E0*1000

            #step = np.multiply(np.divide(np.multiply(Elements['massFractions'], mass), area), np.subtract(Photo_XS[:,1], Photo_XS[:,0]))
            #step = np.max(step)
            step = np.multiply(np.divide(np.multiply(1, mass), area), np.subtract(mu_ave[1], mu_ave[0]))
            #step2 = mass/area*(mu_ave[1] - mu_ave[0])
            #print(step2)
            #step = np.max(step)
            mass = mass*1000
    
            return Error_Statement, E0, mass, step, mu_ave[1]
    
        else:
            # Determine Photabsorption Cross Sections for element at E0 +/- 50 eV
            Photo_XS = [xraylib.CS_Photo(Elements['Elements'][0], E0-delta), xraylib.CS_Photo(Elements['Elements'][0], E0+gamma)]
        
            # Calculate Sample mass @ E0 + 50 eV and edge step

            mass = Al*area/Photo_XS[1]
            step = (mass/area)*(Photo_XS[1]-Photo_XS[0])
            E0 = E0*1000
            mass = mass*1000
            mu_ave = Photo_XS[1]
            #mu ave should not be vector should be caluculated for single element option...
            return Error_Statement, E0, mass, step, mu_ave
        
def XASPLOTTER(Sample, Element, Edge, Area, AL, gamma ,gamma2,delta = 50):
    #from src import functions as fct
    
    Result2, Enot2, ms2, stp3 ,muave = XASMassCalc(Sample, Element, Edge, Area, AL, gamma, delta = 50)
    
    return muave




def XASStoichCalc(Sample1, Sample2, Sample1_DR, Sample2_DR):
    '''
    Calculates the combined chemical formula for a sample and a diluement given
    a ratio of mass components.

    Parameters
    ----------
    Sample1 : STR
        Chemcial formula of the sample. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Sample2 : STR
        Chemcial formula of the diluent. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Sample1_DR : INT or FLOAT
        Mass of the first sample wiht respect to the second. E.g. if the ratio was
        Sample1:Sample2 = 1:5, Sample1_DR = 1.
    Sample2_DR : INT or FLOAT
        Mass of the second sample wiht respect to the first. E.g. if the ratio was
        Sample1:Sample2 = 1:5, Sample2_DR = 5.


    Returns
    -------
    Error_message : STR
        Error message used to identify problems in the funciton inputs.
    Diluted_Sample_Formula : STR
        Chemical formula of the mixing of two samples givne theri mass dilution ratios
    '''
    ERROR1 = 'ERROR - Sample Not Defined'
    ERROR2 = 'ERROR - Dilution Ratio Not Defined'
    
    Error_message = 'None'
    Diluted_Sample_Formula = ''
    
    if Sample1 == '':
        Error_message = ERROR1
        return Error_message, Diluted_Sample_Formula
    
    elif Sample2 != '' and Sample2_DR == '':
        Error_message = ERROR2
        return Error_message, Diluted_Sample_Formula
    
    elif Sample1 != '' and Sample2 != '' and Sample2_DR != '' and Sample1_DR == '':
        Error_message = ERROR2
        return Error_message, Diluted_Sample_Formula
    
    else:
        
        if Sample2 == '':
            Diluted_Sample_Formula = Sample1
            return Error_message, Diluted_Sample_Formula
            
        else:
            
            if Sample1_DR == '':
                Sample1_dR = 1
            else:
                Sample1_dR = float(Sample1_DR)
            
            Sample2_dR = float(Sample2_DR)
            
            # Parse the compounds
            Sample_Elements = xraylib.CompoundParser(Sample1)

            Diluent_Elements = xraylib.CompoundParser(Sample2)
        
        
            #Calculate New Nass Fractions
            Updated_MF = []
    
            for x in range(0,Sample_Elements['nElements']):
                if x == 0:
                    Updated_MF = [Sample_Elements['Elements'][x], Sample_Elements['massFractions'][x]*Sample1_dR/(Sample1_dR + Sample2_dR)]
                else:
                    new_line = [Sample_Elements['Elements'][x], Sample_Elements['massFractions'][x]*Sample1_dR/(Sample1_dR + Sample2_dR)]    
                    Updated_MF = np.vstack((Updated_MF,new_line))

            if Sample2_dR > 0:
                for x in range(0,Diluent_Elements['nElements']):
                    new_line = [Diluent_Elements['Elements'][x], Diluent_Elements['massFractions'][x]*Sample2_dR/(Sample1_dR + Sample2_dR)]   
                    Updated_MF = np.vstack((Updated_MF,new_line)) 

            #Calcualte Moles of each component
            mol = []
            for x in range(0,np.shape(Updated_MF)[0]):
                if x == 0:
                    mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                else:
                    new_mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                    mol = np.vstack((mol,new_mol))
        
            mol = mol/min(mol)

            #Build New String
            for x in range(0,np.shape(Updated_MF)[0]):
                if x == 0:
                    Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x])) 
                else:
                    new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x]))
                    Sample_String = Sample_String+new_String



            Diluted_Sample = xraylib.CompoundParser(Sample_String)

            #Build Condensed String

            for x in range(0,Diluted_Sample['nElements']):
                if x == 0:
                    Diluted_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Diluted_Sample['Elements'][x])), float(Diluted_Sample['nAtoms'][x])) 
                else:
                    new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Diluted_Sample['Elements'][x])), float(Diluted_Sample['nAtoms'][x]))
                    Diluted_String = Diluted_String+new_String
        
            return Error_message, Diluted_String



def metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support):
    '''
    Calculates the chemical formula of a material consiting of two metal site compositsions,
    weight loadings, and a support.

    Parameters
    ----------
    Metal_Site1 : STR
        Chemcial formula of the metal site on the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Metal1_Loading : INT or FLOAT
        [%] Weight % loading of first metal site.
    Metal_Site2 : STR
        Chemcial formula of a second metal site on the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Metal2_Loading : INT or FLOAT
        [%] Weight % loading of first metal site.
    Support : STR
        Chemcial formula of the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.

    Returns
    -------
    Sample_String : STR
        Chemical ormula of sample defined by support, metal site(s) and loadings.

    '''
    
    ERROR1 = 'ERROR - Metal Site 1 Not Defined'
    ERROR2 = 'ERROR - Metal Site 1 Loading Not Defined'
    ERROR3 = 'ERROR - Metal Loading (Site 2) Not Defined'
    ERROR4 = 'ERROR - Support Not Defined'
    
    if Support == '':
        return ERROR4

    elif Metal_Site1 == '':
        return ERROR1
    
    elif Metal1_Loading == '':
        return ERROR2   
    
    elif Metal_Site2 != '' and Metal2_Loading == '':
            return ERROR3
    
    else:        
        Metal_Loading1 = float(Metal1_Loading)
               
        # Parse metal Site 1 and Support 
        MetalSite1_Elements = xraylib.CompoundParser(Metal_Site1)
        
        Support_Elements = xraylib.CompoundParser(Support)
    
   
        #Calculate New Nass Fractions
        Updated_MF = []
    
        if Metal_Site2 == '':
            #Weight metal site 1 fractions and store them + atomic number
            for x in range(0,MetalSite1_Elements['nElements']):
                if x == 0:
                    Updated_MF = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]
                else:
                    new_line = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]   
                    Updated_MF = np.vstack((Updated_MF,new_line))
                    
            #Add Support Mass Fractions
            for x in range(0,Support_Elements['nElements']):
                new_line = [Support_Elements['Elements'][x], Support_Elements['massFractions'][x]*(1-(Metal_Loading1)/100)]   
                Updated_MF = np.vstack((Updated_MF,new_line))
        
        else:
            #Weight metal site 1 fractions and store them + atomic number      
            for x in range(0,MetalSite1_Elements['nElements']):
                if x == 0:
                    Updated_MF = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]
                else:
                    new_line = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]   
                    Updated_MF = np.vstack((Updated_MF,new_line))
        
            #Weight metal site 2 fractions and store them + atomic number      
            MetalSite2_Elements = xraylib.CompoundParser(Metal_Site2)
            Metal_Loading2 = float(Metal2_Loading)
            for x in range(0,MetalSite2_Elements['nElements']):
                new_line = [MetalSite2_Elements['Elements'][x], MetalSite2_Elements['massFractions'][x]*Metal_Loading2/100]   
                Updated_MF = np.vstack((Updated_MF,new_line))
                
            #Add Support Mass Fractions
            for x in range(0,Support_Elements['nElements']):
                new_line = [Support_Elements['Elements'][x], Support_Elements['massFractions'][x]*(1-(Metal_Loading1+Metal_Loading2)/100)]   
                Updated_MF = np.vstack((Updated_MF,new_line))
    
        
        #Calcualte Moles of each component
        mol = []
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
            else:
                new_mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                mol = np.vstack((mol,new_mol))
        
        mol = mol/min(mol)

       
        #Build New String
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x]))
                Sample_String = Sample_String+new_String

        Constructed_Sample = xraylib.CompoundParser(Sample_String)

        
        #Build Condensed String
        for x in range(0,Constructed_Sample['nElements']):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x]))
                Sample_String = Sample_String+new_String
        
        return Sample_String


def ComplexCalculateSample(Complex, Metal_Loading, Metal_Site, Support):
    '''
    Calculate the stoichiometry of a supported complex catalyst based upon the complex,
    its loading, or the metal center and its loading, and the support

    Parameters
    ----------
    Complex : STR
        Chemcial formula of the metal site on the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Metal_Loading : INT or FLOAT
        [%] Weight % loading of first metal site.
    Metal_Site : STR
        Element in the complex
    Support : STR
        Chemcial formula of the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.

    Returns
    -------
    Sample_String : STR
        Chemical ormula of sample defined by support, metal site(s) and loadings.

    '''
               
    ERROR1 = 'ERROR - Metal Complex Not Defined'
    ERROR2 = 'ERROR - Metal Loading Not Defined'
    ERROR3 = 'ERROR - Metal Center not in Complex'
    ERROR4 = 'ERROR - Support Not Defined'
    
    if Support == '':
        return ERROR4

    elif Complex == '':
        return ERROR1
    
    elif Metal_Loading == '':
        return ERROR2
    
    elif Metal_Site in Complex:
        metal_Loading = float(Metal_Loading)
               
        # Parse metal Site 1 and Support 
        MetalSite_Elements = xraylib.CompoundParser(Complex)
        
        Support_Elements = xraylib.CompoundParser(Support)
    
   
        #Calculate New Nass Fractions
        Updated_MF = []
        
        #Find Metal Site in Complex
        ind = MetalSite_Elements['Elements'].index(xraylib.SymbolToAtomicNumber(Metal_Site))
        wt_Factor = metal_Loading/MetalSite_Elements['massFractions'][ind]
        
        #Weight metal site 1 fractions and store them + atomic number      
        for x in range(0,MetalSite_Elements['nElements']):
            if x == 0:
                Updated_MF = [MetalSite_Elements['Elements'][x], MetalSite_Elements['massFractions'][x]*wt_Factor/100]
            else:
                new_line = [MetalSite_Elements['Elements'][x], MetalSite_Elements['massFractions'][x]*wt_Factor/100]   
                Updated_MF = np.vstack((Updated_MF,new_line))
        
        complex_MF = np.sum(Updated_MF[:,1])
        
        #Add Support Mass Fractions
        for x in range(0,Support_Elements['nElements']):
            new_line = [Support_Elements['Elements'][x], Support_Elements['massFractions'][x]*(1-complex_MF)]   
            Updated_MF = np.vstack((Updated_MF,new_line))
    
        
        #Calcualte Moles of each component
        mol = []
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
            else:
                new_mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                mol = np.vstack((mol,new_mol))
        
        mol = mol/min(mol)

       
        #Build New String
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x]))
                Sample_String = Sample_String+new_String

        Constructed_Sample = xraylib.CompoundParser(Sample_String)

        
        #Build Condensed String
        for x in range(0,Constructed_Sample['nElements']):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x]))
                Sample_String = Sample_String+new_String
        
        return Sample_String
    
    else:
        return ERROR3
    

def kspacecalc(EminusEnot):
        import math
        kfromE = math.sqrt((8*math.pi**2*9.10938291*10**-31)/(6.6260695729*10**-34*4.13566751691*10**-15)*(EminusEnot))*1/(10**10)
        
        return kfromE


def BeamTrans(Sample):
    Sample_Elements = xraylib.CompoundParser(Sample)
    #new_mu = np.multiply(Photo_XS[x,:],Elements['massFractions'][x])
    #mu_tot = np.vstack((mu_tot, new_mu))
    densities =[]
    
    for i in range(0,Sample_Elements['nElements']):
        atomicnumber = Sample_Elements['Elements'][i]
        density = xraylib.ElementDensity(atomicnumber)
        densityfrac = density*Sample_Elements['massFractions'][i]
        densities = np.append(densities,density)
    #sample_density = np.sum(densities) 
    
    return Sample_Elements,densityfrac,densities

def XASEZero(Sample,Enot):
    

    Elements = xraylib.CompoundParser(Sample)
    y = ['K','L1','L2','L3'] # add the other edges if need to y vector
    atomicnumbers=[]
    atomicsymbols=[]
    atomicedges=[]
    atomicedgesymbols=[]
    kspaceedges = []
    k = 0
    
    for i in range(0,Elements['nElements']):
        atomicnumber = Elements['Elements'][i]
        atomicsymbol = xraylib.AtomicNumberToSymbol(atomicnumber)
        for j in range(len(y)):
            try:
                atomicedge = xraylib.EdgeEnergy(atomicnumber,j)*1000-Enot
            except:
                pass
                atomicedge = 0
            
            if atomicedge <=0:
                k = k
            else:
                #kspaceedge = math.sqrt((8*math.pi**2*9.10938291*10**-31)/(6.6260695729*10**-34*4.13566751691*10**-15)*(atomicedge))*1/(10**10)
                kspaceedge = kspacecalc(atomicedge)
                kspaceedges= np.append(kspaceedges, kspaceedge)
                atomicedges = np.append(atomicedges, atomicedge+Enot)
                atomicsymbols = np.append(atomicsymbols, atomicsymbol)
                atomicnumbers = np.append(atomicnumbers, atomicnumber)
                atomicedgesymbols = np.append(atomicedgesymbols, y[j])
            
    
    return kspaceedges, atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols
    
def XASEZeroList(Sample):
    

    Elements = xraylib.CompoundParser(Sample)
    y = ['K','L1','L2','L3'] # add the other edges if need to y vector
    atomicnumbers=[]
    atomicsymbols=[]
    atomicedges=[]
    atomicedgesymbols=[]
    k = 0
    
    for i in range(0,Elements['nElements']):
        atomicnumber = Elements['Elements'][i]
        atomicsymbol = xraylib.AtomicNumberToSymbol(atomicnumber)
        for j in range(len(y)):
            try:
                if xraylib.EdgeEnergy(atomicnumber,j)*1000-100 <=0 or xraylib.EdgeEnergy(atomicnumber,j)*1000 <=200:
                    k = k
                else:
                    atomicedge = xraylib.EdgeEnergy(atomicnumber,j)*1000
                    atomicedges = np.append(atomicedges, atomicedge)
                    atomicsymbols = np.append(atomicsymbols, atomicsymbol)
                    atomicnumbers = np.append(atomicnumbers, atomicnumber)
                    atomicedgesymbols = np.append(atomicedgesymbols, y[j])
            except:
                pass
            
    
    return atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols

def unitconvert(thickness,Cindex):
    if Cindex == 0 :
        thickness = float(thickness)*2.54
           
    elif Cindex == 1 :
        thickness = float(thickness)*0.00254
           
    elif Cindex == 2 :
        thickness = float(thickness)
            
    elif Cindex == 3 :
        thickness = float(thickness)*0.1
            
    elif Cindex == 4 :
        thickness = float(thickness)*0.0001
        
    return thickness

#import xraydb
def ionchamberdensity(Ptotal,gas1,gas2,molfrac):
    
    formula1,elementdensity1 = xraydb.get_material(gas1)
    formula2,elementdensity2 = xraydb.get_material(gas2)
    densitymix = molfrac*elementdensity1+(1-molfrac)*elementdensity2
    iondensity = Ptotal*densitymix/760
    return iondensity
    
    
   
    
          
        
###################
#                 #
#    MAIN LOOP    #
#                 #
###################        
    
if __name__ == "__main__":

    def run_app():
        #global fontsize
        # Create an instance of `QApplication`
        #app = QApplication(sys.argv)
        # Show the calculator's GUI
        
        
        mainWin = XASCalcUI()
        
        
        mainWin.cursor()
        mainWin.setStyleSheet(''' font-size: '''+str(fontsize)+'''px; ''')
        mainWin.saveState()
        mainWin.show()
        app.exec_()
    run_app()