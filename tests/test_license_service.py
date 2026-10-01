from datetime import datetime

import pytest

from services.license_service import (
    InMemoryLicenseStateStore,
    LicenseInfoDTO,
    LicenseService,
    LicenseStatus,
)


def test_new_license_service_is_unlicensed():
    service = LicenseService()
    license_info = service.get_license()
    assert isinstance(license_info, LicenseInfoDTO)
    assert license_info.status is LicenseStatus.UNLICENSED
    assert license_info.product == "Business-Scraper"
    assert license_info.edition == "standard"
    assert license_info.license_key is None


def test_activate_creates_local_license_state():
    service = LicenseService()
    license_info = service.activate(" BS-TEST-001 ")
    assert license_info.status is LicenseStatus.ACTIVE
    assert license_info.license_key == "BS-TEST-001"
    assert isinstance(license_info.activated_at, datetime)
    assert service.get_license() == license_info
    assert service.is_licensed() is True


def test_deactivate_clears_local_license_state():
    service = LicenseService()
    service.activate("BS-TEST-001")
    license_info = service.deactivate()
    assert license_info.status is LicenseStatus.UNLICENSED
    assert license_info.license_key is None
    assert service.is_licensed() is False


def test_license_state_store_is_injectable():
    store = InMemoryLicenseStateStore()
    first = LicenseService(store=store)
    second = LicenseService(store=store)
    first.activate("BS-SHARED-001")
    assert second.get_license().license_key == "BS-SHARED-001"


def test_license_dto_is_immutable():
    license_info = LicenseService().activate("BS-TEST-001")
    with pytest.raises((AttributeError, TypeError)):
        license_info.status = LicenseStatus.UNLICENSED


def test_activate_rejects_invalid_license_key():
    service = LicenseService()
    with pytest.raises(TypeError):
        service.activate(123)
    with pytest.raises(ValueError):
        service.activate("   ")


def test_license_service_validates_product_and_edition():
    with pytest.raises(ValueError):
        LicenseService(product="   ")
    with pytest.raises(TypeError):
        LicenseService(edition=123)
    with pytest.raises(ValueError):
        LicenseService(edition="   ")
