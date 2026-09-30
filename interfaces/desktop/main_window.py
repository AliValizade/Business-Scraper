from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import QThread

from interfaces.desktop.scrape_worker import ScrapeWorker
from services.dto import ScrapeRequestDTO


class MainWindow(QMainWindow):
    """Root window for the Business-Scraper desktop application."""

    def __init__(self, application=None):
        super().__init__()
        self.application = application
        self._scrape_thread = None
        self._scrape_worker = None

        self.setWindowTitle("Business-Scraper")
        self.resize(1000, 700)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)

        title = QLabel("Business-Scraper")
        root_layout.addWidget(title)

        scrape_group = QGroupBox("Scrape")
        form = QFormLayout(scrape_group)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("City or location")

        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Keyword 1, Keyword 2")

        self.max_results_input = QSpinBox()
        self.max_results_input.setRange(0, 10000)
        self.max_results_input.setSpecialValueText("No limit")

        form.addRow("Location:", self.location_input)
        form.addRow("Keywords:", self.keywords_input)
        form.addRow("Max results:", self.max_results_input)

        actions = QHBoxLayout()
        self.scrape_button = QPushButton("Start Scrape")
        self.scrape_button.clicked.connect(self._start_scrape)
        actions.addWidget(self.scrape_button)
        actions.addStretch()

        self.status_label = QLabel("Ready.")
        self.result_label = QLabel("")

        root_layout.addWidget(scrape_group)
        root_layout.addLayout(actions)
        root_layout.addWidget(self.status_label)
        root_layout.addWidget(self.result_label)
        root_layout.addStretch()

        self.setCentralWidget(central_widget)

    def _start_scrape(self):
        if self.application is None:
            self.status_label.setText("Application is not configured.")
            return

        location = self.location_input.text().strip()
        keywords = tuple(
            keyword.strip()
            for keyword in self.keywords_input.text().split(",")
            if keyword.strip()
        )
        max_results = self.max_results_input.value() or None

        try:
            request = ScrapeRequestDTO.from_values(
                location=location,
                keywords=keywords,
                max_results=max_results,
            )
            self._scrape_thread = QThread(self)
            self._scrape_worker = ScrapeWorker(
                self.application.scrape_service,
                request,
            )
            self._scrape_worker.moveToThread(self._scrape_thread)
            self._scrape_thread.started.connect(self._scrape_worker.run)
            self._scrape_worker.finished.connect(self._on_scrape_finished)
            self._scrape_worker.failed.connect(self._on_scrape_failed)
            self._scrape_worker.finished.connect(self._finish_scrape_thread)
            self._scrape_worker.failed.connect(self._finish_scrape_thread)
            self.scrape_button.setEnabled(False)
            self.status_label.setText("Scraping...")

            self._scrape_thread.start()

    def _on_scrape_finished(self, result):
            self.status_label.setText(f"Status: {result.status}")
            self.result_label.setText(
                f"Run ID: {result.run_id} | "
                f"Found: {result.total_found} | "
                f"New: {result.total_new} | "
                f"Updated: {result.total_updated} | "
                f"Errors: {result.total_errors}"
            )
        except Exception as exc:
            self.status_label.setText(f"Error: {exc}")

    def _on_scrape_failed(self, message):
        self.status_label.setText(f"Error: {message}")

    def _finish_scrape_thread(self, *_):
        if self._scrape_thread is not None:
            self._scrape_thread.quit()
            self._scrape_thread.finished.connect(self._cleanup_scrape_thread)

    def _cleanup_scrape_thread(self):
        if self._scrape_worker is not None:
            self._scrape_worker.deleteLater()
        if self._scrape_thread is not None:
            self._scrape_thread.deleteLater()
        self._scrape_worker = None
        self._scrape_thread = None
        self.scrape_button.setEnabled(True)
