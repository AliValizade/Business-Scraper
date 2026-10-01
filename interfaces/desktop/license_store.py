from PySide6.QtCore import QSettings

from services.dto import LicenseInfoDTO, LicenseStatus


class QSettingsLicenseStateStore:
    """Persist desktop license state in the current user's QSettings."""

    def __init__(self, settings=None):
        self.settings = settings or QSettings(
            "Business-Scraper",
            "Business-Scraper",
        )

    def load(self):
        status = self.settings.value("license/status")
        if status != LicenseStatus.ACTIVE.value:
            return None

        product = self.settings.value("license/product", "Business-Scraper")
        edition = self.settings.value("license/edition", "standard")
        license_key = self.settings.value("license/key")
        activated_at = self.settings.value("license/activated_at")

        if not license_key:
            return None

        from datetime import datetime

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
        self.settings.setValue("license/key", license_info.license_key)
        self.settings.setValue(
            "license/activated_at",
            license_info.activated_at.isoformat()
            if license_info.activated_at
            else "",
        )
        self.settings.sync()

    def clear(self):
        self.settings.remove("license")
        self.settings.sync()
