from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QWidget, QLabel, QSizePolicy, QPushButton, QFrame,
                               QListWidget, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaDevices

from cameraWindow import CameraWindow

class YoloMainWindow(QWidget):

    def __init__(self, app):
        self.app = app
        super().__init__()

        self.setWindowTitle("YOLO object detection of clothes")

        lblYOLO = QLabel("YOLO object detection of clothes")
        lblYOLO.setAlignment(Qt.AlignmentFlag.AlignTop)
        lblYOLO.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        hr_line = QFrame()
        hr_line.setFrameShape(QFrame.Shape.HLine)

        lblListDevices = QLabel("List of available cameras:")
        lblListDevices.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lblListDevices.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.mediaDevices = QMediaDevices()
        list_mediaDevices = self.mediaDevices.videoInputs()
        self.mediaDevices.videoInputsChanged.connect(self.update_listDevices)
        
        self.listWidget = QListWidget()
        for camera in list_mediaDevices:
            self.listWidget.addItem(camera.description())

        layout_vbx_list = QVBoxLayout()
        layout_vbx_list.addWidget(lblListDevices)
        layout_vbx_list.addWidget(self.listWidget)

        boxfr_list = QFrame()
        boxfr_list.setLayout(layout_vbx_list)

        btnStartCamera = QPushButton("Select Camera")
        btnStartCamera.clicked.connect(self.start_cameraWindow)
        btnStartCamera.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        btnClose = QPushButton("Close App")
        btnClose.clicked.connect(self.closeApp)
        btnClose.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout_hbx_btn = QHBoxLayout()
        layout_hbx_btn.addWidget(btnStartCamera)
        layout_hbx_btn.addWidget(btnClose)

        main_layout = QVBoxLayout()
        main_layout.addWidget(lblYOLO)
        main_layout.addWidget(hr_line)
        main_layout.addWidget(boxfr_list)
        main_layout.addLayout(layout_hbx_btn)

        self.setLayout(main_layout)


    def update_listDevices(self):
        items = self.listWidget.items
        for camera in self.mediaDevices.videoInputs():
            item = self.listWidget.findItems(camera.description(), Qt.MatchFlag.MatchFixedString)
            if len(item) == 0:
                self.listWidget.addItem(camera.description())
    
    def start_cameraWindow(self):
        sel_camera = self.listWidget.currentItem()

        camera_device = None
        for camera in self.mediaDevices.videoInputs():
            if camera.description() == sel_camera.text():
                camera_device = camera
                break

        if camera_device:
            self.cameraWindow = CameraWindow(self, camera_device)
            self.cameraWindow.showFullScreen()
            self.close()
        
        else:
            QMessageBox.warning(self, "Warning", "Please select a camera device for continuing!")


    def closeApp(self):
        self.app.quit()


        