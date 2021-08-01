# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 22:18:20 2021

@author: ashoff
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
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTabWidget

from PyQt5.QtGui import QIcon


### How do I call this?
from src import functions as fct


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
        self.width = 640
        self.height = 480
        
        # Set main window's properties
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Set the central widgetand general layout
        self.generalLayout = QVBoxLayout()
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
        DilutionLayout.addWidget(self.label_dil00, 0, 0, 1, 2)
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
        # Create Button to Reset all Text Fields
        self.button_dil00 = QPushButton('Sample Builder')
        DilutionLayout.addWidget(self.button_dil00, 0, 2)
        self.generalLayout.addLayout(DilutionLayout)
        self.button_dil00.clicked.connect(self.openSampleBuilder)
        
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
        self.label4.setAlignment(Qt.AlignRight)
        InputLayout.addWidget(self.label4, 4, 0)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Lable for Desired Area
        self.label5 = QLabel('Sample Area Perpendicular to Beam [cm<sup>2</sup>]:')
        self.label5.setAlignment(Qt.AlignRight)
        InputLayout.addWidget(self.label5, 5, 0)
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
        
        # Create Editable Textbox for Desired Area
        self.textbox4 = QLineEdit()
        self.textbox4.setPlaceholderText('Sample Area')
        self.textbox4.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox4, 5, 1)
        self.generalLayout.addLayout(InputLayout)
        
        # Create Editable Textbox for Diagnostics
        self.textbox_Xray_05 = QLineEdit()
        self.textbox_Xray_05.setPlaceholderText('Diagnostics')
        self.textbox_Xray_05.setAlignment(Qt.AlignCenter)
        #self.textbox5.setFixedSize(150, 35)
        InputLayout.addWidget(self.textbox_Xray_05, 7, 0, 1, 2)
        self.generalLayout.addLayout(InputLayout)
        
        '''Buttons'''
        #Create Reset Button to Clear X-ray Input Field
        self.button_Input01 = QPushButton('Reset')
        InputLayout.addWidget(self.button_Input01, 6, 0)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input01.clicked.connect(self.clearDisplay)
        
        #Create Button to Calcualte sample mass and step
        self.button_Input02 = QPushButton('Calculate Sample Mass')
        InputLayout.addWidget(self.button_Input02 ,6, 1)
        self.generalLayout.addLayout(InputLayout)
        self.button_Input02.clicked.connect(self.calculateResult)
        
               
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
        
        Result, Enot, ms, stp = fct.XASMassCalc(Sample, Element, Edge, Area, AL)
        
        if 'ERROR' in Result:
            self.textbox_Xray_05.setText(Result)
        else:
            self.textbox5.setText('{0:0.2f}'.format(ms))
            self.textbox6.setText('{0:0.2f}'.format(stp))
            self.textbox7.setText('{0:0.2f}'.format(ms*MF_Samp))
            self.textbox8.setText('{0:0.2f}'.format(ms*MF_Dil))
            self.textbox9.setText('{0:0.0f}'.format(Enot))
            self.textbox_Xray_05.clear()

            
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
        self.textbox3.clear()
        self.combo.setCurrentIndex(0)
        self.textbox4.clear()
        self.textbox5.clear()
        self.textbox6.clear()
        self.textbox7.clear()
        self.textbox8.clear()
        self.textbox_Xray_05.clear()
        

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
        
        
        """Buttons"""
        self.button_tab1_01 = QPushButton("Update Sample")
        Tab1Layout.addWidget(self.button_tab1_01, 5, 1)
        self.tab1.setLayout(Tab1Layout)
        self.button_tab1_01.clicked.connect(self.UpdateSampleMetal)
        
 
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
        
        
        """Buttons"""
        self.button_tab2_01 = QPushButton("Update Sample")
        Tab2Layout.addWidget(self.button_tab2_01, 5, 1)
        self.tab2.setLayout(Tab2Layout)
        self.button_tab2_01.clicked.connect(self.UpdateSampleComplex)
                

        
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        
        
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