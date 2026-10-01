from datetime import datetime, timezone
from typing import Protocol

from .dto import LicenseInfoDTO, LicenseStatus


class LicenseStateStore(Protocol):
    def load(self) -> LicenseInfoDTO | None: ...
    def save(self, license_info: LicenseInfoDTO) -> None: ...
    def clear(self) -> None: ...


class InMemoryLicenseStateStore:
    """Minimal local-state adapter for the licensing foundation."""

    def __init__(self):
        self._license_info = None

    def load(self):
        return self._license_info

    def save(self, license_info):
        self._license_info = license_info

    def clear(self):
        self._license_info = None


class LicenseService:
    """Application boundary for local desktop licensing operations."""

    def __init__(self, product="Business-Scraper", edition="standard", store=None):
        if not isinstance(product, str):
            raise TypeError("product must be a string.")
        if not product.strip():
            raise ValueError("product cannot be empty.")
        if not isinstance(edition, str):
            raise TypeError("edition must be a string.")
        if not edition.strip():
            raise ValueError("edition cannot be empty.")
        if store is None:
            store = InMemoryLicenseStateStore()
        self.product = product.strip()
        self.edition = edition.strip()
        self.store = store

    def get_license(self):
        license_info = self.store.load()
        if license_info is None:
            return LicenseInfoDTO(
                status=LicenseStatus.UNLICENSED,
                product=self.product,
                edition=self.edition,
            )
        return license_info

    def activate(self, license_key):
        if not isinstance(license_key, str):
            raise TypeError("license_key must be a string.")
        license_key = license_key.strip()
        if not license_key:
            raise ValueError("license_key cannot be empty.")

        license_info = LicenseInfoDTO(
            status=LicenseStatus.ACTIVE,
            product=self.product,
            edition=self.edition,
            license_key=license_key,
            activated_at=datetime.now(timezone.utc),
        )
        self.store.save(license_info)
        return license_info

    def deactivate(self):
        self.store.clear()
        return self.get_license()

    def is_licensed(self):
        return self.get_license().status is LicenseStatus.ACTIVE
