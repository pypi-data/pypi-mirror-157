from .Functions import read_json_file, remove_list_duplicates
from .FFmpegHandler import FFmpegHandler
from .Settings import Settings
from PyQt6.QtGui import QIcon
from pathlib import Path
import argparse
import platform
import json
import os


class Environment:
    def __init__(self):
        self.program_dir = os.path.dirname(__file__)
        self.data_dir = self._get_data_path()

        parser = argparse.ArgumentParser()
        parser.add_argument("path", nargs="?")
        self.args = parser.parse_known_args()[0]

        with open(os.path.join(self.program_dir, "version.txt"), "r", encoding="utf-8") as f:
            self.version = f.read().strip()

        self.icon = QIcon(os.path.join(self.program_dir, "Icon.svg"))

        self.settings = Settings()
        self.settings.load(os.path.join(self.data_dir, "settings.json"))

        self.recent_files = read_json_file(os.path.join(self.data_dir, "recentfiles.json"), [])

        self.ffmpeg_handler = FFmpegHandler(self)

    def _get_data_path(self) -> str:
        if platform.system() == "Windows":
            return os.path.join(os.getenv("APPDATA"), "jdAnimatedImageEditor")
        elif platform.system() == "Darwin":
            return os.path.join(str(Path.home()), "Library", "Application Support", "jdAnimatedImageEditor")
        elif platform.system() == "Haiku":
            return os.path.join(str(Path.home()), "config", "settings", "jdAnimatedImageEditor")
        else:
            if os.getenv("XDG_DATA_HOME"):
                return os.path.join(os.getenv("XDG_DATA_HOME"), "jdAnimatedImageEditor")
            else:
                return os.path.join(str(Path.home()), ".local", "share", "jdAnimatedImageEditor")

    def save_recent_files(self):
        try:
            os.makedirs(self.data_dir)
        except Exception:
            pass
        with open(os.path.join(self.data_dir, "recentfiles.json"), "w", encoding="utf-8") as f:
            json.dump(self.recent_files, f, ensure_ascii=False, indent=4)

    def add_to_recent_files(self, path: str) -> None:
        self.recent_files.insert(0, path)
        self.recent_files = remove_list_duplicates(self.recent_files)[:self.settings.get("recentFilesLength")]
        self.save_recent_files()
