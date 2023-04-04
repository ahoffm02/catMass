""" Run the viewer """
#
import sys

from PyQt5.QtWidgets import QApplication

import src.viewer as viewer

def main():
    # Create an instance of `QApplication`
    app = QApplication(sys.argv)
    # Show the calculator's GUI
    mainWin = viewer.XASCalcUI()
    mainWin.show()
    app.exec_()

if __name__ == "__main__":
    main()
