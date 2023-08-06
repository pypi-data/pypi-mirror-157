from PyQt6.QtCore import QTranslator, QLocale
from PyQt6.QtWidgets import QApplication
from .MainWindow import MainWindow
from .Environment import Environment
import PIL.Image
import sys
import os


def main():
    app = QApplication(sys.argv)

    env = Environment()

    app.setDesktopFileName("com.gitlab.JakobDev.jdAnimatedImageEditor")
    app.setApplicationName("jdAnimatedImageEditor")
    app.setWindowIcon(env.icon)

    translator = QTranslator()
    language = env.settings.get("language")
    if language == "default":
        system_language = QLocale.system().name()
        translator.load(
            os.path.join(env.program_dir, "translations", "jdAnimatedImageEditor_" + system_language.split("_")[0] + ".qm"))
        translator.load(os.path.join(env.program_dir, "translations", "jdAnimatedImageEditor_" + system_language + ".qm"))
    else:
        translator.load(os.path.join(env.program_dir, "translations", "jdAnimatedImageEditor_" + language + ".qm"))
    app.installTranslator(translator)

    PIL.Image.preinit()

    w = MainWindow(env)
    w.show()

    if env.args.path:
        w.open_file(env.args.path)

    sys.exit(app.exec())
