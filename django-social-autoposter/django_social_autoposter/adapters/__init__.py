from .base import BaseSocialAdapter
from .facebook import FacebookAdapter
from .instagram import InstagramAdapter
from .twitter import TwitterAdapter
from .linkedin import LinkedInAdapter
from .threads import ThreadsAdapter
from .tiktok import TikTokAdapter

ADAPTERS_MAP = {
    'facebook': FacebookAdapter,
    'instagram': InstagramAdapter,
    'twitter': TwitterAdapter,
    'linkedin': LinkedInAdapter,
    'threads': ThreadsAdapter,
    'tiktok': TikTokAdapter,
}

__all__ = [
    'BaseSocialAdapter',
    'FacebookAdapter',
    'InstagramAdapter',
    'TwitterAdapter',
    'LinkedInAdapter',
    'ThreadsAdapter',
    'TikTokAdapter',
    'ADAPTERS_MAP',
]
