from .Functions import get_logical_table_row_list, clear_table_widget, get_url_from_clipboard, get_sender_table_row, get_pillow_file_extensions, get_qt_file_filter, get_temp_path
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QFileDialog, QMessageBox, QInputDialog, QHeaderView
from PyQt6.QtCore import QCoreApplication, QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap, QMovie, QAction
from .SettingsDialog import SettingsDialog
from .AboutDialog import AboutDialog
from typing import Optional
import PIL.ImageSequence
from PyQt6 import uic
import PIL.ImageDraw
import PIL.Image
import traceback
import requests
import shutil
import sys
import io
import os


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)

        self._image = None

    def set_image(self, image_bytes: bytes) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        self.setPixmap(pixmap)
        self._image = PIL.Image.open(io.BytesIO(image_bytes))

    def get_image(self) -> Optional[PIL.Image.Image]:
        return self._image.copy()


class MainWindow(QMainWindow):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "MainWindow.ui"), self)

        self._env = env
        self._modified = False
        self._current_path = None

        self._settings_dialog = SettingsDialog(env, self)
        self._about_dialog = AboutDialog(env)

        self._reset_all()
        self._update_preview()
        self._update_recent_files_menu()
        self._update_save_actions_enabled()

        self.image_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.new_action.triggered.connect(lambda: self._ask_for_save() and self._reset_all())
        self.open_action.triggered.connect(self._open_action_clicked)
        self.save_action.triggered.connect(self._save_action_clicked)
        self.save_as_action.triggered.connect(self._save_with_dialog)
        self.exit_action.triggered.connect(lambda: self._ask_for_save() and sys.exit(0))

        self.import_video_action.triggered.connect(self._import_video_clicked)
        self.export_video_action.triggered.connect(self._export_video_clicked)

        self.settings_action.triggered.connect(self._settings_dialog.open_dialog)

        self.about_action.triggered.connect(self._about_dialog.exec)
        self.about_qt_action.triggered.connect(QApplication.instance().aboutQt)

        self.image_add_file_button.clicked.connect(self._image_add_file_button_clicked)
        self.image_add_url_button.clicked.connect(self._image_add_url_button_clicked)

        self.duration_spin_box.valueChanged.connect(lambda: (self._update_preview(), self.set_modified(True)))

    def set_modified(self, modified: bool) -> None:
        self._modified = modified
        self.update_window_title()

    def update_window_title(self):
        if self._env.settings.get("windowTitleType") == "programName":
            self.setWindowTitle("jdAnimatedImageEditor")
        elif self._env.settings.get("windowTitleType") == "fileName":
            self.setWindowTitle(os.path.basename(self._current_path or QCoreApplication.translate("MainWindow", "Untitled")) + " - jdAnimatedImageEditor")
        elif self._env.settings.get("windowTitleType") == "filePath":
            self.setWindowTitle((self._current_path or QCoreApplication.translate("MainWindow", "Untitled")) + " - jdAnimatedImageEditor")

        if self._modified and self._env.settings.get("windowTitleFileModified"):
            self.setWindowTitle("*" + self.windowTitle())

    def _update_save_actions_enabled(self):
        enabled = self.image_table.rowCount() > 0
        self.save_action.setEnabled(enabled)
        self.save_as_action.setEnabled(enabled)
        self.export_video_action.setEnabled(enabled)

    def _ask_for_save(self) -> bool:
        if not self._modified:
            return True
        if not self._env.settings.get("checkSaveBeforeClosing"):
            return True
        answer = QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Unsaved changes"), QCoreApplication.translate("MainWindow", "You have unsaved changes. Do you want to save now?"), QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Save:
            self._save_action_clicked()
            return True
        elif answer == QMessageBox.StandardButton.Discard:
            return True
        elif answer == QMessageBox.StandardButton.Cancel:
            return False

    def _reset_all(self) -> None:
        clear_table_widget(self.image_table)
        self.width_spin_box.setValue(150)
        self.height_spin_box.setValue(150)
        self.duration_spin_box.setValue(1)

        self.set_modified(False)
        self._update_preview()
        self._update_save_actions_enabled()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()

        if len(self._env.recent_files) == 0:
            empty_action = QAction(QCoreApplication.translate("MainWindow", "No recent files"), self)
            empty_action.setEnabled(False)
            self.recent_files_menu.addAction(empty_action)
            return

        for i in self._env.recent_files:
            file_action = QAction(i, self)
            file_action.setData(i)
            file_action.triggered.connect(self._open_recent_file)
            self.recent_files_menu.addAction(file_action)

        self.recent_files_menu.addSeparator()

        clear_action = QAction(QCoreApplication.translate("MainWindow", "Clear"), self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_files_menu.addAction(clear_action)

    def _open_recent_file(self):
        action = self.sender()
        if not action:
            return

        if not self._ask_for_save():
            return

        self.open_file(action.data())

    def _clear_recent_files(self):
        self._env.recent_files.clear()
        self._update_recent_files_menu()
        self._env.save_recent_files()

    def _open_action_clicked(self):
        if not self._ask_for_save():
            return

        path = QFileDialog.getOpenFileName(self)[0]
        if path != "":
            self.open_file(path)

    def open_file(self, path: str) -> bool:
        try:
            img = PIL.Image.open(path)
        except PIL.UnidentifiedImageError:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Not an Image"), QCoreApplication.translate("MainWindow", "The given File is not an Image"))
            return
        except FileNotFoundError:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "File not found"), QCoreApplication.translate("MainWindow", "The given File does not exists"))
            return

        self._reset_all()

        for i in PIL.ImageSequence.Iterator(img):
            by = io.BytesIO()
            i.save(by, format="PNG")
            by.seek(0)
            self._add_frame_image(by.read())

        self.width_spin_box.setValue(img.size[0])
        self.height_spin_box.setValue(img.size[1])
        self.duration_spin_box.setValue(img.info.get("duration", 1000) / 1000)
        self._current_path = path
        self.set_modified(False)
        self._update_preview()

        self._env.add_to_recent_files(path)
        self._update_recent_files_menu()

    def _save_with_dialog(self):
        format_list = [["GIF", [".gif"]], ["APNG", [".png", ".apng"]]]
        path = QFileDialog.getSaveFileName(self, filter=get_qt_file_filter(format_list))[0]

        if path != "":
            self.save_file(path)

    def _save_action_clicked(self):
        if self._current_path is None:
            self._save_with_dialog()
        else:
            self.save_file(self._current_path)

    def save_file(self, path: str, file_format: Optional[str] = None, set_modified: bool = True) -> None:
        if not file_format:
            if path.lower().endswith(".gif"):
                file_format = "GIF"
            elif path.lower().endswith(".png") or path.lower().endswith(".apng"):
                file_format = "PNG"
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Unsupported Format"), QCoreApplication.translate("MainWindow", "The given format is not supported for saving animated Images"))
                return

        by = self.get_animated_image(file_format=file_format)
        with open(path, "wb") as f:
            f.write(by)

        if set_modified:
            self._current_path = path
            self.set_modified(False)
            self._env.add_to_recent_files(path)
            self._update_recent_files_menu()

    def _check_ffmpeg_installed(self) -> bool:
        if self._env.ffmpeg_handler.is_ffmpeg_installed():
            return True
        else:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "FFmpeg not found"), QCoreApplication.translate("MainWindow", "FFmpeg was not found. If you have a custom location, you can set it in the Settings."))
            return False

    def _import_video_clicked(self):
        if not self._check_ffmpeg_installed():
            return

        if not self._ask_for_save():
            return

        path = QFileDialog.getOpenFileName(self)[0]

        if path == "":
            return

        temp_path = get_temp_path("jdAnimatedImageEditor_import_{{random}}")

        os.makedirs(temp_path)

        result = self._env.ffmpeg_handler.execute_ffmpeg_command(["-i", path, "-vf", "fps=1", os.path.join(temp_path, "%06d.png")])

        if result.returncode != 0:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Import failed"), QCoreApplication.translate("MainWindow", "The import of {{path}} failed. Maybe your FFmpeg version can't decode this video.").replace("{{path}}", path))
            shutil.rmtree(temp_path)
            return

        self._reset_all()

        for i in os.listdir(temp_path):
            with open(os.path.join(temp_path, i), "rb") as f:
                self._add_frame_image(f.read())

        shutil.rmtree(temp_path)

        self._current_path = None
        self.set_modified(False)

    def _export_video_clicked(self):
        if not self._check_ffmpeg_installed():
            return

        path = QFileDialog.getSaveFileName(self)[0]

        if path == "":
            return

        if path.lower().split(".")[-1] in ["gif", "png", "apng"]:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Not a Video"),  QCoreApplication.translate("MainWindow", "This function is for exporting Videos, not Images. If you want to save as a Image, use File>Save."))
            return

        temp_path = get_temp_path("jdAnimatedImageEditor_export_{{random}}.gif")
        self.save_file(temp_path, file_format="GIF", set_modified=False)

        result = self._env.ffmpeg_handler.execute_ffmpeg_command(["-i", temp_path, "-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-y", path])

        os.remove(temp_path)

        if result.returncode == 0:
            QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Export finished"), QCoreApplication.translate("MainWindow", "The export has been finished"))
        else:
            QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Export failed"), QCoreApplication.translate("MainWindow", "The export has been failed. Maybe your FFmpeg version can't encode to the given format."))

    def _add_frame_image(self, img: bytes):
        row = self.image_table.rowCount()
        self.image_table.insertRow(row)

        label = ImageLabel()
        label.set_image(img)
        self.image_table.setCellWidget(row, 0, label)

        remove_button = QPushButton(QCoreApplication.translate("MainWindow", "Remove"))
        remove_button.clicked.connect(self._remove_frame_clicked)
        self.image_table.setCellWidget(row, 1, remove_button)

        export_button = QPushButton(QCoreApplication.translate("MainWindow", "Export"))
        export_button.clicked.connect(self._export_frame_clicked)
        self.image_table.setCellWidget(row, 2, export_button)

        if self.image_table.rowCount() == 1:
            self.width_spin_box.setValue(label.get_image().size[0])
            self.height_spin_box.setValue(label.get_image().size[1])

        self._update_save_actions_enabled()

    def _remove_frame_clicked(self):
        row = get_sender_table_row(self.image_table, 1, self.sender())
        self.image_table.removeRow(row)
        self.set_modified(True)

        self._update_save_actions_enabled()

    def _export_frame_clicked(self):
        row = get_sender_table_row(self.image_table, 2, self.sender())

        format_list = []
        for i in PIL.Image.SAVE.keys():
            format_list.append([i, get_pillow_file_extensions(i)])

        path, ok = QFileDialog.getSaveFileName(self, caption=QCoreApplication.translate("MainWindow", "Export Image"), filter=get_qt_file_filter(format_list, QCoreApplication.translate("MainWindow", "All Imageformats")))

        if path == "":
            return

        img = self.image_table.cellWidget(row, 0).get_image()

        try:
            img.save(path)
        except ValueError:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Unsupported Fileformat"), QCoreApplication.translate("MainWindow", "The given extension is not supported"))
        except Exception:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Error"), QCoreApplication.translate("MainWindow", "A Error occurred while trying to export the Image"))

    def _image_add_file_button_clicked(self):
        format_list = []
        for i in PIL.Image.OPEN.keys():
            format_list.append([i, get_pillow_file_extensions(i)])

        for i in QFileDialog.getOpenFileNames(self, filter=get_qt_file_filter(format_list, QCoreApplication.translate("MainWindow", "All Imageformats")))[0]:
            with open(i, "rb") as f:
                image_bytes = f.read()

            try:
                PIL.Image.open(io.BytesIO(image_bytes))
            except PIL.UnidentifiedImageError:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Not an Image"), QCoreApplication.translate("MainWindow", "{{path}} is not an Image").replace("{{path}}", i))
                continue

            self._add_frame_image(image_bytes)

        self._update_preview()
        self.set_modified(True)

    def _image_add_url_button_clicked(self):
        url = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Enter URL"), QCoreApplication.translate("MainWindow", "Please enter the URL to the Image"), text=get_url_from_clipboard())[0]

        if url == "":
            return

        try:
            image_bytes = requests.get(url, stream=True).raw.read()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Error"), QCoreApplication.translate("MainWindow", "The Image could not been downloaded"))
            return

        try:
            PIL.Image.open(io.BytesIO(image_bytes))
        except PIL.UnidentifiedImageError:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Invalid Image"), QCoreApplication.translate("MainWindow", "The Image is not valid"))
            return

        self._add_frame_image(image_bytes)
        self._update_preview()

    def _update_preview(self) -> None:
        """Updates the preview label with the current Image
        The variables must be in class or it will crash.
        Source: https://stackoverflow.com/questions/30895402/loading-animated-gif-data-in-qmovie"""
        if self.image_table.rowCount() == 0:
            self.preview_label.setMovie(QMovie())
            self.preview_label.setText(QCoreApplication.translate("MainWindow", "A preview of your animated image will be displayed here"))
            return

        self._movie_byte_array = QByteArray(self.get_animated_image(file_format="GIF"))
        self._movie_buffer = QBuffer(self._movie_byte_array)
        self._movie_buffer.open(QIODevice.OpenModeFlag.ReadOnly)

        self._preview_movie = QMovie()
        self._preview_movie.setDevice(self._movie_buffer)
        self.preview_label.setMovie(self._preview_movie)
        self._preview_movie.start()

    def get_animated_image(self, file_format: str) -> bytes:
        image_list = []

        for i in get_logical_table_row_list(self.image_table):
            image_list.append(self.image_table.cellWidget(i, 0).get_image().resize((self.width_spin_box.value(), self.height_spin_box.value())))

        by = io.BytesIO()
        image_list[0].save(by, format=file_format, append_images=image_list[1:], save_all=True, duration=self.duration_spin_box.value() * 1000, loop=0)
        by.seek(0)

        return by.read()

    def closeEvent(self, event):
        if self._ask_for_save():
            event.accept()
        else:
            event.ignore()
