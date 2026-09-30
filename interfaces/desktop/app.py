from PySide6.QtWidgets import QApplication

from interfaces.desktop.main_window import MainWindow


def create_desktop_app(application=None):
    """Create the Qt application and root desktop window."""
    qt_app = QApplication.instance() or QApplication([])
    window = MainWindow(application=application)
    return qt_app, window


def run_desktop_app(application=None):
    """Start the desktop event loop."""
    qt_app, window = create_desktop_app(application=application)
    window.show()
    return qt_app.exec()
