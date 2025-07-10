import re
from urllib.parse import urlparse, urlunparse


def is_valid_linkedin_url(url: str) -> bool:
    """
    Validate a LinkedIn post URL (supports /posts/ and /feed/update/ formats).
    """
    pattern = re.compile(
        r"^https://(www\.)?linkedin\.com/(feed/update/urn:li:activity:[\w\d]+|posts/[\w\d\-]+)(/?|\?.*)?$"
    )
    return bool(pattern.match(url))


def clean_linkedin_url(url: str) -> str:
    """
    Remove query parameters from a LinkedIn URL to avoid analytics tracking.
    """
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))
