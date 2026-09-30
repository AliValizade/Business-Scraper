from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Root window for the Business-Scraper desktop application."""

    def __init__(self, application=None):
        super().__init__()
        self.application = application

        self.setWindowTitle("Business-Scraper")
        self.resize(1000, 700)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        title = QLabel("Business-Scraper")
        subtitle = QLabel("Desktop application")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setCentralWidget(central_widget)
