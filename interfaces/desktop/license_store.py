from datetime import datetime

from PySide6.QtCore import QSettings

from services.dto import LicenseInfoDTO, LicenseStatus


class QSettingsLicenseStateStore:
    """Persist desktop license state in the current user's QSettings."""

    def __init__(self, settings=None):
        self.settings = (
            settings
            if settings is not None
            else QSettings("Business-Scraper", "Business-Scraper")
        )

    def load(self):
        status = self.settings.value("license/status", "", type=str)
        if str(status).strip().lower() != LicenseStatus.ACTIVE.value:
            return None

        product = self.settings.value(
            "license/product", "Business-Scraper", type=str
        )
        edition = self.settings.value("license/edition", "standard", type=str)
        license_key = self.settings.value("license/key", "", type=str)
        activated_at = self.settings.value(
            "license/activated_at", "", type=str
        )

        if not str(license_key).strip():
            return None

        parsed_activated_at = None
        if activated_at:
            try:
                parsed_activated_at = datetime.fromisoformat(str(activated_at))
            except ValueError:
                parsed_activated_at = None

        return LicenseInfoDTO(
            status=LicenseStatus.ACTIVE,
            product=str(product),
            edition=str(edition),
            license_key=str(license_key),
            activated_at=parsed_activated_at,
        )

    def save(self, license_info):
        self.settings.setValue("license/status", license_info.status.value)
        self.settings.setValue("license/product", license_info.product)
        self.settings.setValue("license/edition", license_info.edition)
        self.settings.setValue(
            "license/key",
            license_info.license_key or "",
        )
        self.settings.setValue(
            "license/activated_at",
            license_info.activated_at.isoformat()
            if license_info.activated_at
            else "",
        )
        self.settings.sync()

    def clear(self):
        self.settings.remove("license/status")
        self.settings.remove("license/product")
        self.settings.remove("license/edition")
        self.settings.remove("license/key")
        self.settings.remove("license/activated_at")
        self.settings.sync()
