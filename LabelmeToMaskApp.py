import glob
import json
import os
import shutil
import sys
import time

import cv2
import labelme
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QObject
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QFileDialog, QProgressBar, QTextEdit

# 全局变量用于存储配置文件路径
CONFIG_FILE = 'LabelmeToMask.json'

suffixes = ['png', 'tif']


def gray_to_color_mask(gray_image):
    custom_colormap = np.zeros((6, 3), dtype=np.uint8)

    custom_colormap[0] = [0, 0, 0]
    custom_colormap[1] = [64, 64, 64]
    custom_colormap[2] = [129, 129, 129]
    custom_colormap[3] = [64, 255, 64]
    custom_colormap[4] = [255, 255, 255]
    custom_colormap[5] = [255, 129, 64]

    color_image = custom_colormap[gray_image]
    # color_image = cv2.applyColorMap(gray_image, cv2.COLORMAP_JET)
    # color_image = cv2.addWeighted(origin_image, 1, color_image, 1-alpha, 0)
    return color_image


class WorkerSignals(QObject):
    progress_updated = pyqtSignal(int)
    runtime_updated = pyqtSignal(float)
    operation_finished = pyqtSignal(str, float)
    operation_error = pyqtSignal(str)
    log_message = pyqtSignal(str)


class WorkerThread(QThread):
    def __init__(self, data_dir=None):
        super().__init__()
        self._is_running = True
        self.data_dir = data_dir
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.labelme_to_mask(self.data_dir)
        except Exception as e:
            self.signals.operation_error.emit(str(e))

    def labelme_to_mask(self, input_path):
        output_path = os.path.join(input_path, 'dataset')
        self.signals.log_message.emit(f"-" * 100)
        self.signals.log_message.emit(f"Converting {input_path} to {output_path}")
        if os.path.exists(output_path):
            self.signals.log_message.emit(f"Output directory {output_path} already exists. Deleting it...")
            shutil.rmtree(output_path)
        os.makedirs(output_path, exist_ok=True)
        class_name_to_id = {'gum': 0, '0': 1, '2': 2, '3': 3, '4': 4, '5': 5}

        json_file_names = sorted(glob.glob(os.path.join(input_path, '*.json')))
        self.signals.log_message.emit(f"Found {len(json_file_names)} json files in {input_path}")
        self.signals.log_message.emit(f"-" * 100)
        start_time = time.time()
        for i, file_name in enumerate(json_file_names):
            if not self._is_running:
                return
            suffix = next((s for s in suffixes if os.path.exists(file_name.replace('json', s))), "")
            base = os.path.splitext(os.path.basename(file_name))[0]
            out_img_file = os.path.join(output_path, f"{base}_image.png")
            out_mask_file = os.path.join(output_path, f"{base}_mask.png")

            label_file = labelme.LabelFile(filename=file_name)
            img = labelme.utils.img_data_to_arr(label_file.imageData)
            try:
                lbl, _ = labelme.utils.shapes_to_label(
                    img_shape=img.shape,
                    shapes=label_file.shapes,
                    label_name_to_value=class_name_to_id)
                mask = np.zeros_like(lbl)
                # mask[lbl == 0] = 129
                # mask[lbl == 1] = 0
                # mask[lbl == 2] = 255
                # mask[lbl == 3] = 192
                # mask[lbl == 4] = 64
                # mask[lbl == 5] = 32
                mask[lbl == 0] = 2
                mask[lbl == 1] = 0
                mask[lbl == 2] = 4
                mask[lbl == 3] = 3
                mask[lbl == 4] = 1
                mask[lbl == 5] = 5
                if 5 in mask:
                    mask = gray_to_color_mask(mask)
                    cv2.imencode(os.path.splitext(out_mask_file)[1], mask)[1].tofile(out_mask_file)
                    shutil.copy(file_name.replace('json', suffix),
                                os.path.join(output_path, os.path.basename(file_name.replace('json', suffix))))
                    shutil.copy(file_name, os.path.join(output_path, os.path.basename(file_name)))
                # cv2.imencode(os.path.splitext(out_mask_file)[1], mask)[1].tofile(out_mask_file)
                # shutil.copy(file_name.replace('json', suffix), out_img_file)

                elapsed_time = time.time() - start_time
                self.signals.runtime_updated.emit(elapsed_time)
                self.signals.progress_updated.emit(int((i + 1) / len(json_file_names) * 100))

            except Exception as e:
                self.signals.operation_error.emit(str(e))

        elapsed_time = time.time() - start_time
        self.signals.operation_finished.emit("Labelme to mask", elapsed_time)

    def stop(self):
        self._is_running = False


class LabelmeToMaskWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LabelmeToMask App")
        self.default_width = 800
        self.default_height = 350
        self.resize(self.default_width, self.default_height)
        self.center()

        self.data_dir = self.load_default_directory()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.directory_layout = QHBoxLayout()
        self.add_directory_input("Data Directory")

        self.add_buttons_and_output_panel()

        self.threads = {}

    def center(self):
        screen = QApplication.primaryScreen()
        screen_size = screen.availableSize()
        self.move((screen_size.width() - self.width()) // 2, (screen_size.height() - self.height()) // 2)

    def add_directory_input(self, label_text):
        label = QLabel(f"{label_text}:")
        self.directory_layout.addWidget(label)
        self.directory_input = QLineEdit(self.data_dir)
        self.directory_input.editingFinished.connect(self.save_default_directory)
        self.directory_layout.addWidget(self.directory_input)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        self.directory_layout.addWidget(browse_button)
        self.layout.addLayout(self.directory_layout)

    def add_buttons_and_output_panel(self):
        confirm_button = QPushButton("Confirm Directory")
        confirm_button.clicked.connect(self.confirm_directory)
        self.layout.addWidget(confirm_button)

        self.output_panel = QTextEdit()
        self.layout.addWidget(self.output_panel)

        operation_layout = QHBoxLayout()
        self.add_operation_buttons(operation_layout)
        self.layout.addLayout(operation_layout)

        delete_open_layout = self.create_delete_open_buttons()
        self.layout.addLayout(delete_open_layout)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(QApplication.instance().quit)
        self.layout.addWidget(exit_button)

        self.layout.addStretch()

    def add_operation_buttons(self, layout):
        button = QPushButton("Labelme to Mask")
        button.setFixedWidth(150)
        button.clicked.connect(self.perform_operation)
        layout.addWidget(button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_operation)
        layout.addWidget(self.stop_button)

        self.runtime_label = QLabel("0.00 s")
        layout.addWidget(self.runtime_label)

    def create_delete_open_buttons(self):
        buttons_layout = QHBoxLayout()

        delete_button = QPushButton("Delete Dataset")
        delete_button.clicked.connect(self.delete_dataset)
        buttons_layout.addWidget(delete_button)

        open_button = QPushButton("Open Dataset")
        open_button.clicked.connect(self.open_dataset)
        buttons_layout.addWidget(open_button)

        return buttons_layout

    def browse_directory(self):
        current_directory = self.directory_input.text()
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", parent_directory)
        if directory:
            self.directory_input.setText(directory)
            self.save_default_directory()

    def confirm_directory(self):
        for operation, thread in self.threads.items():
            if thread.isRunning():
                thread.stop()
                thread.wait()

        self.reset_operation_widgets()
        self.data_dir = self.directory_input.text()
        if not os.path.exists(self.data_dir):
            self.output_panel.append(f"Directory not found: {self.data_dir}")
            return
        self.output_panel.append(f"Current Directory:\nData Directory: {self.data_dir}")

    def perform_operation(self):
        self.reset_operation_widgets()

        thread = WorkerThread(data_dir=self.data_dir)
        thread.signals.progress_updated.connect(self.progress_bar.setValue)
        thread.signals.runtime_updated.connect(lambda runtime: self.runtime_label.setText(f"{runtime:.2f} s"))
        thread.signals.operation_finished.connect(self.operation_finished)
        thread.signals.operation_error.connect(self.handle_operation_error)
        thread.signals.log_message.connect(self.log_message)
        self.threads["Labelme to mask"] = thread
        thread.start()

    def stop_operation(self):
        thread = self.threads.get("Labelme to mask")
        if thread:
            thread.stop()
            self.operation_finished("Labelme to mask")

    def delete_dataset(self):
        dataset_dir = os.path.join(self.data_dir, 'dataset')
        if os.path.exists(dataset_dir):
            shutil.rmtree(dataset_dir)
            self.output_panel.append(f"Deleted directory: {dataset_dir}")
        else:
            self.output_panel.append(f"Directory not found: {dataset_dir}")

    def open_dataset(self):
        dataset_dir = os.path.join(self.data_dir, 'dataset')
        if os.path.exists(dataset_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dataset_dir))
        else:
            self.output_panel.append(f"Directory not found: {dataset_dir}")

    def operation_finished(self, operation, runtime):
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)
        # self.reset_operation_widgets()
        self.output_panel.append(f"{operation} finished in {runtime:.2f} seconds")

    def handle_operation_error(self, error_message):
        self.output_panel.append(f"Error: {error_message}")

    def log_message(self, message):
        self.output_panel.append(message)

    def reset_operation_widgets(self):
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

    def load_default_directory(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config.get("default_directory", "")
        except FileNotFoundError:
            return ""

    def save_default_directory(self):
        config = {"default_directory": self.directory_input.text()}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabelmeToMaskWindow()
    window.show()
    app.aboutToQuit.connect(window.save_default_directory)
    sys.exit(app.exec_())
