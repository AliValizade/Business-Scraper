from PySide6.QtCore import QSettings, QThread, QSize
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QProgressBar,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QComboBox,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from interfaces.desktop.scrape_worker import ScrapeWorker
from services.dto import ScrapeRequestDTO


class MainWindow(QMainWindow):
    """Root window for the Business-Scraper desktop application."""

    def __init__(self, application=None):
        super().__init__()
        self.application = application
        self._scrape_thread = None
        self._scrape_worker = None
        self.settings = QSettings("Business-Scraper", "Business-Scraper")

        self.setWindowTitle("Business-Scraper")
        saved_size = self.settings.value("window_size")
        if isinstance(saved_size, QSize):
            self.resize(saved_size)
        else:
            self.resize(1200, 800)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)

        root_layout.addWidget(QLabel("Business-Scraper"))

        scrape_group = QGroupBox("Scrape")
        form = QFormLayout(scrape_group)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("City or location")

        self.source_combo = QComboBox()
        self.source_combo.addItem("Google Maps", "google_maps")
        self.source_combo.addItem("Neshan", "neshan")

        self.access_mode_combo = QComboBox()
        self.access_mode_combo.addItem("Web", "web")
        self.access_mode_combo.addItem("API", "api")
        self.source_combo.currentIndexChanged.connect(
            self._on_source_changed
        )

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setEnabled(False)

        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Keyword 1, Keyword 2")

        self.max_results_input = QSpinBox()
        self.max_results_input.setRange(0, 10000)
        self.max_results_input.setSpecialValueText("No limit")

        form.addRow("Source:", self.source_combo)
        form.addRow("Access mode:", self.access_mode_combo)
        form.addRow("API key:", self.api_key_input)
        form.addRow("Location:", self.location_input)
        form.addRow("Keywords:", self.keywords_input)
        form.addRow("Max results:", self.max_results_input)

        self.license_group = QGroupBox("License")
        license_layout = QHBoxLayout(self.license_group)
        self.license_status_label = QLabel()
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("License key")
        self.activate_license_button = QPushButton("Activate")
        self.activate_license_button.clicked.connect(self._activate_license)
        license_layout.addWidget(self.license_status_label)
        license_layout.addWidget(self.license_key_input)
        license_layout.addWidget(self.activate_license_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        actions = QHBoxLayout()
        self.scrape_button = QPushButton("Start Scrape")
        self.scrape_button.clicked.connect(self._start_scrape)
        actions.addWidget(self.scrape_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_scrape)
        actions.addWidget(self.cancel_button)

        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["csv", "excel", "json"])
        saved_format = self.settings.value("export_format", "csv")
        index = self.export_format_combo.findText(str(saved_format))
        if index >= 0:
            self.export_format_combo.setCurrentIndex(index)
        self.export_format_combo.currentTextChanged.connect(
            lambda value: self.settings.setValue("export_format", value)
        )

        self.export_button = QPushButton("Export Selected Run")
        self.export_button.clicked.connect(self._export_selected_run)

        actions.addWidget(self.export_format_combo)
        actions.addWidget(self.export_button)

        self.refresh_runs_button = QPushButton("Refresh Runs")
        self.refresh_runs_button.clicked.connect(self._load_runs)
        actions.addWidget(self.refresh_runs_button)
        actions.addStretch()

        self.status_label = QLabel("Ready.")
        self.result_label = QLabel("")

        root_layout.addWidget(scrape_group)
        root_layout.addWidget(self.license_group)
        root_layout.addWidget(self.progress_bar)
        root_layout.addLayout(actions)
        root_layout.addWidget(self.status_label)
        root_layout.addWidget(self.result_label)

        runs_group = QGroupBox("Run History")
        runs_layout = QVBoxLayout(runs_group)

        self.runs_table = QTableWidget(0, 8)
        self.runs_table.setHorizontalHeaderLabels(
            ["ID", "Source", "Mode", "City", "Keyword", "Status", "Found", "Started"]
        )
        self.runs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.runs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.runs_table.itemSelectionChanged.connect(self._load_selected_run_businesses)
        runs_layout.addWidget(self.runs_table)

        businesses_group = QGroupBox("Businesses in Selected Run")
        businesses_layout = QVBoxLayout(businesses_group)

        self.businesses_table = QTableWidget(0, 6)
        self.businesses_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Category", "City", "Phone", "Rating"]
        )
        self.businesses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.businesses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        businesses_layout.addWidget(self.businesses_table)

        root_layout.addWidget(runs_group)
        root_layout.addWidget(businesses_group)
        root_layout.addStretch()

        self.setCentralWidget(central_widget)

        self._on_source_changed()
        if self.application is not None:
            self._refresh_license_status()
            self._load_runs()

    def closeEvent(self, event):
        if self._scrape_thread is not None and self._scrape_thread.isRunning():
            self._set_status("A scrape is still running.", error=True)
            event.ignore()
            return

        self.settings.setValue("window_size", self.size())
        super().closeEvent(event)

    def _set_status(self, message, error=False):
        self.status_label.setText(message)
        self.status_label.setProperty("error", error)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _on_source_changed(self):
        is_api = self.access_mode_combo.currentData() == "api"
        self.api_key_input.setEnabled(is_api)

        source = self.source_combo.currentData()
        if source == "google_maps" and is_api:
            self.api_key_input.setPlaceholderText(
                "Google Maps API key — API adapter pending"
            )
        elif source == "neshan" and is_api:
            self.api_key_input.setPlaceholderText("Neshan API key")
        else:
            self.api_key_input.clear()
            self.api_key_input.setPlaceholderText("API key")

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
        source = self.source_combo.currentData()
        access_mode = self.access_mode_combo.currentData()
        api_key = self.api_key_input.text().strip() or None

        if not location:
            self._set_status("Location is required.", error=True)
            return
        if not keywords:
            self._set_status("At least one keyword is required.", error=True)
            return

        try:
            request = ScrapeRequestDTO.from_values(
                location=location,
                keywords=keywords,
                max_results=max_results,
                source=source,
                access_mode=access_mode,
                api_key=api_key,
            )

            self._scrape_thread = QThread(self)
            self._scrape_worker = ScrapeWorker(
                self.application.scrape_service,
                request,
            )
            self._scrape_worker.moveToThread(self._scrape_thread)

            self._scrape_thread.started.connect(self._scrape_worker.run)
            self._scrape_thread.finished.connect(self._cleanup_scrape_thread)

            self._scrape_worker.finished.connect(self._on_scrape_finished)
            self._scrape_worker.finished.connect(self._finish_scrape_thread)
            self._scrape_worker.failed.connect(self._on_scrape_failed)
            self._scrape_worker.failed.connect(self._finish_scrape_thread)
            self._scrape_worker.cancelled.connect(self._on_scrape_cancelled)
            self._scrape_worker.cancelled.connect(self._finish_scrape_thread)

            self.scrape_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.progress_bar.setRange(0, 0)
            self.status_label.setText("Scraping...")
            self._scrape_thread.start()
        except Exception as exc:
            self._set_status(f"Error: {exc}", error=True)

    def _on_scrape_finished(self, result):
        if result.status == "FAILED" and result.error_message:
            self._set_status(
                f"Status: {result.status} | {result.error_message}",
                error=True,
            )
        else:
            self.status_label.setText(
                f"Status: {result.status} | "
                f"{result.source} / {result.access_mode}"
            )

        self.result_label.setText(
            f"Run ID: {result.run_id} | "
            f"Found: {result.total_found} | "
            f"New: {result.total_new} | "
            f"Updated: {result.total_updated} | "
            f"Errors: {result.total_errors}"
        )
        self._load_runs()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if result.status == "COMPLETED" else 0)
        self._restore_scrape_controls()

    def _on_scrape_failed(self, message):
        self._set_status(f"Error: {message}", error=True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._restore_scrape_controls()

    def _restore_scrape_controls(self):
        self.scrape_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _cancel_scrape(self):
        if self._scrape_worker is not None:
            self.status_label.setText("Cancellation requested...")
            self.cancel_button.setEnabled(False)
            self._scrape_worker.cancel()

    def _on_scrape_cancelled(self):
        self.status_label.setText("Scrape cancelled.")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._restore_scrape_controls()

    def _finish_scrape_thread(self, *_):
        if self._scrape_thread is not None:
            self._scrape_thread.quit()

    def _cleanup_scrape_thread(self):
        if self._scrape_worker is not None:
            self._scrape_worker.deleteLater()
        if self._scrape_thread is not None:
            self._scrape_thread.deleteLater()
        self._scrape_worker = None
        self._scrape_thread = None
        self._restore_scrape_controls()

    def _refresh_license_status(self):
        license_info = self.application.license_service.get_license()
        if license_info.status.value == "active":
            self.license_status_label.setText(f"Active — {license_info.edition}")
            self.license_key_input.clear()
            self.activate_license_button.setEnabled(False)
        else:
            self.license_status_label.setText("Unlicensed")
            self.activate_license_button.setEnabled(True)

    def _activate_license(self):
        key = self.license_key_input.text().strip()
        if not key:
            self._set_status("License key is required.", error=True)
            return
        try:
            self.application.license_service.activate(key)
            self._refresh_license_status()
            self._set_status("License activated.")
        except Exception as exc:
            self._set_status(f"License activation failed: {exc}", error=True)

    def _export_selected_run(self):
        if self.application is None:
            self.status_label.setText("Application is not configured.")
            return

        selected = self.runs_table.selectedItems()
        if not selected:
            self.status_label.setText("Select a run to export.")
            return

        run_id = int(self.runs_table.item(selected[0].row(), 0).text())
        format_name = self.export_format_combo.currentText()

        filters = {
            "csv": "CSV Files (*.csv)",
            "excel": "Excel Files (*.xlsx)",
            "json": "JSON Files (*.json)",
        }
        default_extension = {
            "csv": ".csv",
            "excel": ".xlsx",
            "json": ".json",
        }[format_name]

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Run",
            f"run_{run_id}{default_extension}",
            filters[format_name],
        )
        if not output_path:
            return

        try:
            result = self.application.export_run(
                run_id=run_id,
                output_path=output_path,
                format_name=format_name,
            )
            self.status_label.setText(
                f"Exported run {run_id} to {result}"
            )
        except Exception as exc:
            self._set_status(f"Export failed: {exc}", error=True)

    def _load_runs(self):
        if self.application is None:
            return

        try:
            runs = self.application.run_service.list_runs()
            self.runs_table.setRowCount(0)

            for run in runs:
                row = self.runs_table.rowCount()
                self.runs_table.insertRow(row)
                values = (
                    run.id,
                    run.source,
                    run.access_mode,
                    run.city,
                    run.keyword,
                    run.status,
                    run.total_found,
                    run.started_at,
                )
                for column, value in enumerate(values):
                    self.runs_table.setItem(
                        row,
                        column,
                        QTableWidgetItem(str(value)),
                    )
        except Exception as exc:
            self._set_status(f"Could not load runs: {exc}", error=True)

    def _load_selected_run_businesses(self):
        if self.application is None:
            return

        selected = self.runs_table.selectedItems()
        if not selected:
            self.businesses_table.setRowCount(0)
            return

        run_id = int(self.runs_table.item(selected[0].row(), 0).text())

        try:
            businesses = self.application.run_service.get_run_businesses(run_id)
            self.businesses_table.setRowCount(0)

            for business in businesses:
                row = self.businesses_table.rowCount()
                self.businesses_table.insertRow(row)
                values = (
                    business.id,
                    business.name,
                    business.category,
                    business.city,
                    business.phone,
                    business.rating,
                )
                for column, value in enumerate(values):
                    self.businesses_table.setItem(
                        row,
                        column,
                        QTableWidgetItem(str(value)),
                    )
        except Exception as exc:
            self._set_status(f"Could not load run businesses: {exc}", error=True)
