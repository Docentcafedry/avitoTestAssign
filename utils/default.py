import string
import re
from secrets import choice

ALPHABET = string.ascii_letters + string.digits
pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"


def generate_random_slug() -> string:
    slug = ""
    for i in range(6):
        slug += choice(ALPHABET)
    return slug


def validate_url(url: str) -> bool:
    match = re.match(pattern=pattern, string=url)
    return True if match else False
