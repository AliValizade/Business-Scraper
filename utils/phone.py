import re

from utils.text import normalize_digits


def normalize_phone(value):
    if value is None:
        return None

    phone = normalize_digits(value)

    # Keep only digits and the leading plus sign.
    phone = re.sub(r"[^\d+]", "", phone)

    if not phone:
        return None

    # Convert 0098... to +98...
    if phone.startswith("0098"):
        phone = "+98" + phone[4:]

    # Convert Iranian local mobile numbers:
    # 09123456789 -> +989123456789
    if phone.startswith("09") and len(phone) == 11:
        phone = "+98" + phone[1:]

    # Convert Iranian local landline numbers:
    # 05112345678 -> +985112345678
    if phone.startswith("0") and len(phone) >= 10:
        phone = "+98" + phone[1:]

    return phone