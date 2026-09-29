class BusinessService:
    """Application service boundary for business queries."""

    def __init__(self, session_factory):
        if session_factory is None:
            raise ValueError("session_factory is required.")
        self.session_factory = session_factory

    def list_businesses(self):
        from core.models import Business

        session = self.session_factory()
        try:
            businesses = session.query(Business).all()
            return [
                {
                    column.name: getattr(business, column.name)
                    for column in Business.__table__.columns
                }
                for business in businesses
            ]
        finally:
            session.close()
