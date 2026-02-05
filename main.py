from PySide6.QtWidgets import QApplication
import sys

from mainWindow import YoloMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = YoloMainWindow(app)
    win.show()
    sys.exit(app.exec())