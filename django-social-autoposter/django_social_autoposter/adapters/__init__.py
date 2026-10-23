from .base import BaseSocialAdapter
from .facebook import FacebookAdapter
from .instagram import InstagramAdapter
from .twitter import TwitterAdapter
from .linkedin import LinkedInAdapter

ADAPTERS_MAP = {
    'facebook': FacebookAdapter,
    'instagram': InstagramAdapter,
    'twitter': TwitterAdapter,
    'linkedin': LinkedInAdapter,
}

__all__ = [
    'BaseSocialAdapter',
    'FacebookAdapter',
    'InstagramAdapter',
    'TwitterAdapter',
    'LinkedInAdapter',
    'ADAPTERS_MAP',
]
