from PySide6.QtCore import QObject, Signal, Slot

from services.dto import ScrapeRequestDTO


class ScrapeWorker(QObject):
    """Background worker for one scrape operation."""

    finished = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, scrape_service, request):
        super().__init__()
        self.scrape_service = scrape_service
        self.request = request
        self._cancel_requested = False

    @Slot()
    def run(self):
        try:
            if self._cancel_requested:
                self.cancelled.emit()
                return

            result = self.scrape_service.start_scrape(self.request)

            if self._cancel_requested:
                self.cancelled.emit()
                return

            self.finished.emit(result)
        except Exception as exc:
            if self._cancel_requested:
                self.cancelled.emit()
                return
            self.failed.emit(str(exc))

    @Slot()
    def cancel(self):
        self._cancel_requested = True
