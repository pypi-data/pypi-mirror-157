from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import webbrowser
import os


class AboutDialog(QDialog):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "AboutDialog.ui"), self)

        self.icon_label.setPixmap(env.icon.pixmap(64, 64))
        self.version_label.setText(self.version_label.text().replace("{{version}}", env.version))

        self.view_source_button.clicked.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdAnimatedImageEditor"))
        self.close_button.clicked.connect(self.close)
