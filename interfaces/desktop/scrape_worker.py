from PySide6.QtCore import QObject, Signal, Slot

from services.dto import ScrapeRequestDTO


class ScrapeWorker(QObject):
    """Background worker for one scrape operation."""

    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, scrape_service, request):
        super().__init__()
        self.scrape_service = scrape_service
        self.request = request

    @Slot()
    def run(self):
        try:
            result = self.scrape_service.start_scrape(self.request)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
