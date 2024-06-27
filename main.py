from LabelmeToMaskApp import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabelmeToMaskWindow()
    window.show()
    app.aboutToQuit.connect(window.save_default_directories)
    sys.exit(app.exec_())
