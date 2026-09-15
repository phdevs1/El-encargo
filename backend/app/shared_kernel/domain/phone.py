import phonenumbers
from phonenumbers import NumberParseException


class InvalidPhoneNumber(ValueError):
    def __init__(self, raw: str):
        self.raw = raw
        super().__init__(f"Could not parse phone number: {raw!r}")


def normalize_phone_e164(raw: str, default_region: str) -> str:
    try:
        parsed = phonenumbers.parse(raw, default_region.upper())
    except NumberParseException as exc:
        raise InvalidPhoneNumber(raw) from exc
    if not phonenumbers.is_valid_number(parsed):
        raise InvalidPhoneNumber(raw)
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
