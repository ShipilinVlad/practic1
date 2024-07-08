# Вариант №28

import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel,
                               QFileDialog, QMessageBox, QComboBox,
                               QInputDialog)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.image = None
        self.modified_image = None

    def initUI(self):
        self.setWindowTitle('Image Processor')
        self.setGeometry(100, 100, 600, 700)

        layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.image_label.setFixedHeight(600)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.size_label = QLabel(self)
        layout.addWidget(self.size_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()

        load_button = QPushButton('Load Image', self)
        load_button.clicked.connect(self.load_image)
        button_layout.addWidget(load_button)

        webcam_button = QPushButton('Capture from Webcam', self)
        webcam_button.clicked.connect(self.capture_from_webcam)
        button_layout.addWidget(webcam_button)

        layout.addLayout(button_layout)

        self.color_combo = QComboBox(self)
        self.color_combo.addItems(["Original", "Red Channel", "Green Channel", "Blue Channel"])
        self.color_combo.currentIndexChanged.connect(self.change_color_channel)
        layout.addWidget(self.color_combo, alignment=Qt.AlignCenter)

        operation_layout = QHBoxLayout()

        crop_button = QPushButton('Crop Image', self)
        crop_button.clicked.connect(self.crop_image)
        operation_layout.addWidget(crop_button)

        draw_button = QPushButton('Draw Circle', self)
        draw_button.clicked.connect(self.draw_circle)
        operation_layout.addWidget(draw_button)

        blur_button = QPushButton('Blur Image', self)
        blur_button.clicked.connect(self.blur_image)
        operation_layout.addWidget(blur_button)

        save_button = QPushButton('Save Image', self)
        save_button.clicked.connect(self.save_image)
        operation_layout.addWidget(save_button)

        layout.addLayout(operation_layout)

        self.setLayout(layout)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image', os.getenv('HOME'), 'Images (*.png *.jpg)')
        if file_name:
            self.image = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.modified_image = self.image.copy()
            self.display_image()

    def capture_from_webcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.critical(self, "Error", "Unable to access the webcam.")
            return

        ret, frame = cap.read()
        if ret:
            self.image = frame
            self.modified_image = self.image.copy()
            self.display_image()
        else:
            QMessageBox.critical(self, "Error", "Failed to capture image from webcam.")
        cap.release()

    def display_image(self, image=None):
        if image is None:
            image = self.modified_image

        if image is not None:
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation))

            self.size_label.setText(f'Image size: {width} x {height}')

    def change_color_channel(self):
        if self.modified_image is None:
            return

        index = self.color_combo.currentIndex()
        if index == 0:  # Original
            self.display_image(self.modified_image)
        elif index == 1:  # Red Channel
            red_channel = self.modified_image.copy()
            red_channel[:, :, 0] = 0
            red_channel[:, :, 1] = 0
            self.display_image(red_channel)
        elif index == 2:  # Green Channel
            green_channel = self.modified_image.copy()
            green_channel[:, :, 0] = 0
            green_channel[:, :, 2] = 0
            self.display_image(green_channel)
        elif index == 3:  # Blue Channel
            blue_channel = self.modified_image.copy()
            blue_channel[:, :, 1] = 0
            blue_channel[:, :, 2] = 0
            self.display_image(blue_channel)

    def crop_image(self):
        if self.modified_image is None:
            return

        x, ok = QInputDialog.getInt(self, 'Input', 'X coordinate:')
        if not ok:
            return
        y, ok = QInputDialog.getInt(self, 'Input', 'Y coordinate:')
        if not ok:
            return
        width, ok = QInputDialog.getInt(self, 'Input', 'Width:')
        if not ok:
            return
        height, ok = QInputDialog.getInt(self, 'Input', 'Height:')
        if not ok:
            return

        if x < 0 or y < 0 or x + width > self.modified_image.shape[1] or y + height > self.modified_image.shape[0]:
            QMessageBox.critical(self, "Error", "Crop dimensions exceed image bounds.")
            return

        cropped_image = self.modified_image[y:y+height, x:x+width].copy()
        self.modified_image = np.ascontiguousarray(cropped_image)
        self.display_image()

    def draw_circle(self):
        if self.modified_image is None:
            return

        x, ok = QInputDialog.getInt(self, 'Input', 'X coordinate of center:')
        if not ok:
            return
        y, ok = QInputDialog.getInt(self, 'Input', 'Y coordinate of center:')
        if not ok:
            return
        radius, ok = QInputDialog.getInt(self, 'Input', 'Radius:')
        if not ok:
            return
        thickness, ok = QInputDialog.getInt(self, 'Input', 'Thickness:')
        if not ok:
            return

        cv2.circle(self.modified_image, (x, y), radius, (0, 0, 255), thickness)
        self.display_image()

    def blur_image(self):
        if self.modified_image is None:
            return

        kernel_size, ok = QInputDialog.getInt(self, 'Input', 'Kernel size (odd number):')
        if not ok:
            return

        if kernel_size % 2 == 0:
            QMessageBox.critical(self, "Error", "Kernel size must be an odd number.")
            return

        self.modified_image = cv2.GaussianBlur(self.modified_image, (kernel_size, kernel_size), 0)
        self.display_image()

    def save_image(self):
        if self.modified_image is None:
            return

        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Image', os.getenv('HOME'), 'Images (*.png *.jpg)')
        if file_name:
            ext = os.path.splitext(file_name)[1]
            if ext.lower() not in ['.png', '.jpg', '.jpeg']:
                QMessageBox.critical(self, "Error", "Invalid file extension. Please use .png or .jpg.")
                return
            success, encoded_image = cv2.imencode(ext, self.modified_image)
            if success:
                with open(file_name, 'wb') as f:
                    f.write(encoded_image)
            else:
                QMessageBox.critical(self, "Error", "Failed to save image.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessor()
    ex.show()
    sys.exit(app.exec())
