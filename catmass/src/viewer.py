# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 22:18:20 2021

@author: ashoff

Version updated by jperezag
"""


import sys

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QAction
#from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QGridLayout

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QSlider

#from tkinter import *
#from tkinter.filedialog import asksaveasfile
from PyQt5.QtWidgets import QFileDialog

#from pathlib import Path

from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QRadioButton,QCheckBox

import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.widgets import Button, RadioButtons, CheckButtons
from PyQt5.QtGui import QPixmap

import xraydb

### How do I call this?
from src import functions as fct

#######################
##     MAIN VIEW     ##
#######################

#Matrix to save values
saver= [None] *55
saverlabel = [None]*55

samplesaver = [None]*6
complexsaver = [None]*6
#savers = np.empty((19, 5))

ksavingcounter = 0


SampleDilutionBlockWidth = 450
XrayInputBlockWidth = 360
XrayInputBlockHight = 590
XrayInputBlockHight2= XrayInputBlockHight+20
ResultsBlockWidth = 320
PropertiesBlockWidth = 370+50+20

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
        self.width = 480#640
        self.height = 640#480
        
        # Set main window's properties
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        XASCalcUI.setFixedHeight(self, XrayInputBlockHight+50)
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

        #self._centralWidget.setStyleSheet("background-color:rgb(176,196,222)")
        #self._centralWidget.setStyleSheet("background-color:rgb(192,192,192)")
       #"background-color:rgb(255,255,255)"
       
       
        # Create menu bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        #editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        #searchMenu = mainMenu.addMenu('Search')
        #toolsMenu = mainMenu.addMenu('Tools')
        #helpMenu = mainMenu.addMenu('Help')
        
        #add a open text file that is a previes saved sample mass calculation
        OpenAction = QAction(QIcon('open24.png'),'Open File', self)
        fileMenu.addAction(OpenAction)
        OpenAction.triggered.connect(self.opencatfile)
        OpenAction.triggered.connect(self.PreviousSave)
        
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
        viewMenu.addAction(OpenAction)
        OpenAction.triggered.connect(self.openInfo)
        
        OpenAction = QAction(QIcon('ResetValues24.png'),'Reset Values', self)
        viewMenu.addAction(OpenAction)
        OpenAction.triggered.connect(self.Resetall)
    
        
        
    def _createPropertiesBlock(self)    :
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
            self.label_P00 = QLabel('X-ray Properties Of Materials')
            self.label_P00.setAlignment(Qt.AlignLeft)
            self.label_P00.setStyleSheet("font-weight: bold; text-decoration: underline")
            PropertiesLayout.addWidget(self.label_P00, 0, 0, 1, 3)
            self.label_P00.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.label_P08 = QLabel('Ion Chamber Gases')
            self.label_P08.setAlignment(Qt.AlignLeft)
            self.label_P08.setStyleSheet("font-weight: bold; text-decoration: underline")
            PropertiesLayout.addWidget(self.label_P08, 7, 0, 1, 3)
            self.label_P08.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
    
        
        
            # Create Common gases Label
            self.label_P01 = QLabel('Common Gases')
            self.label_P01.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.label_P01, 1, 0)
            self.label_P01.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create common materials Label
            self.label_P02 = QLabel('Common Materials')
            self.label_P02.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.label_P02, 2, 0)
            self.label_P02.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create "units header Label
            #self.label_P03 = QLabel('[cm]')
            #self.label_P03.setAlignment(Qt.AlignCenter)
            #PropertiesLayout.addWidget(self.label_P03, 0, 2)
            #self.label_P03.setWordWrap(True)
            #self.generalLayout.addLayout(PropertiesLayout)
        
            # Creat "Dummy" label for shifting textboxes up label
            self.label_P04 = QLabel(self)
            #self.label_P04.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.label_P04, 15, 0,14,3)
            #self.label_dil06.setStyleSheet("background-color:rgb(0,0,0)")
            #self.label_dil06.resize(0.5, 1)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create unit header" Label
            self.label_P05 = QLabel('%')
            self.label_P05.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.label_P05, 0, 4)
            self.label_P05.setWordWrap(True)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create solvent materials Label
            self.label_P06 = QLabel('Common Solvents')
            self.label_P06.setAlignment(Qt.AlignCenter)
            self.label_P06.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P06, 3, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create solvent materials Label
            self.label_P07 = QLabel('Common Metals')
            self.label_P07.setAlignment(Qt.AlignCenter)
            self.label_P07.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P07, 4, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create pressure label for ion chambers
            self.label_P09 = QLabel('Total Pressure')
            self.label_P09.setAlignment(Qt.AlignCenter)
            self.label_P09.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P09, 10, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create label for chabmer length
            self.label_P10 = QLabel("Ion Chamber Length [cm]")
            self.label_P10.setAlignment(Qt.AlignCenter)
            self.label_P10.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P10, 11, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create label for chabmer length
            self.label_P11 = QLabel("% Beam Absorbed")
            self.label_P11.setAlignment(Qt.AlignCenter)
            self.label_P11.setWordWrap(True)
            PropertiesLayout.addWidget(self.label_P11, 11, 3)
            self.generalLayout.addLayout(PropertiesLayout)
        
        
        
            """Input Fields"""
        
            # Create Text Box for thickness of material
            self.textbox_P02 = QLineEdit()
            self.textbox_P02.setPlaceholderText('Thickness')
            self.textbox_P02.setFixedSize(65, 35)
            PropertiesLayout.addWidget(self.textbox_P02, 1, 2)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Text Box for thickness of material
            self.textbox_P03 = QLineEdit()
            self.textbox_P03.setPlaceholderText('Thickness')
            self.textbox_P03.setFixedSize(65, 35)
            PropertiesLayout.addWidget(self.textbox_P03, 2, 2)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Text Box for thickness of solvent
            self.textbox_P04 = QLineEdit()
            self.textbox_P04.setPlaceholderText('Thickness')
            self.textbox_P04.setFixedSize(65, 35)
            PropertiesLayout.addWidget(self.textbox_P04, 3, 2)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Text Box for thickness of metal
            self.textbox_P05 = QLineEdit()
            self.textbox_P05.setPlaceholderText('Thickness')
            self.textbox_P05.setFixedSize(65, 35)
            PropertiesLayout.addWidget(self.textbox_P05, 4, 2)
            self.generalLayout.addLayout(PropertiesLayout)
            
            
        
        
            # Create Combobox (dropdown) in main window for materials
            self.combo2 = QComboBox()
            for name, m in xraydb.get_materials(categories=['ceramic','polymer']).items():
                self.combo2.addItem(name)
            self.combo2.setFixedSize(150, 35)
            PropertiesLayout.addWidget(self.combo2, 2, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U2 = QComboBox()
            self.combo_U2.addItem('in')
            self.combo_U2.addItem('mils')
            self.combo_U2.addItem('cm')
            self.combo_U2.addItem('mm')
            self.combo_U2.addItem('μm')
            self.combo_U2.setFixedSize(50, 35)
            self.combo_U2.setCurrentIndex(4)
            PropertiesLayout.addWidget(self.combo_U2, 2, 3)
            self.generalLayout.addLayout(PropertiesLayout)
        
        
            # Create Combobox (dropdown) in main window for materials
            self.combo3 = QComboBox()
            for name, m in xraydb.get_materials(categories='gas').items():
                self.combo3.addItem(name)
            self.combo3.setCurrentIndex(8)
            self.combo3.setFixedSize(150, 35)
            PropertiesLayout.addWidget(self.combo3, 1, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U3 = QComboBox()
            self.combo_U3.addItem('in')
            self.combo_U3.addItem('mils')
            self.combo_U3.addItem('cm')
            self.combo_U3.addItem('mm')
            self.combo_U3.addItem('μm')
            self.combo_U3.setFixedSize(50, 35)
            self.combo_U3.setCurrentIndex(2)
            PropertiesLayout.addWidget(self.combo_U3, 1, 3)
            self.generalLayout.addLayout(PropertiesLayout)
        
        
            # Create Combobox (dropdown) in main window for materials
            self.combo4 = QComboBox()
            for name, m in xraydb.get_materials(categories='solvent').items():
                self.combo4.addItem(name)
            self.combo4.setCurrentIndex(0)
            self.combo4.setFixedSize(150, 35)
            PropertiesLayout.addWidget(self.combo4, 3, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U4 = QComboBox()
            self.combo_U4.addItem('in')
            self.combo_U4.addItem('mils')
            self.combo_U4.addItem('cm')
            self.combo_U4.addItem('mm')
            self.combo_U4.addItem('μm')
            self.combo_U4.setFixedSize(50, 35)
            self.combo_U4.setCurrentIndex(2)
            PropertiesLayout.addWidget(self.combo_U4, 3, 3)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Combobox (dropdown) in main window for materials
            self.combo5 = QComboBox()
            for name, m in xraydb.get_materials(categories='metal').items():
                self.combo5.addItem(name)
            self.combo5.setCurrentIndex(2)
            self.combo5.setFixedSize(150, 35)
            PropertiesLayout.addWidget(self.combo5, 4, 1)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.combo_U5 = QComboBox()
            self.combo_U5.addItem('in')
            self.combo_U5.addItem('mils')
            self.combo_U5.addItem('cm')
            self.combo_U5.addItem('mm')
            self.combo_U5.addItem('μm')
            self.combo_U5.setFixedSize(50, 35)
            self.combo_U5.setCurrentIndex(1)
            PropertiesLayout.addWidget(self.combo_U5, 4, 3)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            self.textboxP04 = QLineEdit()
            self.textboxP04.setFixedSize(50, 35)
            self.textboxP04.setAlignment(Qt.AlignRight)
            self.textboxP04.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP04, 1, 4)
            self.generalLayout.addLayout(PropertiesLayout)
        
            # Create Editable Textbox for result %trans
            self.textboxP05 = QLineEdit()
            self.textboxP05.setFixedSize(50, 35)
            self.textboxP05.setAlignment(Qt.AlignRight)
            self.textboxP05.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP05, 2, 4)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            self.textboxP06 = QLineEdit()
            self.textboxP06.setFixedSize(50, 35)
            self.textboxP06.setAlignment(Qt.AlignRight)
            self.textboxP06.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP06, 3, 4)
            self.generalLayout.addLayout(PropertiesLayout)
            
            # Create Editable Textbox for result %trans
            self.textboxP07 = QLineEdit()
            self.textboxP07.setFixedSize(50, 35)
            self.textboxP07.setAlignment(Qt.AlignRight)
            self.textboxP07.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP07, 4, 4)
            self.generalLayout.addLayout(PropertiesLayout)
            
            
            # Create Combobox for ionchamber gas 1
            self.combo6 = QComboBox()
            self.combo6.setEditable(True)
            line_edit = self.combo6.lineEdit()
            for name, m in xraydb.get_materials(categories='gas').items():
                self.combo6.addItem(name)
            self.combo6.setCurrentIndex(1)
            self.combo6.setFixedSize(120, 35)
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
            self.combo7.setFixedSize(120, 35)
            PropertiesLayout.addWidget(self.combo7, 8, 3,1,2)
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
            self.combo_C1.setFixedSize(60, 35)
            self.combo_C1.setCurrentIndex(1)
            PropertiesLayout.addWidget(self.combo_C1, 11, 2,Qt.AlignCenter)
            self.generalLayout.addLayout(PropertiesLayout)
            self.combo_C1.currentTextChanged.connect(self.CalBeamabs)
        
            """Buttons"""
            # Create Button to Open Sample Builder
            self.button_P00 = QPushButton('Percent Beam Transmitted')
            PropertiesLayout.addWidget(self.button_P00, 6, 0,1,5)
            self.generalLayout.addLayout(PropertiesLayout)
            self.button_P00.clicked.connect(self.Calculatetransbeam)
            
            # Create Button to Open Sample Builder
            self.button_P00 = QPushButton('Reset')
            PropertiesLayout.addWidget(self.button_P00, 15, 0,1,5)
            self.generalLayout.addLayout(PropertiesLayout)
            self.button_P00.clicked.connect(self.clearxrayprop)
            
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
            self.textboxP08.setFixedSize(60, 35)
            self.textboxP08.setAlignment(Qt.AlignRight)
            self.textboxP08.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP08, 9, 0)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP08.setText('{0:0.0f}'.format(-self.slider.value())+' %')
            
            self.textboxP09 = QLineEdit()
            self.textboxP09.setFixedSize(60, 35)
            self.textboxP09.setAlignment(Qt.AlignLeft)
            self.textboxP09.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP09, 9, 4,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP09.setText('{0:0.0f}'.format(100+self.slider.value())+' %')
            
            self.textboxP10 = QLineEdit()
            self.textboxP10.setFixedSize(60, 35)
            self.textboxP10.setAlignment(Qt.AlignLeft)
            self.textboxP10.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP10, 10, 4,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP10.setText('{0:0.0f}'.format(round(self.slider2.value(),-1))+' torr')
            
            self.textboxP11 = QLineEdit()
            self.textboxP11.setFixedSize(60, 35)
            self.textboxP11.setAlignment(Qt.AlignCenter)
            self.textboxP11.setReadOnly(True)
            PropertiesLayout.addWidget(self.textboxP11, 11, 4,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            
            self.textboxP12 = QLineEdit()
            self.textboxP12.setFixedSize(60, 35)
            self.textboxP12.setAlignment(Qt.AlignCenter)
            PropertiesLayout.addWidget(self.textboxP12, 11, 0,Qt.AlignRight)
            self.generalLayout.addLayout(PropertiesLayout)
            self.textboxP12.setText('0')
            self.textboxP12.hide()
            self.textboxP12.textEdited.connect(self.CalBeamabs)
           
            #if self.combo_C1.currentIndex() == 5:
                #self.textboxP12.textChanged.connect(self.CalBeamabs)
                
            
            
            
    
    def valuechange(self):
        #size = self.slider.value()
        self.textboxP08.setText('{0:0.0f}'.format(-self.slider.value())+' %')
        self.textboxP09.setText('{0:0.0f}'.format(100+self.slider.value())+' %')
    
    def valuechange2(self):
        #size = self.slider.value()
        self.textboxP10.setText('{0:0.0f}'.format(round(self.slider2.value(),-1))+' torr')
        
        
    
    def _createSampleDilutionBlock(self)    :
        '''Define QFrame'''
        Diluent_frame = QFrame()
        Diluent_frame.setFrameShape(QFrame.StyledPanel)
        Diluent_frame.setLineWidth(1)
                
        self.generalLayout.addWidget(Diluent_frame)
        Diluent_frame.setFixedWidth(SampleDilutionBlockWidth)
        
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
        
        # Creat "Dummy" label fo Co-ACCESS label
        self.label_dil06 = QLabel(self)
        self.label_dil06.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil06, 7, 0,14,3)
        #self.label_dil06.setStyleSheet("background-color:rgb(0,0,0)")
        #self.label_dil06.resize(0.5, 1)
        self.generalLayout.addLayout(DilutionLayout)
       
         
        
        self.label_dil05 = QLabel(self)
        pixmap = QPixmap('co_access_logo_text.png')
        self.label_dil05.setPixmap(pixmap)
        self.label_dil05.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil05, 10, 0,7,3)
        self.label_dil05.resize(0.5, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        
        """Input Fields"""
        # Create Text Box for Sample Formula
        self.textbox_dil01 = QLineEdit()
        self.textbox_dil01.setPlaceholderText('Chemical Formula')
        self.textbox_dil01.setFixedSize(150, 35)
        DilutionLayout.addWidget(self.textbox_dil01, 3, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Diluent Formula
        self.textbox_dil02 = QLineEdit()
        self.textbox_dil02.setPlaceholderText('Chemical Formula')
        self.textbox_dil02.setFixedSize(150, 35)
        DilutionLayout.addWidget(self.textbox_dil02, 3, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Sample Dilution Fraction
        self.textbox_dil03 = QLineEdit()
        self.textbox_dil03.setPlaceholderText('#')
        self.textbox_dil03.setAlignment(Qt.AlignCenter)
        self.textbox_dil03.setFixedSize(75, 35)
        DilutionLayout.addWidget(self.textbox_dil03, 4, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Diluent Dilution Fraction
        self.textbox_dil04 = QLineEdit()
        self.textbox_dil04.setPlaceholderText('#')
        self.textbox_dil04.setAlignment(Qt.AlignCenter)
        self.textbox_dil04.setFixedSize(75, 35)
        DilutionLayout.addWidget(self.textbox_dil04, 4, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        
        # Create Text Box for File path of openned file
        self.textbox_dil06 = QLineEdit()
        self.textbox_dil06.setPlaceholderText('File Path')
        self.textbox_dil06.setAlignment(Qt.AlignCenter)
        #self.textbox_dil05.setFixedSize(150, 35)
        self.textbox_dil06.setReadOnly(True)
        DilutionLayout.addWidget(self.textbox_dil06, 6, 0, 1,3)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Diagnostics
        self.textbox_dil05 = QLineEdit()
        self.textbox_dil05.setPlaceholderText('Diagnostic')
        self.textbox_dil05.setAlignment(Qt.AlignCenter)
        #self.textbox_dil05.setFixedSize(150, 35)
        DilutionLayout.addWidget(self.textbox_dil05, 7, 0, 1,3)
        self.generalLayout.addLayout(DilutionLayout)
        
        
        
        
        
        """Buttons"""
        # Create Button to Open Sample Builder
        self.button_dil00 = QPushButton('Sample Builder')
        DilutionLayout.addWidget(self.button_dil00, 1, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil00.clicked.connect(self.openSampleBuilder)
        
        # Create Button to Import Previous save
        #self.button_dil03 = QPushButton('Import Previous Save')
        #DilutionLayout.addWidget(self.button_dil03, 1, 1)
        #self.generalLayout.addLayout(DilutionLayout)
        #self.button_dil03.clicked.connect(self.updatecountmin)
        #self.button_dil03.clicked.connect(self.PreviousSave)
        
       
        
        
        # Create Button to Reset all Text Fields
        self.button_dil01 = QPushButton('Reset')
        DilutionLayout.addWidget(self.button_dil01, 5, 0)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil01.clicked.connect(self.clearDilutionInput)
        
        # Create Button to Calculate Diluted Sample Chemical Formula 
        self.button_dil02 = QPushButton('Calculate Diluted Sample Chemical Formula')
        DilutionLayout.addWidget(self.button_dil02, 5, 1, 1, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil02.clicked.connect(self.calculateSampleComp)
        
        
        
        
        
        
    def _createXrayInputBlock(self):
        '''Define QFrame'''
        global XrayInputFrame
        XrayInputFrame = QFrame()
        XrayInputFrame.setFrameShape(QFrame.StyledPanel)
        XrayInputFrame.setLineWidth(1)
                
        self.generalLayout.addWidget(XrayInputFrame)
        
        """Define Layout"""
        InputLayout = QGridLayout()
        XrayInputFrame.setLayout(InputLayout)
        XrayInputFrame.setFixedWidth(XrayInputBlockWidth)
        
        XrayInputFrame.setFixedHeight(XrayInputBlockHight)
        
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
        InputLayout.addWidget(self.label1, 1, 0)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Label for Element of Interest
        self.label2 = QLabel('Element to be Scanned:')
        self.label2.setAlignment(Qt.AlignRight)
        InputLayout.addWidget(self.label2, 2, 0)
        self.generalLayout.addLayout(InputLayout)
        
        #Create Label for Element of Interest
        self.label3 = QLabel('Edge to be Scanned:')
        self.label3.setAlignment(Qt.AlignRight)
        InputLayout.addWidget(self.label3, 3, 0)
        self.generalLayout.addLayout(InputLayout)
        
        #Create Label for edge to be scanned
        self.label12 = QLabel('Energy to Calculate Sample Mass [eV]:')
        self.label12.setAlignment(Qt.AlignRight)
        InputLayout.addWidget(self.label12, 4, 0)
        self.label12.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        self.label12.hide()
        
        
        # Create Lable for Desired Absorption Length
        self.label4 = QLabel('Total Sample Absorption at E0 + 50 eV:')
        self.label4.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label4, 6, 0)
        self.label4.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        self.label6 = QLabel('Sample Area Perpendicular')
        self.label6.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label6, 7, 0)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        self.label7 = QLabel('to Beam of Co-ACCESS')
        self.label7.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label7, 8, 0)
        self.generalLayout.addLayout(InputLayout)
        # Create Lable for Co-ACCESS default cell Area
        self.label8 = QLabel('Capillaries:')
        self.label8.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label8, 9, 0)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for bed legnth
        self.label11 = QLabel('Bed length [1 cm]')
        self.label11.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label11, 10, 0)
        self.generalLayout.addLayout(InputLayout)
        
        
        # Create Lable for Desired Area
        self.label5 = QLabel('Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
        self.label5.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label5, 11, 0)
        self.label5.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        
        
        
        # Create Lable for plot lower limit
        self.label9 = QLabel('Lower Limit of μ Average Plot')
        self.label9.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label9, 12, 0)
        self.generalLayout.addLayout(InputLayout)
        # Create Lable for plot upper limit
        self.label10 = QLabel('Upper Limit of μ Average Plot')
        self.label10.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label10, 13, 0)
        self.generalLayout.addLayout(InputLayout)
        
        
        
        
        """Input Fields"""
        
        # Create Editable Textbox for Sample Stoichiometry
        self.textbox1 = QLineEdit()
        self.textbox1.setPlaceholderText('Defined Above')
        self.textbox1.setStyleSheet("background-color:rgb(224,224,224)")
        self.textbox1.setReadOnly(True)
        self.textbox1.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox1, 1, 1)
        self.generalLayout.addLayout(InputLayout)

        # Create Editable Textbox for Element to be Scanned
        self.textbox2 = QLineEdit()
        self.textbox2.setPlaceholderText('Element Symbol')
        self.textbox2.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox2, 2, 1)
        self.generalLayout.addLayout(InputLayout)

        # Create Combobox (dropdown) in main window for Edge to Scan
        self.combo = QComboBox()
        self.combo.addItem('K')
        self.combo.addItem('L1')
        self.combo.addItem('L2')
        self.combo.addItem('L3')
        self.combo.addItem('Other')        
        self.combo.setFixedSize(150, 35)
        InputLayout.addWidget(self.combo, 3, 1)
        self.generalLayout.addLayout(InputLayout)
        self.combo.currentTextChanged.connect(self.on_combobox_changed)
        
        self.textbox14 = QLineEdit()
        self.textbox14.setPlaceholderText('Energy')
        self.textbox14.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox14, 4, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox14.hide()
        
        
        #checkbox to show results with cell at 45 degrees
        self.b2 = QCheckBox()
        InputLayout.addWidget(self.b2, 5, 1)
        #self.b1.setAlignment(Qt.AlignCenter)
        self.b2.setText("Sample at 45°")
        self.b2.toggled.connect(self.b1_function)
 
        
        # Create Editable Textbox for Desired Absorption Length
        self.textbox3 = QLineEdit()
        self.textbox3.setPlaceholderText('Target Absorption Length')
        self.textbox3.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox3, 6, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox3.setText('2.5')
        
        
        # Radio button for Capillaries
        self.radioButton1 = QRadioButton(self)
        InputLayout.addWidget(self.radioButton1, 7, 1)
        self.radioButton2 = QRadioButton()
        InputLayout.addWidget(self.radioButton2, 8, 1)
        self.radioButton3 = QRadioButton()
        InputLayout.addWidget(self.radioButton3, 9, 1)
        #self.radioButton4 = QRadioButton()
        #InputLayout.addWidget(self.radioButton4, 5, 5)
        self.radioButton1.setText("3 mm Capillary")
        self.radioButton2.setText("1 mm Capillary")
        self.radioButton3.setText("7 mm Pellet")
        self.radioButton1.toggled.connect(self.radioButton1_function) 
        self.radioButton2.toggled.connect(self.radioButton2_function) 
        self.radioButton3.toggled.connect(self.radioButton3_function)
        
        # Create Editable Textbox bed length
        self.textbox13 = QLineEdit()
        self.textbox13.setPlaceholderText('1')
        self.textbox13.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox13, 10, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox13.setText('1')
        
     
                   
        # Create Editable Textbox for Desired Area
        self.textbox4 = QLineEdit()
        self.textbox4.setPlaceholderText('Sample Area')
        self.textbox4.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox4, 11, 1)
        self.generalLayout.addLayout(InputLayout)
        
        
        
        # Create Editable Textbox for Plot lower limit
        self.textbox11 = QLineEdit()
        self.textbox11.setPlaceholderText('-200')
        self.textbox11.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox11, 12, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox11.setText('-200')
        # Create Editable Textbox for Plot upper limit
        self.textbox12 = QLineEdit()
        self.textbox12.setPlaceholderText('1000')
        self.textbox12.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox12, 13, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox12.setText('1000')
        
        #checkbox to show plot
        self.b1 = QCheckBox()
        InputLayout.addWidget(self.b1, 14, 1)
        #self.b1.setAlignment(Qt.AlignCenter)
        self.b1.setText("Show Plot")
        
        #checkbox to show Xray transmission block
        self.b3 = QCheckBox()
        InputLayout.addWidget(self.b3, 14, 0)
        #self.b1.setAlignment(Qt.AlignCenter)
        self.b3.setText("X-ray transmission  \n through media")
        self.b3.toggled.connect(self.b3_function)
        
       
        # Create Editable Textbox for Diagnostics
        self.textbox_Xray_05 = QLineEdit()
        self.textbox_Xray_05.setPlaceholderText('Diagnostics')
        self.textbox_Xray_05.setAlignment(Qt.AlignCenter)
        #self.textbox5.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox_Xray_05, 16, 0, 1, 2)
        self.generalLayout.addLayout(InputLayout)
        
        '''Buttons'''
        #Create Reset Button to Clear X-ray Input Field
        self.button_Input01 = QPushButton('Reset')
        InputLayout.addWidget(self.button_Input01, 15, 0)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input01.clicked.connect(self.clearDisplay)
        #Create Button to Calcualte sample mass and step
        self.button_Input02 = QPushButton('Calculate Sample Mass')
        InputLayout.addWidget(self.button_Input02 ,15, 1)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input02.clicked.connect(self.calculateResult)
        
        
    def radioButton1_function(self):
        if self.radioButton1.isChecked():
            if self.textbox13.text() =='N/A':
                self.textbox13.setText('1')
            crossarea = float(self.textbox13.text())*0.3
            self.textbox4.setText(str(crossarea))

    def radioButton2_function(self):
        if self.radioButton2.isChecked():
            if self.textbox13.text() =='N/A':
                self.textbox13.setText('1')
            crossarea = float(self.textbox13.text())*0.1
            self.textbox4.setText(str(crossarea))

    def radioButton3_function(self):
        if self.radioButton3.isChecked():
            self.textbox13.setText('N/A')
            self.textbox4.setText('0.38')
    
    def b1_function_previoussave(self):
        if self.b2.isChecked()== False:
            self.label4.setText('Total Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
            self.label7.setText('Estimated Edge Step:')
        else:
            self.label4.setText('Projected Total Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Projected Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
            self.label7.setText('Projected Estimated Edge Step:')
    
    
    def b1_function(self):
        import math
                
        if self.b2.isChecked()== False:
            stp = self.textbox6.text()
            AL = self.textbox3.text()
            Area = self.textbox4.text()
            self.textbox6.setText('{0:0.4f}'.format(float(stp)/math.sqrt(2)))
            self.textbox3.setText('{0:0.2f}'.format(float(AL)/math.sqrt(2)))
            self.textbox4.setText('{0:0.2f}'.format(float(Area)*math.sqrt(2)))
            self.label4.setText('Total Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
            self.label7.setText('Estimated Edge Step:')
        else:
            stp = self.textbox6.text()
            AL = self.textbox3.text()
            Area = self.textbox4.text()
            self.textbox6.setText('{0:0.4f}'.format(float(stp)*math.sqrt(2)))
            self.textbox3.setText('{0:0.2f}'.format(float(AL)*math.sqrt(2)))
            self.textbox4.setText('{0:0.2f}'.format(float(Area)/math.sqrt(2)))
            self.label4.setText('Projected Total Sample Absorption at E0 + 50 eV:')
            self.label5.setText('Projected Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
            self.label7.setText('Projected Estimated Edge Step:')
        if float(self.textbox6.text()) >1:
            self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
        else:
           self.textbox6.setStyleSheet("background-color:rgb(255,255,255)") 
        
        
    def b3_function(self):
        
        #XASCalcUI.setMaximumWidth(self, 200)
        
        if self.b3.isChecked()== False:
        
            " Handles the hiding of the panel and markers "
            layercount = self.generalLayout.count()-1
            #print(layercount)
            child = self.generalLayout.takeAt(layercount)
            #child.widget().deleteLater()
            child.widget().hide()
            #child.widget().show()
            #self.generalLayout.setSpacing(1)
            XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+40)
            
            
        else:
            XASCalcUI.setFixedWidth(self, SampleDilutionBlockWidth+XrayInputBlockWidth+ResultsBlockWidth+PropertiesBlockWidth+40)
            self._createPropertiesBlock()
            #child.widget().show()
    
            
         
    def on_combobox_previoussave(self):
        if self.combo.currentIndex() == 4:
            self.textbox2.setStyleSheet("background-color:rgb(224,224,224)")
            self.textbox2.setText('N/A')
            self.textbox2.setReadOnly(True)
            self.textbox6.setText('N/A')
            #self.textbox6.setStyleSheet("background-color:rgb(224,224,224)")
            #XrayInputFrame.setFixedHeight(self,XrayInputBlockHight)
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight2+50)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight2)
        else:
            self.textbox14.hide()
            self.label12.hide()
            self.textbox2.setStyleSheet("background-color:rgb(255,255,255)")
            #self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
            self.textbox2.setReadOnly(False)
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight+50)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight)
        
    def on_combobox_changed(self):
        if self.combo.currentIndex() == 4:
           self.textbox14.show()
           self.label12.show()
           self.textbox3.setText('1.5')
           self.textbox11.setText('-1000')
           self.textbox2.setStyleSheet("background-color:rgb(224,224,224)")
           self.textbox2.setText('N/A')
           self.textbox2.setReadOnly(True)
           self.textbox6.setText('N/A')
           self.textbox6.setStyleSheet("background-color:rgb(224,224,224)")
           #XrayInputFrame.setFixedHeight(self,XrayInputBlockHight)
           XASCalcUI.setFixedHeight(self, XrayInputBlockHight2+50)
           XrayInputFrame.setFixedHeight(XrayInputBlockHight2)
        else:
            self.textbox14.hide()
            self.label12.hide()
            
            self.textbox3.setText('2.5')
            self.textbox11.setText('-200')
           
            if self.textbox2.text() =='N/A':
                self.textbox2.setStyleSheet("background-color:rgb(255,255,255)")
                self.textbox2.clear()
                self.textbox6.clear()
                self.textbox6.setStyleSheet("background-color:rgb(255,255,255)")
            self.textbox2.setReadOnly(False)
            XASCalcUI.setFixedHeight(self, XrayInputBlockHight+50)
            XrayInputFrame.setFixedHeight(XrayInputBlockHight)
            
        
        
    
        
        
    def _createResultsBlock(self):
        '''Define QFrame'''
        ResultsFrame = QFrame()
        ResultsFrame.setFrameShape(QFrame.StyledPanel)
        ResultsFrame.setLineWidth(1)
                
        self.generalLayout.addWidget(ResultsFrame)
           
        """Define Layout"""
        OutputLayout = QGridLayout()
        ResultsFrame.setLayout(OutputLayout)
        ResultsFrame.setFixedWidth(ResultsBlockWidth)

        """Text Labels"""
        #Create Header Label
        self.label_Result01 = QLabel('Results')
        self.label_Result01.setAlignment(Qt.AlignLeft)
        self.label_Result01.setStyleSheet("font-weight: bold; text-decoration: underline")
        OutputLayout.addWidget(self.label_Result01, 0, 0, 1 ,2)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Label for Total Mass
        self.label6 = QLabel('Diluted Sample Mass [mg]:')
        self.label6.setAlignment(Qt.AlignRight)
        self.label6.setWordWrap(True)
        OutputLayout.addWidget(self.label6, 1, 0)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Label for Estimated Edge Step
        self.label7 = QLabel('Estimated Edge Step:')
        self.label7.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label7, 2, 0)
        self.label7.setWordWrap(True)
        self.generalLayout.addLayout(OutputLayout)
        
        #Create Label for Sample Mass
        self.label8 = QLabel('Sample Mass [mg]:')
        self.label8.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label8, 3, 0)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Lable for Diluent Mass
        self.label9 = QLabel('Diluent Mass [mg]:')
        self.label9.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label9, 4, 0)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Label for Edge Energy
        self.label10 = QLabel('Edge Energy [eV]:')
        self.label10.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label10, 5, 0)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Dummy Label 
        #self.label12 = QLabel('')
        #self.label12.setAlignment(Qt.AlignRight)
        #OutputLayout.addWidget(self.label12, 10, 0,4,1)
        #self.generalLayout.addLayout(OutputLayout)
        
        self.label11 = QLabel(self)
        #pixmap = QPixmap('SSRL_logo.png')
        pixmap = QPixmap('SSRL_logo_2021.png')
        self.label11.setPixmap(pixmap)
        self.label11.setAlignment(Qt.AlignCenter)
        
        OutputLayout.addWidget(self.label11, 10, 0,7,3)
        
        self.label11.resize(0.5, 1)
        self.generalLayout.addLayout(OutputLayout) 
        
        
        
        """Output Fields"""
        # Create Editable Textbox for Total Sample Mass
        self.textbox5 = QLineEdit()
        self.textbox5.setFixedSize(150, 35)
        self.textbox5.setAlignment(Qt.AlignRight)
        self.textbox5.setReadOnly(True)
        OutputLayout.addWidget(self.textbox5, 1, 1)
        self.generalLayout.addLayout(OutputLayout)

        # Create Editable Textbox for Estimated Edge Step 
        self.textbox6 = QLineEdit()
        self.textbox6.setFixedSize(150, 35)
        self.textbox6.setAlignment(Qt.AlignRight)
        self.textbox6.setReadOnly(True)
        OutputLayout.addWidget(self.textbox6, 2, 1)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Editable Textbox for Sample Mass
        self.textbox7 = QLineEdit()
        self.textbox7.setFixedSize(150, 35)
        self.textbox7.setAlignment(Qt.AlignRight)
        self.textbox7.setReadOnly(True)
        OutputLayout.addWidget(self.textbox7, 3, 1)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Editable Textbox for Diluent Mass
        self.textbox8 = QLineEdit()
        self.textbox8.setFixedSize(150, 35)
        self.textbox8.setAlignment(Qt.AlignRight)
        self.textbox8.setReadOnly(True)
        OutputLayout.addWidget(self.textbox8, 4, 1)
        self.generalLayout.addLayout(OutputLayout)

        # Create Editable Textbox for Edge Enrgy
        self.textbox9 = QLineEdit()
        self.textbox9.setFixedSize(150, 35)
        self.textbox9.setAlignment(Qt.AlignRight)
        self.textbox9.setReadOnly(True)
        OutputLayout.addWidget(self.textbox9, 5, 1)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Editable Textbox for ploty
        #self.textbox10 = QLineEdit()
        #self.textbox10.setFixedSize(150, 35)
        #self.textbox10.setAlignment(Qt.AlignRight)
        #self.textbox10.setReadOnly(True)
        #OutputLayout.addWidget(self.textbox10, 6, 1)
        #self.generalLayout.addLayout(OutputLayout)
        
       
        
        #self.button_ptl00 = QPushButton('Save Results')
        #OutputLayout.addWidget(self.button_ptl00, 0, 1)
        #self.generalLayout.addLayout(OutputLayout)
        #self.button_ptl00.clicked.connect(self.textlabels)
        #self.button_ptl00.clicked.connect(self.updatecount)

    #def updatecount(self):
       #global ksavingcounter
       #ksavingcounter +=1
   
    #def updatecountmin(self):
       #global ksavingcounter
       #ksavingcounter -=1
    
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
        saverlabel[19] = 'Total Sample Absorptoin at E0 + 50 eV:'
        'add radio button state to saver'
        saverlabel[20] = 'Capillary/Pellet:'
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
        
        #print(saverlabel)
        
    
    def SaveResults(self):
        saver[0] = samplesaver[1]
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
        saver[19] = self.textbox3.text()
        'radio butnn checkstate'
        if self.radioButton1.isChecked():
            saver[20] = 3
        if self.radioButton2.isChecked():
            saver[20] = 1
        if self.radioButton3.isChecked():
            saver[20] = 7
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
            
            
        
   
    def opencatfile(self):
       global filePath
       filePath = QFileDialog.getOpenFileName(self)[0]
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
       
    def SaveAs(self):
        global filePath
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "",
						"txt(*.txt);;All Files(*.*) ")
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
        samplesaver[1] = saver[0] 
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
        self.combo.setCurrentIndex(float(saver[16]))
        self.textbox14.setText(saver[17])
        ' 45 deg check state'
        if float(saver[18]) != self.b2.checkState():
            #self.b2.setCheckState(2)
            if float(saver[18]) == 0:
                self.b2.setCheckState(0)
            else:
                self.b2.setCheckState(2)   
            #self.b2.click()
        self.b1_function_previoussave()
        self.textbox3.setText(saver[19])
        if saver[20] != '':
            if float(saver[20]) == 3:
                self.radioButton1.click()
            if float(saver[20]) == 1:
                self.radioButton2.click()
            if float(saver[20]) == 7:
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
            self.combo3.setCurrentIndex(float(saver[31]))
            self.textbox_P02.setText(saver[32])
            self.combo_U3.setCurrentIndex(float(saver[33]))
            self.textboxP04.setText(saver[34])
            self.combo2.setCurrentIndex(float(saver[35]))
            self.textbox_P03.setText(saver[36])
            self.combo_U2.setCurrentIndex(float(saver[37]))
            self.textboxP05.setText(saver[38])
            self.combo4.setCurrentIndex(float(saver[39]))
            self.textbox_P04.setText(saver[40])
            self.combo_U4.setCurrentIndex(float(saver[41]))
            self.textboxP06.setText(saver[42])
            self.combo5.setCurrentIndex(float(saver[43]))
            self.textbox_P05.setText(saver[44])
            self.combo_U5.setCurrentIndex(float(saver[45]))
            self.textboxP07.setText(saver[46])
            self.combo6.setCurrentIndex(float(saver[47]))
            self.combo7.setCurrentIndex(float(saver[48]))
            self.slider.setValue(float(saver[49]))
            self.slider2.setValue(float(saver[50]))
            self.combo_C1.setCurrentIndex(float(saver[51]))
            self.textboxP11.setText(saver[52])
        else:
            self.b3.setCheckState(0)
            
        print('File imported')
        #print(ksavingcounter)
        
        
        
        
   
        
        
    def calculateSampleComp(self):
        """Evaluate expressions"""
        Sample = self.textbox_dil01.text()
        Diluent = self.textbox_dil02.text()
        Sample_DR = self.textbox_dil03.text()
        Diluent_DR = self.textbox_dil04.text()
        
        Error_message, Result = fct.XASStoichCalc(Sample, Diluent, Sample_DR, Diluent_DR)
        if "ERROR" in Error_message:
            self.textbox_dil05.setText(Result)
        else:
            self.textbox1.setText(Result)
            self.textbox_dil05.setText(Error_message)
        
        
    def calculateResult(self):
        """Evaluate expressions."""
        
        
        
        Sample = self.textbox1.text()
        Element = self.textbox2.text()
        if self.combo.currentIndex() == 4:
            Edge = self.textbox14.text()
        else:
            Edge = self.combo.currentText()
        AL = self.textbox3.text()
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
        
        Result, Enot, ms, stp,muave = fct.XASMassCalc(Sample, Element, Edge, Area, AL)
        
        import math
        
        stp45 = stp*math.sqrt(1)
        AL45 = float(AL)*math.sqrt(1)
        Area45 = float(Area)/math.sqrt(1)
        
        if 'ERROR' in Result:
            self.textbox_Xray_05.setText(Result)
        else:
            self.textbox5.setText('{0:0.2f}'.format(ms))
            if self.b2.isChecked()== False:
                self.textbox6.setText('{0:0.4f}'.format(stp))
            else:
                self.textbox6.setText('{0:0.4f}'.format(stp45))
                self.textbox3.setText('{0:0.2f}'.format(AL45))
                self.textbox4.setText('{0:0.2f}'.format(Area45))
                
                
                
            if stp >1:
                self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
            if self.b2.isChecked()== True and stp45 >1:
                self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")                
            self.textbox7.setText('{0:0.2f}'.format(ms*MF_Samp))
            self.textbox8.setText('{0:0.2f}'.format(ms*MF_Dil))
            self.textbox9.setText('{0:0.0f}'.format(Enot))
            self.textbox_Xray_05.clear()
        
            
                        
        
        #if self.textbox11.text() == '' or self.textbox12.text() == '':
        if self.b1.isChecked()== False:
            self.textbox_Xray_05.setText(Result)
        else:
            self.textbox_Xray_05.clear()
            #section to ensure plot auto appears as new window
            from IPython import get_ipython
            get_ipython().run_line_magic('matplotlib','qt5')
            
           
            #Create plot of AL over energy range kspace over energy range and list reulsts table in last fig
            
            
            kspaceedges, atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols = fct.XASEZero(Sample,Enot)
            
            atomicedgesall,atomicsymbolsall,atomicnumbersall,atomicedgesymbolsall = fct.XASEZeroList(Sample)
            
            #ploting limits
            delta1 = float(self.textbox11.text())
            delta2 = float(self.textbox12.text())
            start = delta1
            interval = 0.5
            stop = delta2+interval
            figure, axis = plt.subplots(1, 3,figsize=(16,5))
            
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
            kspace  = [None] *length2
        
            #kpace plot y values for now
            for i in range(length3):
                y3[i]=0
            #kspace  y value points are edges of element in sample that could show up in kspace
            for i in range(length2):
                kspace[i] = fct.kspacecalc(x2[i])
                #y2[i] = fct.XASPLOTTER(Sample, Element, Edge, Area, AL, x2[i],delta1)
                #y2[i] =float(y2[i])*(ms/float(Area))/1000
                #y2[i] = (y2[i]-float(AL))/float(AL)
                y2[i] = 0
            #plot of modified mu average (Absorption length over energy range)
            
            
            
            for i in range(length):
                if self.b2.isChecked()== False:
                    y[i] = fct.XASPLOTTER(Sample, Element, Edge, Area, AL, x[i],delta1)
                    y[i] =float(y[i])*(ms/float(Area))/1000
                else:
                    y[i] = fct.XASPLOTTER(Sample, Element, Edge, Area, str(AL45), x[i],delta1) 
                    #y[i] =float(y[i])*(ms/float(Area))*math.sqrt(1) /1000
                    y[i] =float(y[i])*(ms/float(Area))/1000
            #redefining x axis to absolute scale
            x = np.arange(start, stop, interval)+Enot
            
            
            
            
            
            
            
            
            
            #defining plot names, axis labels and plot colors
            axis[0].plot(x, y, color = 'b', linestyle= '-') #label="XXXX \nI am Trying To Add a New Line of Text"
            
            
            axis[0].set_xlabel(r"Photon Energy (eV)")
            axis[0].set_xlim([Enot+delta1, Enot+delta2])
            axis[0].set_ylim([0, float(muave)*(ms/float(Area))/1000*1.5])
            axis[0].set_ylabel(r"$µ_{average}$ • Mass/Area")
            axis[1].set_xlim([0, fct.kspacecalc(delta2)])
            axis[1].yaxis.set_visible(False)
            axis[2].xaxis.set_visible(False)
            axis[2].yaxis.set_visible(False)
            #import matplotlib.ticker as mtick
            #axis[1].yaxis.set_major_formatter(mtick.PercentFormatter())
            
            axis[1].plot(kspace, y2,color = 'b', linestyle= '-')
            axis[1].plot(kspaceedges, y3,color = 'g', linestyle="",marker="o")
            
            axis[1].set_xlabel(r"k ($\AA$⁻¹)")
            
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
            
            #listing results values in 3 figure
            left = 0.01
            width = 0.01
            bottom  = 0.01
            height = .6
            right = left + width
            top = bottom + height
            
            #title functions need to be worked out in next version
            #if self.tab1.textbox_tab101.text() =='' or self.tab1.textbox_tab2_05 == '' : 
                #if self.textbox_dil04.text() =='' or self.textbox_dil03.text() =='':
                   # axis[1].set_title(self.textbox_dil01.text())
               # else:
                    #axis[1].set_title(self.textbox_dil01.text() + ' '+ self.textbox_dil02.text() +' '+ self.textbox_dil03.text() +':'+self.textbox_dil04.text())
           # else:
               # axis[1].set_title(self.tab1.textbox_tab101.text())
            #if self.textbox_dil04.text() =='' or self.textbox_dil03.text() =='':
                #axis[1].set_title(self.textbox_dil01.text())
            #else:
                #axis[1].set_title(self.textbox_dil01.text() + ' '+ self.textbox_dil02.text() +' '+ self.textbox_dil03.text() +':'+self.textbox_dil04.text())
            
            
            axis[2].text(right, top, "Total Sample Absorption:")
            axis[2].text(right, top-.05, "Estimated Edge Step:")
            axis[2].text(right, top-.1, "Sample mass[mg]:")
            axis[2].text(right, top-.15, "Diluent mass[mg]:")
            axis[2].text(right, top-.2, "Cell:")
            axis[2].text(right+0.5, top, self.textbox3.text())
            axis[2].text(right+0.5, top-0.05, self.textbox6.text())
            axis[2].text(right+0.5, top-0.1, self.textbox7.text())
            axis[2].text(right+0.5, top-0.15, self.textbox8.text())
            if self.radioButton1.isChecked():
                axis[2].text(right+0.5, top-0.2, "3 mm")
            if self.radioButton2.isChecked():
                axis[2].text(right+0.5, top-0.2, "1 mm")
            if self.radioButton3.isChecked():
                axis[2].text(right+0.5, top-0.2, "Pellet")
        
            for i in range(length4):
                if self.b2.isChecked()== False:
                    Result1, Enots[i], ms1, yedges[i],muaves[i] = fct.XASMassCalc(Sample, atomicsymbolsall[i], atomicedgesymbolsall[i], Area, AL)
                    muaves[i] =float(muaves[i])*(ms/float(Area))/1000
                    yedges[i]='{0:0.3f}'.format(yedges[i])
                else:
                    Result1, Enots[i], ms1, yedges[i],muaves[i] = fct.XASMassCalc(Sample, atomicsymbolsall[i], atomicedgesymbolsall[i], Area, str(AL45))
                    muaves[i] =float(muaves[i])*(ms/float(Area))/1000
                    yedges[i]='{0:0.3f}'.format(yedges[i])
            
            axis[0].plot(Enots, muaves,color = 'g', linestyle="",marker="o")
            
            for i, txt in enumerate(yedges):
                axis[0].annotate(txt, (Enots[i], muaves[i]), # these are the coordinates to position the label
                textcoords="offset points", # how to position the text
                xytext=(30,8), # distance from text to points (x,y)
                ha='right',rotation = 0) # horizontal alignment can be left, right or center
            
            plt.show
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
        self.b1.setChecked(False)
        self.b2.setChecked(False)
        self.textbox3.setText('2.5')
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
            thicknessgas = fct.unitconvert(thicknessgas,self.combo_U3.currentIndex())
            transgas = np.exp(-float(thicknessgas) *  xraydb.material_mu(Materialgases,float(Enot)))*100
            self.textboxP04.setText('{0:0.2f}'.format(transgas))
        if thicknesswall !='':
            thicknesswall = fct.unitconvert(thicknesswall,self.combo_U2.currentIndex())
            transwall = np.exp(-float(thicknesswall) *  xraydb.material_mu(Materialwall,float(Enot)))*100
            self.textboxP05.setText('{0:0.2f}'.format(transwall))
        if thicknesssolvent !='':
            thicknesssolvent = fct.unitconvert(thicknesssolvent,self.combo_U4.currentIndex())
            transsolvent = np.exp(-float(thicknesssolvent) *  xraydb.material_mu(Materialsolvent,float(Enot)))*100
            self.textboxP06.setText('{0:0.2f}'.format(transsolvent))
        if thicknessmetal !='':
            thicknessmetal = fct.unitconvert(thicknessmetal,self.combo_U5.currentIndex())
            transmetal = np.exp(-float(thicknessmetal) *  xraydb.material_mu(Materialmetal,float(Enot)))*100
            self.textboxP07.setText('{0:0.2f}'.format(transmetal))
    
    def CalBeamabs(self):
        if self.textbox9.text()=='':
            self.textboxP11.setText("Error")
        else:
            ionchamberdensity = fct.ionchamberdensity(self.slider2.value(),self.combo6.currentText(),self.combo7.currentText(),-self.slider.value()/100)
            Enot = self.textbox9.text()

            if self.combo_C1.currentIndex() == 5:
                self.textboxP12.show()
                ionchambergas1 =  -self.slider.value()/100*float(self.textboxP12.text())*xraydb.material_mu(self.combo6.currentText(),float(Enot),density=ionchamberdensity)
                ionchambergas2 =  (100+self.slider.value())/100*float(self.textboxP12.text())*xraydb.material_mu(self.combo7.currentText(),float(Enot),density=ionchamberdensity)
                transionchamber = np.exp(-(ionchambergas1+ionchambergas2))*100
          
            else:
                self.textboxP12.hide()
                ionchambergas1 =  -self.slider.value()/100*float(self.combo_C1.currentText())*xraydb.material_mu(self.combo6.currentText(),float(Enot),density=ionchamberdensity)
                ionchambergas2 =  (100+self.slider.value())/100*float(self.combo_C1.currentText())*xraydb.material_mu(self.combo7.currentText(),float(Enot),density=ionchamberdensity)
                transionchamber = np.exp(-(ionchambergas1+ionchambergas2))*100
        
            self.textboxP11.setText('{0:0.2f}'.format(100-transionchamber))
        
        
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
        self.tabs.addTab(self.tab2,"Supported Metal Complexs")
        
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
        self.label_tab2_06 = QLabel('Note: for metal oxide or organometallic complexes')
        self.label_tab2_06.setAlignment(Qt.AlignLeft)
        Tab2Layout.addWidget(self.label_tab2_06, 7, 0, 1,2)
        self.tab2.setLayout(Tab2Layout)
        
        # Create Label for Notes
        self.label_tab2_07 = QLabel('Note: only define Complex Loading OR Metal Loading')
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
        #samplesaver.clear()
        #samplesaver = [None]*6
        
        
    def clearSampleBuildertab2(self):
        "Clear the sample builder tab of inputs"
        self.textbox_tab2_01.clear()
        self.textbox_tab2_02.clear()
        self.textbox_tab2_03.clear()
        self.textbox_tab2_04.clear()
        self.textbox_tab2_05.clear()  
        #complexsaver.clear()
        #complexsaver = [None]*6
        
        
    def UpdateSampleMetal(self):
        Support = self.textbox_tab101.text()
        Metal_Site1 = self.textbox_tab102.text()
        Metal1_Loading = self.textbox_tab103.text()
        Metal_Site2 = self.textbox_tab104.text()
        Metal2_Loading = self.textbox_tab105.text()
            
        Result = fct.metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support)
        
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
            
            Result = fct.metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support)
            
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
            
            Result = fct.ComplexCalculateSample(Complex, Metal_Loading, Metal_Site, Support)
            
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
        self.width = 480#640
        self.height = 640#480
        InfoWindow.setFixedWidth(self, 400)
        # Set main window's properties
        self.setWindowTitle(self.title)
        layout = QGridLayout()
        
        self.label_Info00 = QLabel('Python Libraries')
        self.label_Info00.setAlignment(Qt.AlignLeft)
        self.label_Info00.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info00, 0, 0, 1, 4)
        self.label_Info00.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info01 = QLabel('xraydb')
        self.label_Info01.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info01, 1, 0)
        self.label_Info01.setWordWrap(True)
        self.setLayout(layout)
        
        linkTemplate = '<a href={0}>{1}</a>'
        
        self.label_Info02 = QLabel('xraylib')
        self.label_Info02.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info02, 1, 1)
        self.label_Info02.setWordWrap(True)
        self.setLayout(layout)
        
        
    
        self.label_Info03 = QLabel()
        self.label_Info03.setText(linkTemplate.format('https://sites.slac.stanford.edu/co-access','Co-ACCESS Information'))
        self.label_Info03.setAlignment(Qt.AlignLeft)
        self.label_Info03.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info03, 2, 0, 1, 4)
        self.label_Info03.setWordWrap(True)
        self.label_Info03.setOpenExternalLinks(True)
        self.setLayout(layout)
        
   
        self.label_Info04 = QLabel('Co-ACCESS, is supported by the U.S. Department of Energy, Office of Basic Energy Sciences, Chemical Sciences, Geosciences and Biosciences')
        self.label_Info04.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info04, 3, 0,1,4)
        self.label_Info04.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info05 = QLabel('Common Co-ACCESS XAS Cell Information')
        self.label_Info05.setAlignment(Qt.AlignLeft)
        self.label_Info05.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info05, 4, 0, 1, 4)
        self.label_Info05.setWordWrap(True)
        self.setLayout(layout)
   
        self.label_Info06 = QLabel('Capillary Wall Thickness [μm]')
        self.label_Info06.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info06, 5, 0,1,4)
        self.label_Info06.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info07 = QLabel('1 mm')
        self.label_Info07.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info07, 6, 1,1,1)
        self.label_Info07.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info08 = QLabel('3 mm')
        self.label_Info08.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info08, 6, 2,1,1)
        self.label_Info08.setWordWrap(True)
        self.setLayout(layout)
        
        self.label_Info09 = QLabel('Kapton')
        self.label_Info09.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info09, 7, 0,1,1)
        self.setLayout(layout)
        
        self.label_Info10 = QLabel('80')
        self.label_Info10.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info10, 7,1,1,1)
        self.setLayout(layout)
        
        self.label_Info11 = QLabel('87')
        self.label_Info11.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info11, 7,2,1,1)
        self.setLayout(layout)
        
        self.label_Info12 = QLabel('Quartz')
        self.label_Info12.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info12, 8, 0,1,1)
        self.setLayout(layout)
        
        self.label_Info13 = QLabel('10 or 20')
        self.label_Info13.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info13, 8,1,1,1)
        self.setLayout(layout)
        
        self.label_Info14 = QLabel('20')
        self.label_Info14.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info14, 8,2,1,1)
        self.setLayout(layout)
        
        self.label_Info15 = QLabel('Misc')
        self.label_Info15.setAlignment(Qt.AlignLeft)
        self.label_Info15.setStyleSheet("font-weight: bold; text-decoration: underline")
        layout.addWidget(self.label_Info15, 9, 0, 1, 4)
        self.setLayout(layout)
        
        self.label_Info16 = QLabel('Kapton Shield [mils]')
        self.label_Info16.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info16, 10, 0,1,2)
        self.setLayout(layout)
        
        self.label_Info17 = QLabel('2')
        self.label_Info17.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info17, 10, 2,1,2)
        self.setLayout(layout)
        
        self.label_Info18 = QLabel('Milar [μm]')
        self.label_Info18.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info18, 11, 0,1,2)
        self.setLayout(layout)
        
        self.label_Info19 = QLabel('3.5')
        self.label_Info19.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info19, 11, 2,1,2)
        self.setLayout(layout)
        
        self.label_Info20 = QLabel('Diameter')
        self.label_Info20.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label_Info20, 6, 0,1,1)
        self.setLayout(layout)
      
        
      
        
###################
#                 #
#    MAIN LOOP    #
#                 #
###################        
    
if __name__ == "__main__":
    def run_app():
        # Create an instance of `QApplication`
        app = QApplication(sys.argv)
        # Show the calculator's GUI
        
        mainWin = XASCalcUI()
        
        mainWin.saveState()
        
        mainWin.show()
        app.exec_()
    run_app()