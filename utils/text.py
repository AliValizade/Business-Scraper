import re


PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_DIGITS = "0123456789"


DIGIT_TRANSLATION = str.maketrans(
    PERSIAN_DIGITS + ARABIC_DIGITS,
    ENGLISH_DIGITS + ENGLISH_DIGITS,
)


PERSIAN_TRANSLATION = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
    }
)


def normalize_digits(value):
    if value is None:
        return None

    text = str(value).translate(DIGIT_TRANSLATION)

    text = text.replace("٫", ".")
    text = text.replace("٬", ",")

    return text


def normalize_persian_text(value):
    if value is None:
        return None

    text = str(value)

    text = text.translate(PERSIAN_TRANSLATION)

    text = normalize_digits(text)

    # Normalize different whitespace characters.
    text = re.sub(r"[\u00A0\u2000-\u200B\u202F]", " ", text)

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_name(value):
    return normalize_persian_text(value)


def normalize_address(value):
    return normalize_persian_text(value)


def normalize_category(value):
    return normalize_persian_text(value)


def normalize_city(value):
    return normalize_persian_text(value)


def normalize_keyword(value):
    return normalize_persian_text(value)