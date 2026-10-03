from core.request import ScrapeRequest

from .dto import ScrapeRequestDTO, ScrapeResultDTO


class ScrapeService:
    """Application service boundary for scrape operations."""

    def __init__(self, pipeline):
        if pipeline is None:
            raise ValueError("pipeline is required.")
        self.pipeline = pipeline

    def build_request(self, location, keywords, max_results=None, source="google_maps", access_mode="web", api_key=None):
        request_dto = ScrapeRequestDTO.from_values(
            location=location,
            keywords=keywords,
            max_results=max_results,
            source=source,
            access_mode=access_mode,
            api_key=api_key,
        )
        return ScrapeRequest(
            location=request_dto.location,
            keywords=request_dto.keywords,
            max_results=request_dto.max_results,
            source=request_dto.source,
            access_mode=request_dto.access_mode,
            api_key=request_dto.api_key,
        )

    def start_scrape(
        self,
        request=None,
        keywords=None,
        max_results=None,
        location=None,
        source="google_maps",
        access_mode="web",
        api_key=None,
    ):
        if isinstance(request, ScrapeRequestDTO):
            request_dto = request
        else:
            if request is None:
                request = location
            request_dto = ScrapeRequestDTO.from_values(
                location=request,
                keywords=keywords,
                max_results=max_results,
                source=source,
                access_mode=access_mode,
                api_key=api_key,
            )

        core_request = self.build_request(
            location=request_dto.location,
            keywords=request_dto.keywords,
            max_results=request_dto.max_results,
            source=request_dto.source,
            access_mode=request_dto.access_mode,
            api_key=request_dto.api_key,
        )
        result = self.pipeline.run(request=core_request)

        return ScrapeResultDTO(
            status=result.status,
            source=result.source,
            access_mode=result.access_mode,
            location=result.location,
            keywords=result.keywords,
            run_id=result.run_id,
            total_found=result.total_found,
            total_new=result.total_new,
            total_updated=result.total_updated,
            total_duplicates=result.total_duplicates,
            total_errors=result.total_errors,
            error_message=result.error_message,
        )
