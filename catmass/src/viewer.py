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

from PyQt5.QtWidgets import QGridLayout

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTabWidget



from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QRadioButton,QCheckBox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, CheckButtons
from PyQt5.QtGui import QPixmap



### How do I call this?
from src import functions as fct

#######################
##     MAIN VIEW     ##
#######################

#Matrix to save values
saver= [None] *19
samplesaver = [None]*6
complexsaver = [None]*6
#savers = np.empty((19, 5))


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
        
        # Set the central widgetand general layout
        self.generalLayout = QHBoxLayout()
        
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self._createSampleDilutionBlock()
        self._createXrayInputBlock()
        self._createResultsBlock()

       
        # Create menu bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        #editMenu = mainMenu.addMenu('Edit')
        #viewMenu = mainMenu.addMenu('View')
        #searchMenu = mainMenu.addMenu('Search')
        #toolsMenu = mainMenu.addMenu('Tools')
        #helpMenu = mainMenu.addMenu('Help')
        
        # Add Exit Button to File Menu + Action
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(QApplication.closeAllWindows)
        exitButton.triggered.connect(QApplication.quit)
        fileMenu.addAction(exitButton)
    
    def _createSampleDilutionBlock(self)    :
        '''Define QFrame'''
        Diluent_frame = QFrame()
        Diluent_frame.setFrameShape(QFrame.StyledPanel)
        Diluent_frame.setLineWidth(1)
                
        self.generalLayout.addWidget(Diluent_frame)
        
        
        """Define Layout"""
        DilutionLayout = QGridLayout()
        
        Diluent_frame.setLayout(DilutionLayout)
        
        '''Text Labels'''
        # Create Header Label
        self.label_dil00 = QLabel('Sample and Dilution Definition')
        self.label_dil00.setAlignment(Qt.AlignLeft)
        self.label_dil00.setStyleSheet("font-weight: bold; text-decoration: underline")
        DilutionLayout.addWidget(self.label_dil00, 0, 0, 1, 1)
        self.label_dil00.setWordWrap(True)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create "Sample" Label
        self.label_dil01 = QLabel('Sample')
        self.label_dil01.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil01, 1, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create "Diluent" Label
        self.label_dil02 = QLabel('Diluent')
        self.label_dil02.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil02, 1, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create "Stoichiometry" Label
        self.label_dil03 = QLabel('Stoichiometry:')
        self.label_dil03.setAlignment(Qt.AlignRight)
        DilutionLayout.addWidget(self.label_dil03, 2, 0)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Creat "Dilution Ratio" label
        self.label_dil04 = QLabel('Mass Dilution Ratio:')
        self.label_dil04.setAlignment(Qt.AlignRight)
        DilutionLayout.addWidget(self.label_dil04, 3, 0)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Creat "Dummy" label fo Co-ACCESS label
       
         
        
        self.label_dil05 = QLabel(self)
        pixmap = QPixmap('co_access_logo_text.png')
        self.label_dil05.setPixmap(pixmap)
        self.label_dil05.setAlignment(Qt.AlignCenter)
        DilutionLayout.addWidget(self.label_dil05, 6, 0,7,3)
        self.label_dil05.resize(0.5, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        
        """Input Fields"""
        # Create Text Box for Sample Formula
        self.textbox_dil01 = QLineEdit()
        self.textbox_dil01.setPlaceholderText('Chemical Formula')
        self.textbox_dil01.setFixedSize(150, 35)
        DilutionLayout.addWidget(self.textbox_dil01, 2, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Diluent Formula
        self.textbox_dil02 = QLineEdit()
        self.textbox_dil02.setPlaceholderText('Chemical Formula')
        self.textbox_dil02.setFixedSize(150, 35)
        DilutionLayout.addWidget(self.textbox_dil02, 2, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Sample Dilution Fraction
        self.textbox_dil03 = QLineEdit()
        self.textbox_dil03.setPlaceholderText('#')
        self.textbox_dil03.setAlignment(Qt.AlignCenter)
        self.textbox_dil03.setFixedSize(75, 35)
        DilutionLayout.addWidget(self.textbox_dil03, 3, 1)
        self.generalLayout.addLayout(DilutionLayout)
        
        # Create Text Box for Diluent Dilution Fraction
        self.textbox_dil04 = QLineEdit()
        self.textbox_dil04.setPlaceholderText('#')
        self.textbox_dil04.setAlignment(Qt.AlignCenter)
        self.textbox_dil04.setFixedSize(75, 35)
        DilutionLayout.addWidget(self.textbox_dil04, 3, 2)
        self.generalLayout.addLayout(DilutionLayout)
        
        
        
        
        # Create Text Box for Diagnostics
        self.textbox_dil05 = QLineEdit()
        self.textbox_dil05.setPlaceholderText('Diagnostic')
        self.textbox_dil05.setAlignment(Qt.AlignCenter)
        #self.textbox_dil05.setFixedSize(150, 35)
        DilutionLayout.addWidget(self.textbox_dil05, 5, 0, 1,3)
        self.generalLayout.addLayout(DilutionLayout)
        
        
        """Buttons"""
        # Create Button to Open Sample Builder
        self.button_dil00 = QPushButton('Sample Builder')
        DilutionLayout.addWidget(self.button_dil00, 0, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil00.clicked.connect(self.openSampleBuilder)
        
        # Create Button to Import Previous save
        self.button_dil00 = QPushButton('Import Previous Save')
        DilutionLayout.addWidget(self.button_dil00, 0, 1)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil00.clicked.connect(self.PreviousSave)
        
        
        # Create Button to Reset all Text Fields
        self.button_dil01 = QPushButton('Reset')
        DilutionLayout.addWidget(self.button_dil01, 4, 0)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil01.clicked.connect(self.clearDilutionInput)
        
        # Create Button to Calculate Diluted Sample Chemical Formula 
        self.button_dil02 = QPushButton('Calculate Diluted Sample Chemical Formula')
        DilutionLayout.addWidget(self.button_dil02, 4, 1, 1, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil02.clicked.connect(self.calculateSampleComp)
        
        
        
        
        
        
    def _createXrayInputBlock(self):
        '''Define QFrame'''
        XrayInputFrame = QFrame()
        XrayInputFrame.setFrameShape(QFrame.StyledPanel)
        XrayInputFrame.setLineWidth(1)
                
        self.generalLayout.addWidget(XrayInputFrame)
        
        """Define Layout"""
        InputLayout = QGridLayout()
        XrayInputFrame.setLayout(InputLayout)
        
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
        
        # Create Lable for Desired Absorption Length
        self.label4 = QLabel('Total Sample Absorption at E0 + 50 eV:')
        self.label4.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label4, 4, 0)
        self.label4.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Desired Area
        self.label5 = QLabel('Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
        self.label5.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label5, 9, 0)
        self.label5.setWordWrap(True)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        self.label6 = QLabel('Sample Area Perpendicular')
        self.label6.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label6, 5, 0)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Co-ACCESS default cell Area
        self.label7 = QLabel('to Beam of Co-ACCESS')
        self.label7.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label7, 6, 0)
        self.generalLayout.addLayout(InputLayout)
        # Create Lable for Co-ACCESS default cell Area
        self.label8 = QLabel('Capillaries:')
        self.label8.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label8, 7, 0)
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
        
        # Create Lable for bed legnth
        self.label11 = QLabel('Bed length [1 cm]')
        self.label11.setAlignment(Qt.AlignCenter)
        InputLayout.addWidget(self.label11, 8, 0)
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
        self.combo.setFixedSize(150, 35)
        InputLayout.addWidget(self.combo, 3, 1)
        self.generalLayout.addLayout(InputLayout)
 
        # Create Editable Textbox for Desired Absorption Length
        self.textbox3 = QLineEdit()
        self.textbox3.setPlaceholderText('Target Absorption Length')
        self.textbox3.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox3, 4, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox3.setText('2.5')
        
        
        #checkbox to show plot
        self.b1 = QCheckBox()
        InputLayout.addWidget(self.b1, 11, 0)
        #self.b1.setAlignment(Qt.AlignCenter)
        self.b1.setText("Show Plot")
        #checkbox to show results with cell at 45 degrees
        self.b2 = QCheckBox()
        InputLayout.addWidget(self.b2, 11, 1)
        #self.b1.setAlignment(Qt.AlignCenter)
        self.b2.setText("Sample at 45°")
        self.b2.toggled.connect(self.b1_function)
        
        
        
        
        # Radio button for Capillaries
        self.radioButton1 = QRadioButton(self)
        InputLayout.addWidget(self.radioButton1, 5, 1)
        self.radioButton2 = QRadioButton()
        InputLayout.addWidget(self.radioButton2, 6, 1)
        self.radioButton3 = QRadioButton()
        InputLayout.addWidget(self.radioButton3, 7, 1)
        #self.radioButton4 = QRadioButton()
        #InputLayout.addWidget(self.radioButton4, 5, 5)
        self.radioButton1.setText("3 mm Capillary")
        self.radioButton2.setText("1 mm Capillary")
        self.radioButton3.setText("7 mm Pellet")
        self.radioButton1.toggled.connect(self.radioButton1_function) 
        self.radioButton2.toggled.connect(self.radioButton2_function) 
        self.radioButton3.toggled.connect(self.radioButton3_function)
     
       
            
        # Create Editable Textbox for Desired Area
        self.textbox4 = QLineEdit()
        self.textbox4.setPlaceholderText('Sample Area')
        self.textbox4.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox4, 9, 1)
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
        
        # Create Editable Textbox bed length
        self.textbox13 = QLineEdit()
        self.textbox13.setPlaceholderText('1')
        self.textbox13.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox13, 8, 1)
        self.generalLayout.addLayout(InputLayout)
        self.textbox13.setText('1')
        

        # Create Editable Textbox for Diagnostics
        self.textbox_Xray_05 = QLineEdit()
        self.textbox_Xray_05.setPlaceholderText('Diagnostics')
        self.textbox_Xray_05.setAlignment(Qt.AlignCenter)
        #self.textbox5.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox_Xray_05, 14, 0, 1, 2)
        self.generalLayout.addLayout(InputLayout)
        
        '''Buttons'''
        #Create Reset Button to Clear X-ray Input Field
        self.button_Input01 = QPushButton('Reset')
        InputLayout.addWidget(self.button_Input01, 10, 0)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input01.clicked.connect(self.clearDisplay)
        #Create Button to Calcualte sample mass and step
        self.button_Input02 = QPushButton('Calculate Sample Mass')
        InputLayout.addWidget(self.button_Input02 ,10, 1)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input02.clicked.connect(self.calculateResult)
        
        
    def radioButton1_function(self):
        if self.radioButton1.isChecked():
            crossarea = float(self.textbox13.text())*0.3
            self.textbox4.setText(str(crossarea))

    def radioButton2_function(self):
        if self.radioButton2.isChecked():
            crossarea = float(self.textbox13.text())*0.1
            self.textbox4.setText(str(crossarea))

    def radioButton3_function(self):
        if self.radioButton3.isChecked():
            self.textbox13.setText('1')
            self.textbox4.setText('0.38')
    def b1_function(self):
        import math
                
        if self.b2.isChecked()== False:
            stp = self.textbox6.text()
            AL = self.textbox3.text()
            Area = self.textbox4.text()
            self.textbox6.setText('{0:0.2f}'.format(float(stp)/math.sqrt(2)))
            self.textbox3.setText('{0:0.2f}'.format(float(AL)/math.sqrt(2)))
            self.textbox4.setText('{0:0.2f}'.format(float(Area)*math.sqrt(2)))
        else:
            stp = self.textbox6.text()
            AL = self.textbox3.text()
            Area = self.textbox4.text()
            self.textbox6.setText('{0:0.4f}'.format(float(stp)*math.sqrt(2)))
            self.textbox3.setText('{0:0.2f}'.format(float(AL)*math.sqrt(2)))
            self.textbox4.setText('{0:0.2f}'.format(float(Area)/math.sqrt(2)))
        
        if float(self.textbox6.text()) >1:
            self.textbox6.setStyleSheet("background-color:rgb(255,0,0)")
        else:
           self.textbox6.setStyleSheet("background-color:rgb(255,255,255)") 
        
        
        
        
        
        
        
        
    def _createResultsBlock(self):
        '''Define QFrame'''
        ResultsFrame = QFrame()
        ResultsFrame.setFrameShape(QFrame.StyledPanel)
        ResultsFrame.setLineWidth(1)
                
        self.generalLayout.addWidget(ResultsFrame)
           
        """Define Layout"""
        OutputLayout = QGridLayout()
        ResultsFrame.setLayout(OutputLayout)

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
        OutputLayout.addWidget(self.label6, 1, 0)
        self.generalLayout.addLayout(OutputLayout)
        
        # Create Label for Estimated Edge Step
        self.label7 = QLabel('Estimated Edge Step:')
        self.label7.setAlignment(Qt.AlignRight)
        OutputLayout.addWidget(self.label7, 2, 0)
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
        #self.label11 = QLabel('')
        #self.label11.setAlignment(Qt.AlignRight)
        #OutputLayout.addWidget(self.label11, 12, 0,5,1)
        #self.generalLayout.addLayout(OutputLayout)
        self.label11 = QLabel(self)
        pixmap = QPixmap('SSRL_logo.png')
        self.label11.setPixmap(pixmap)
        self.label11.setAlignment(Qt.AlignCenter)
        OutputLayout.addWidget(self.label11, 12, 0,5,3)
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
        
       
        
        self.button_ptl00 = QPushButton('Save Results')
        OutputLayout.addWidget(self.button_ptl00, 0, 1)
        self.generalLayout.addLayout(OutputLayout)
        self.button_ptl00.clicked.connect(self.SaveResults)
        
        
        
    
        
    
    def SaveResults(self):
        
        saver[1] = self.textbox_dil01.text()
        saver[2] = self.textbox_dil02.text()
        saver[3] = self.textbox_dil03.text()
        saver[4] = self.textbox_dil04.text()
        saver[5] = self.textbox1.text()
        saver[6] = self.textbox2.text()
        saver[7] = self.textbox3.text()
        saver[8] = self.textbox4.text()
        saver[9] = self.textbox11.text()
        saver[10] = self.textbox12.text()
        saver[11] = self.textbox5.text()
        saver[12] = self.textbox6.text()
        saver[13] = self.textbox7.text()
        saver[14] = self.textbox8.text()
        print(saver)
        
    def PreviousSave(self):
        
        self.textbox_dil01.setText(saver[1])
        self.textbox_dil02.setText(saver[2])
        self.textbox_dil03.setText(saver[3])
        self.textbox_dil04.setText(saver[4])
        self.textbox1.setText(saver[5])
        self.textbox2.setText(saver[6])
        self.textbox3.setText(saver[7])
        self.textbox4.setText(saver[8])
        self.textbox11.setText(saver[9])
        self.textbox12.setText(saver[10])
        self.textbox5.setText(saver[11])
        self.textbox6.setText(saver[12])
        self.textbox7.setText(saver[13])
        self.textbox8.setText(saver[14])
        
        
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
            #Create plot of AL over energy range kspace over energy range and list reulsts table in last fig
            kspaceedges, atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols = fct.XASEZero(Sample,Enot)
            #ploting limits
            delta1 = float(self.textbox11.text())
            delta2 = float(self.textbox12.text())
            self.textbox_Xray_05.clear()
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
            #define blank y values to be populated by later functions
            y  = [None] * length
            y2  = [None] * length2
            y3 = [None] * length3
            
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
            axis[0].plot(x, y, color = 'g', linestyle= '-') #label="XXXX \nI am Trying To Add a New Line of Text"
            
            axis[0].set_xlabel(r"Photon Energy (eV)")
            axis[0].set_ylabel(r"$µ_{average}$ • Mass/Area")
            axis[1].set_xlim([0, fct.kspacecalc(delta2)])
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

    
    def clearDisplay(self):
        """Clear the input display."""
        self.textbox1.clear()
        self.textbox2.clear()
        self.textbox3.setText('2.5')
        self.combo.setCurrentIndex(0)
        self.b1.setChecked(False)
        self.b2.setChecked(False)
        self.textbox4.clear()
        self.textbox5.clear()
        self.textbox6.clear()
        self.textbox7.clear()
        self.textbox8.clear()
        self.textbox_Xray_05.clear()
        self.textbox11.setText('-200')
        self.textbox12.setText('1000')
        self.textbox13.setText('1')

    
        
        
        
        
    def openSampleBuilder(self):
        self.dialog = SampleBuilder(self)
        self.dialog.show()

    
  

  
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
        mainWin.show()
        app.exec_()
    run_app()