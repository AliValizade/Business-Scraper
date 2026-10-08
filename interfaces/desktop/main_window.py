from pathlib import Path

from PySide6.QtCore import QSettings, QThread, QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QProgressBar,
    QHBoxLayout,
    QListWidget,
    QStyle,
    QStackedWidget,
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
        self.sidebar_collapsed = False
        self._sidebar_labels = ["Dashboard", "Scrape", "Runs", "Results", "Settings", "License"]
        self._sidebar_icons = [
            QStyle.SP_ComputerIcon,
            QStyle.SP_FileDialogDetailedView,
            QStyle.SP_BrowserReload,
            QStyle.SP_FileDialogListView,
            QStyle.SP_FileDialogContentsView,
            QStyle.SP_DialogApplyButton,
        ]

        self.setWindowTitle("Business-Scraper")
        saved_size = self.settings.value("window_size")
        if isinstance(saved_size, QSize):
            self.resize(saved_size)
        else:
            self.resize(1200, 760)
        self.setMinimumSize(960, 640)

        self.dark_mode = str(self.settings.value("theme", "light")).lower() == "dark"
        self._apply_theme()

        central = QWidget()
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 18, 10, 18)
        sidebar_layout.setSpacing(10)

        self.sidebar_logo = QLabel()
        self.sidebar_logo.setObjectName("SidebarLogo")
        self.sidebar_logo.setAlignment(Qt.AlignCenter)
        self.sidebar_logo.setFixedHeight(92)
        logo_path = Path(__file__).resolve().parents[2] / "assets" / "Logo-PyVerse.png"
        if logo_path.exists():
            self.sidebar_logo.setPixmap(
                QPixmap(str(logo_path)).scaled(92, 92, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        sidebar_layout.addWidget(self.sidebar_logo)

        self.sidebar_title = QLabel("Business-Scraper")
        self.sidebar_title.setObjectName("AppTitle")
        self.sidebar_title.setAutoFillBackground(False)
        self.sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.sidebar_title)

        self.sidebar_menu = QListWidget()
        self.sidebar_menu.setObjectName("SidebarMenu")
        self.sidebar_menu.setIconSize(QSize(22, 22))
        self.sidebar_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_menu.setUniformItemSizes(True)
        self.sidebar_menu.setMinimumHeight(360)
        self.sidebar_menu.setMaximumHeight(360)
        self._refresh_sidebar_items()
        self.sidebar_menu.currentRowChanged.connect(self._navigate_to_page)
        sidebar_layout.addWidget(self.sidebar_menu)
        sidebar_layout.addStretch()

        self.sidebar_status = QLabel("● Ready")
        self.sidebar_status.setStyleSheet("color: #94a3b8; padding: 4px;")
        sidebar_layout.addWidget(self.sidebar_status)
        outer.addWidget(self.sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 20)
        content_layout.setSpacing(10)

        header = QHBoxLayout()
        self.menu_button = QPushButton("☰")
        self.menu_button.setObjectName("MenuButton")
        self.menu_button.setFixedSize(42, 38)
        self.menu_button.clicked.connect(self._toggle_sidebar)
        header.addWidget(self.menu_button)
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("PageTitle")
        self.page_subtitle = QLabel("Business scraping workspace")
        self.page_subtitle.setObjectName("PageSubtitle")
        title_box.addWidget(self.page_title)
        title_box.addWidget(self.page_subtitle)
        header.addLayout(title_box)
        header.addStretch()
        content_layout.addLayout(header)

        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages, 1)
        outer.addWidget(content, 1)
        self.setCentralWidget(central)

        self._build_dashboard_page()
        self._build_scrape_page()
        self._build_runs_page()
        self._build_results_page()
        self._build_settings_page()
        self._build_license_page()

        self.sidebar_menu.setCurrentRow(0)
        self._on_source_changed()
        if self.application is not None:
            self._refresh_license_status()
            self._load_runs()

    def _apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget { background: #111827; color: #e5e7eb; }
                QWidget#Sidebar { background: #001128; }
                QLabel#SidebarLogo { background: transparent; }
                QLabel#AppTitle { background: transparent; color: white; font-size: 16pt; font-weight: 700; padding: 0; }
                QLabel#PageTitle { font-size: 20pt; font-weight: 700; color: #f8fafc; }
                QLabel#PageSubtitle { color: #94a3b8; }
                QPushButton#MenuButton { background: transparent; color: #e5e7eb; border: none; font-size: 18pt; padding: 4px 10px; }
                QPushButton#MenuButton:hover { background: #1f2937; border-radius: 8px; }
                QListWidget#SidebarMenu { background: transparent; border: none; color: #e2e8f0; outline: none; padding: 4px 0; }
                QListWidget#SidebarMenu::item { padding: 9px 8px; margin: 2px 0; border-radius: 8px; min-height: 24px; }
                QListWidget#SidebarMenu::item:selected { background: #2563eb; color: white; }
                QGroupBox { background: #1f2937; border: 1px solid #374151; border-radius: 10px; margin-top: 10px; padding: 14px; }
                QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #e5e7eb; font-weight: 600; }
                QLineEdit, QComboBox, QSpinBox { background: #111827; color: #f9fafb; border: 1px solid #4b5563; border-radius: 7px; padding: 7px 9px; min-height: 18px; }
                QPushButton { background: #2563eb; color: white; border: none; border-radius: 7px; padding: 8px 14px; font-weight: 600; }
                QPushButton:hover { background: #1d4ed8; }
                QPushButton:disabled { background: #374151; color: #9ca3af; }
                QTableWidget { background: #111827; color: #e5e7eb; border: 1px solid #374151; border-radius: 7px; gridline-color: #374151; selection-background-color: #1d4ed8; selection-color: white; }
                QHeaderView::section { background: #1f2937; color: #e5e7eb; border: none; padding: 7px; font-weight: 600; }
                QProgressBar { background: #374151; color: #f9fafb; border: none; border-radius: 5px; min-height: 18px; max-height: 18px; text-align: center; }
                QProgressBar::chunk { background: #2563eb; border-radius: 5px; }
                QLabel#Status { color: #cbd5e1; padding: 4px 0; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background: #f5f7fb; color: #172033; }
                QWidget#Sidebar { background: #001128; }
                QLabel#SidebarLogo { background: transparent; border: none; }
                QWidget#Sidebar QLabel { background: transparent; }
                QLabel#AppTitle { background: transparent; color: #f8fafc; font-size: 16pt; font-weight: 700; padding: 0 2px; }
                QLabel#PageTitle { font-size: 20pt; font-weight: 700; color: #172033; }
                QLabel#PageSubtitle { color: #64748b; }
                QPushButton#MenuButton { background: transparent; color: #172033; border: none; font-size: 18pt; padding: 4px 10px; }
                QPushButton#MenuButton:hover { background: #e2e8f0; border-radius: 8px; }
                QListWidget#SidebarMenu { background: transparent; border: none; color: #e2e8f0; outline: none; padding: 0; }
                QListWidget#SidebarMenu::item { padding: 12px 10px; margin: 2px 0; border-radius: 8px; }
                QListWidget#SidebarMenu::item:selected { background: #2563eb; color: white; }
                QGroupBox { background: white; border: 1px solid #dfe5ef; border-radius: 10px; margin-top: 10px; padding: 14px; }
                QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #334155; font-weight: 600; }
                QLineEdit, QComboBox, QSpinBox { background: white; color: #172033; border: 1px solid #cfd7e6; border-radius: 7px; padding: 7px 9px; min-height: 18px; }
                QPushButton { background: #2563eb; color: white; border: none; border-radius: 7px; padding: 8px 14px; font-weight: 600; }
                QPushButton:hover { background: #1d4ed8; }
                QPushButton:disabled { background: #cbd5e1; color: #64748b; }
                QTableWidget { background: white; color: #172033; border: 1px solid #dfe5ef; border-radius: 7px; gridline-color: #e8edf5; selection-background-color: #dbeafe; selection-color: #172033; }
                QHeaderView::section { background: #eef2f7; color: #334155; border: none; padding: 7px; font-weight: 600; }
                QProgressBar { background: #e8edf5; color: #172033; border: none; border-radius: 5px; min-height: 18px; max-height: 18px; text-align: center; }
                QProgressBar::chunk { background: #2563eb; border-radius: 5px; }
                QLabel#Status { color: #475569; padding: 4px 0; }
            """)
        if hasattr(self, "theme_button"):
            self.theme_button.setText("Switch to Light" if self.dark_mode else "Switch to Dark")

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("theme", "dark" if self.dark_mode else "light")
        self._apply_theme()

    def _build_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        summary = QHBoxLayout()
        self.dashboard_runs = QLabel("0")
        self.dashboard_results = QLabel("0")
        for title, value in (("Runs", self.dashboard_runs), ("Results", self.dashboard_results)):
            box = QGroupBox(title)
            box_layout = QVBoxLayout(box)
            value.setStyleSheet("font-size: 22pt; font-weight: 700; padding-left: 8px;")
            box_layout.addWidget(value)
            summary.addWidget(box)
        layout.addLayout(summary)
        recent = QGroupBox("Recent Runs")
        recent_layout = QVBoxLayout(recent)
        self.dashboard_table = QTableWidget(0, 6)
        self.dashboard_table.setHorizontalHeaderLabels(["ID", "Source", "Mode", "City", "Status", "Found"])
        self.dashboard_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dashboard_table.setEditTriggers(QTableWidget.NoEditTriggers)
        recent_layout.addWidget(self.dashboard_table)
        layout.addWidget(recent, 1)
        self.pages.addWidget(page)

    def _build_scrape_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("New Scrape")
        form = QFormLayout()
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("City or location")
        self.source_combo = QComboBox()
        self.source_combo.addItem("Google Maps", "google_maps")
        self.source_combo.addItem("Neshan", "neshan")
        self.access_mode_combo = QComboBox()
        self.access_mode_combo.addItem("Web", "web")
        self.access_mode_combo.addItem("API", "api")
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        self.access_mode_combo.currentIndexChanged.connect(self._on_source_changed)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
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
        group.setLayout(form)
        layout.addWidget(group)

        actions = QHBoxLayout()
        self.scrape_button = QPushButton("Start Scrape")
        self.scrape_button.clicked.connect(self._start_scrape)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_scrape)
        actions.addWidget(self.scrape_button)
        actions.addWidget(self.cancel_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(18)
        layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("Status")
        self.result_label = QLabel("")
        layout.addWidget(self.status_label)
        layout.addWidget(self.result_label)
        layout.addStretch()
        self.pages.addWidget(page)

    def _build_runs_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        toolbar = QHBoxLayout()
        self.refresh_runs_button = QPushButton("Refresh Runs")
        self.refresh_runs_button.clicked.connect(self._load_runs)
        toolbar.addWidget(self.refresh_runs_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        self.runs_table = QTableWidget(0, 8)
        self.runs_table.setHorizontalHeaderLabels(
            ["ID", "Source", "Mode", "City", "Keyword", "Status", "Found", "Started"]
        )
        self.runs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.runs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.runs_table.itemSelectionChanged.connect(self._load_selected_run_businesses)
        self.runs_table.cellClicked.connect(self._open_run_results)
        layout.addWidget(self.runs_table)
        self.pages.addWidget(page)

    def _build_results_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        toolbar = QHBoxLayout()
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
        toolbar.addStretch()
        toolbar.addWidget(self.export_format_combo)
        toolbar.addWidget(self.export_button)
        layout.addLayout(toolbar)

        self.businesses_table = QTableWidget(0, 6)
        self.businesses_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "City", "Phone", "Rating"])
        self.businesses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.businesses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.businesses_table)
        self.pages.addWidget(page)

    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Appearance")
        form = QFormLayout()
        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self._toggle_theme)
        form.addRow("Theme:", self.theme_button)
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        self.pages.addWidget(page)

    def _build_license_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.license_group = QGroupBox("License")
        license_layout = QHBoxLayout(self.license_group)
        self.license_status_label = QLabel()
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("License key")
        self.activate_license_button = QPushButton("Activate")
        self.activate_license_button.clicked.connect(self._activate_license)
        license_layout.addWidget(self.license_status_label)
        license_layout.addWidget(self.license_key_input, 1)
        license_layout.addWidget(self.activate_license_button)
        layout.addWidget(self.license_group)
        layout.addStretch()
        self.pages.addWidget(page)

    def _navigate_to_page(self, index):
        if index < 0:
            return
        self.pages.setCurrentIndex(index)
        titles = [
            ("Dashboard", "Business scraping workspace"),
            ("Scrape", "Create a new scraping run"),
            ("Runs", "Run history and exports"),
            ("Results", "Businesses from the selected run"),
            ("Settings", "Application preferences"),
            ("License", "License and activation"),
        ]
        title, subtitle = titles[index]
        self.page_title.setText(title)
        self.page_subtitle.setText(subtitle)
        if index == 0:
            self._refresh_dashboard()

    def _refresh_sidebar_items(self):
        current_row = self.sidebar_menu.currentRow()
        self.sidebar_menu.blockSignals(True)
        self.sidebar_menu.clear()

        # Keep this explicit addItems call as the stable navigation contract.
        self.sidebar_menu.addItems(
            ["Dashboard", "Scrape", "Runs", "Results", "Settings", "License"]
        )

        for index, label in enumerate(self._sidebar_labels):
            item = self.sidebar_menu.item(index)
            item.setIcon(self.style().standardIcon(self._sidebar_icons[index]))
            item.setText("" if self.sidebar_collapsed else label)
            item.setTextAlignment(
                Qt.AlignCenter if self.sidebar_collapsed else Qt.AlignVCenter | Qt.AlignLeft
            )

        if 0 <= current_row < self.sidebar_menu.count():
            self.sidebar_menu.setCurrentRow(current_row)
        self.sidebar_menu.blockSignals(False)

    def _toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.sidebar.setFixedWidth(68 if self.sidebar_collapsed else 220)
        if self.sidebar.layout() is not None:
            self.sidebar.layout().setContentsMargins(
                5 if self.sidebar_collapsed else 10,
                18,
                5 if self.sidebar_collapsed else 10,
                18,
            )
        self.sidebar_logo.setVisible(not self.sidebar_collapsed)
        self.sidebar_title.setVisible(not self.sidebar_collapsed)
        self.sidebar_status.setVisible(not self.sidebar_collapsed)
        self._refresh_sidebar_items()

    def _refresh_dashboard(self):
        if self.application is None:
            return
        try:
            runs = self.application.run_service.list_runs()
            self.dashboard_runs.setText(str(len(runs)))
            self.dashboard_results.setText(str(sum(run.total_found or 0 for run in runs)))
            self.dashboard_table.setRowCount(0)
            for run in runs[:10]:
                row = self.dashboard_table.rowCount()
                self.dashboard_table.insertRow(row)
                values = (run.id, run.source, run.access_mode, run.city, run.status, run.total_found)
                for col, value in enumerate(values):
                    self.dashboard_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as exc:
            self._set_status(f"Could not refresh dashboard: {exc}", error=True)

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
                "Google Maps API key"
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

    def _open_run_results(self, row, _column):
        if self.application is None:
            return
        self.runs_table.selectRow(row)
        self._load_selected_run_businesses()
        self.sidebar_menu.setCurrentRow(3)

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
