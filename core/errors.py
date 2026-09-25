class RunNotFoundError(LookupError):
    """Raised when a requested scrape run does not exist."""

    def __init__(self, run_id):
        super().__init__(
            f"Scrape run with id {run_id} was not found."
        )
        self.run_id = run_id
