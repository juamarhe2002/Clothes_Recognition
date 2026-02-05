from PySide6.QtCore import QThread, Signal
from ultralytics import YOLO
import cv2
import time


class YoloWorker(QThread):
    frame_processed = Signal(object, float)  # frame + inference time

    def __init__(self, model_path):
        super().__init__()
        self.model = YOLO(model_path)
        self.frame = None
        self.running = True

    def set_frame(self, frame):
        self.frame = frame

    def run(self):
        while self.running:
            if self.frame is None:
                continue

            frame = self.frame.copy()
            self.frame = None

            t0 = time.time()

            results = self.model(frame, verbose=False)[0]
            annotated = results.plot() # Draws the boxes on the images

            infer_time = time.time() - t0

            self.frame_processed.emit(annotated, infer_time)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
