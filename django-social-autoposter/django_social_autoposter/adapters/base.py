import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseSocialAdapter(ABC):
    """
    Abstract Base Class for Social Media Platform Adapters.
    """
    platform_name = "base"

    def __init__(self, creds: dict):
        self.creds = creds or {}

    @abstractmethod
    def publish(self, broadcast) -> dict:
        """
        Publishes the given SocialBroadcast instance to the target platform.
        Must return a dictionary matching:
        {
            'success': bool,
            'post_id': str or None,
            'post_url': str or None,
            'error': str or None,
            'raw_response': dict or None,
        }
        """
        pass

    def build_text_message(self, broadcast, max_length=None) -> str:
        """
        Builds standard text message combining title, body, and link.
        Truncates cleanly if max_length is specified.
        """
        parts = []
        if broadcast.title:
            parts.append(broadcast.title)
        if broadcast.message:
            parts.append(broadcast.message)
        if broadcast.link_url:
            parts.append(f"\n{broadcast.link_url}")

        full_text = "\n\n".join(filter(None, parts))
        if max_length and len(full_text) > max_length:
            suffix = f"...\n{broadcast.link_url}" if broadcast.link_url else "..."
            cutoff = max(0, max_length - len(suffix))
            full_text = full_text[:cutoff].rstrip() + suffix
        return full_text
