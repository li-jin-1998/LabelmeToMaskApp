import sys
from PyQt5.QtWidgets import QApplication
from LabelmeToMaskApp import LabelmeToMaskWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabelmeToMaskWindow()
    window.show()
    app.aboutToQuit.connect(window.save_default_directory)
    sys.exit(app.exec_())
