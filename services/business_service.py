from .dto import BusinessDTO


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
            return [self._to_dto(business) for business in businesses]
        finally:
            session.close()

    @staticmethod
    def _to_dto(business):
        return BusinessDTO(
            id=business.id,
            name=business.name,
            category=business.category,
            address=business.address,
            city=business.city,
            phone=business.phone,
            website=business.website,
            instagram=business.instagram,
            rating=business.rating,
            reviews_count=business.reviews_count,
            latitude=business.latitude,
            longitude=business.longitude,
            google_maps_url=business.google_maps_url,
            source=business.source,
            source_id=business.source_id,
            search_keyword=business.search_keyword,
            scraped_at=business.scraped_at,
            source_url=business.source_url,
            created_at=business.created_at,
            updated_at=business.updated_at,
        )
