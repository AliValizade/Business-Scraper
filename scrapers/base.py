from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.page = None

    @abstractmethod
    def search(self, query, location):
        raise NotImplementedError

    @abstractmethod
    def scrape(self):
        raise NotImplementedError