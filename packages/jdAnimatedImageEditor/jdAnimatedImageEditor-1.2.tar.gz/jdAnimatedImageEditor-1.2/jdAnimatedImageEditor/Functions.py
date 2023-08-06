from PyQt6.QtWidgets import QTableWidget, QApplication, QComboBox, QMessageBox
from PyQt6.QtCore import QObject, QCoreApplication
from typing import Optional, Any
import urllib.parse
import traceback
import PIL.Image
import tempfile
import random
import json
import sys
import os


def get_logical_table_row_list(table: QTableWidget) -> list[int]:
    """Returns a List of the row indexes in the order they appear in the table"""
    index_list = []
    header = table.verticalHeader()
    for i in range(table.rowCount()):
        index_list.append(header.logicalIndex(i))
    return index_list

def clear_table_widget(table: QTableWidget):
    """Removes all Rows from a QTableWidget"""
    while table.rowCount() > 0:
        table.removeRow(0)


def is_url(text: str) -> bool:
    "Checks if the given text is a URL"
    result = urllib.parse.urlparse(text)
    if result.scheme not in ("http", "https"):
        return False
    if result.netloc == "":
        return False
    return True


def get_url_from_clipboard() -> str:
    """If the Clipboard has a URL return it. Otherwise return a empty string."""
    if is_url(QApplication.clipboard().text()):
        return QApplication.clipboard().text()
    else:
        return ""


def select_combo_box_data(box: QComboBox, data: Any, default_index: int = 0) -> None:
    """Set the index to the item with the given data"""
    index = box.findData(data)
    if index == -1:
        box.setCurrentIndex(default_index)
    else:
        box.setCurrentIndex(index)


def read_json_file(path: str, default: Any) -> Any:
    """Tries to read a JSON file"""
    if not os.path.isfile(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        QMessageBox.critical(None, QCoreApplication.translate("Functions", "Can't parse JSON"), QCoreApplication.translate("Functions", "Can't parse {{path}}. Using default data.").replace("{{path}}", path))
        print(traceback.format_exc(), end="", file=sys.stderr)
        return default


def remove_list_duplicates(old_list: list[Any]) -> list[Any]:
    """Removes all duplicates from a list"""
    new_list = []

    for i in old_list:
        if i not in new_list:
            new_list.append(i)

    return new_list


def get_sender_table_row(table: QTableWidget, column: int, sender: QObject) -> int:
    """Get the Row in a QTableWidget that contains the Button that was clicked"""
    for i in range(table.rowCount()):
        if table.cellWidget(i, column) == sender:
            return i


def get_pillow_file_extensions(pillow_format: str) -> list[str]:
    """Get a List with all File extenstions of a Format in Pillow"""
    extension_list = []
    for key, value in PIL.Image.EXTENSION.items():
        if value == pillow_format:
            extension_list.append(key)
    return extension_list


def get_qt_file_filter(file_formats: list, all_text: Optional[str] = None) -> str:
    """Creates a filter for QFileDialog with the list og the file formats"""
    if len(file_formats) == 0:
        return QCoreApplication.translate("Functions", "All Files") + " (*)"

    filter_string = ""

    if not all_text:
        filter_string += QCoreApplication.translate("Functions", "All Files") + " (*);;"

    extension_list = []
    for file_format in file_formats:
        filter_string += file_format[0] + " ("
        for extension in file_format[1]:
            filter_string += f"*{extension} "
            extension_list.append(extension)
        filter_string = filter_string[:-1] + ");;"

    if all_text:
        all_filter = all_text + " ("
        for extension in extension_list:
            all_filter += f"*{extension} "
        filter_string = all_filter[:-1] + ");;" + filter_string
        filter_string += QCoreApplication.translate("Functions", "All Files") + " (*);;"

    return filter_string[:-2]


def get_temp_path(name_template: str) -> str:
    """Checks if the given temp path exists, if not return them"""
    while True:
        temp_path = os.path.join(tempfile.gettempdir(), name_template.replace("{{random}}", str(random.randrange(100000))))
        if not os.path.exists(temp_path):
            return temp_path


def is_flatpak() -> bool:
    """Checks is the Program runs as Flatpak"""
    return os.path.isfile("/.flatpak-info")
