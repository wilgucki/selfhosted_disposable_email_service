import re


def is_email_address_valid(value: str) -> bool:
    pattern = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    if not re.search(pattern, value):
        return False
    return True
