from abc import ABC, abstractmethod

from core.states import ScraperState


class BaseScraper(ABC):
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.page = None
        self.state = ScraperState.INITIALIZING

    def set_state(self, state):
        if not isinstance(state, ScraperState):
            raise ValueError(
                "state must be an instance of ScraperState."
            )

        self.state = state

    @abstractmethod
    def search(self, query, location):
        raise NotImplementedError

    @abstractmethod
    def scrape(self):
        raise NotImplementedError