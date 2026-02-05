import time
import numpy as np
import cv2

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QSizePolicy, QPushButton, QHBoxLayout, QLayout
from PySide6.QtGui import QImage, QPixmap, QScreen
from PySide6.QtMultimedia import QCamera, QVideoSink, QMediaCaptureSession, QVideoFrame
from PySide6.QtCore import Qt

from yolo_worker import YoloWorker

model_path = "yolo_trained_models/yolo11s_best_t2.pt"

class CameraWindow(QWidget):
    def __init__(self, main_win, camera_device):
        self.main_win = main_win
        super().__init__()

        self.setWindowTitle(f"Yolo detection on camera {camera_device.description()}")

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.btn_camera = QPushButton("Start Camera")
        self.btn_camera.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.btn_camera.clicked.connect(self.init_camera)

        btnGoBack = QPushButton("Go Back")
        btnGoBack.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        btnGoBack.clicked.connect(self.goBack)

        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(self.btn_camera)
        hbox_btns.addWidget(btnGoBack)

        vboxlay_lbl = QVBoxLayout()
        vboxlay_lbl.addWidget(self.label)

        fr_hbox_btns = QFrame()
        fr_hbox_btns.setLayout(vboxlay_lbl)

        layout = QVBoxLayout(self)
        layout.addWidget(fr_hbox_btns)
        layout.addLayout(hbox_btns)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        

        # -----------------
        # FPS tracking
        # -----------------
        self.last_time = time.time()
        self.fps = 0

        # -----------------
        # Camera setup
        # -----------------
        #camera_device = QMediaDevices.defaultVideoInput()
        self.camera = QCamera(camera_device)
        self.camera_on = False

        self.captureSession = QMediaCaptureSession()
        self.captureSession.setCamera(self.camera)

        self.sink = QVideoSink()
        self.captureSession.setVideoSink(self.sink)

        self.sink.videoFrameChanged.connect(self.process_frame)

        # -----------------
        # YOLO worker
        # -----------------
        self.worker = YoloWorker(model_path)
        self.worker.frame_processed.connect(self.update_display)
        self.worker.start()

        

    def init_camera(self):
        if not self.camera_on:
            self.camera_on = True
            self.camera.start()
            self.btn_camera.setText("Stop camera")
            self.showFullScreen()
        
        elif self.camera_on:
            self.camera_on = False
            self.camera.stop()
            self.btn_camera.setText("Start camera")

    def goBack(self):
        self.worker.stop()
        self.camera.stop()
        self.main_win.show()
        self.close()

    # -------------------------------------------------
    # Convert QVideoFrame -> numpy
    # -------------------------------------------------
    def process_frame(self, frame = QVideoFrame()):

        if not frame.isValid():
            return

        frame = frame.toImage()

        print(f"W:{frame.width()}, H:{frame.height()}, Color:{frame.hasAlphaChannel()}")

        frame = frame.convertToFormat(QImage.Format.Format_RGB888)

        w = frame.width()
        h = frame.height()

        ptr = frame.bits()
        arr = np.array(ptr).reshape((h, w, 3))

        arr = cv2.resize(arr, (960, 540)) # Resize the image for constant inference size.

        # convert to BGR for YOLO/OpenCV
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

        self.worker.set_frame(arr)

    # -------------------------------------------------
    # Receive annotated frame from YOLO
    # -------------------------------------------------
    def update_display(self, frame, infer_time):

        # FPS calc
        now = time.time()
        self.fps = 1.0 / (now - self.last_time)
        self.last_time = now

        # draw FPS text
        cv2.putText(
            frame,
            f"FPS: {self.fps:.1f}  Infer: {infer_time*1000:.1f}ms",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape

        img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)

        pix = QPixmap.fromImage(img)
        self.label.setPixmap(
            pix.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

    def closeEvent(self, event):
        self.worker.stop()
        self.camera.stop()
        event.accept()
