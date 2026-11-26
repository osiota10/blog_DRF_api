import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseSocialAdapter(ABC):
    """
    Abstract Base Class for Social Media Platform Adapters.
    """
    platform_name = "base"
    VIDEO_EXTENSIONS = ('.mp4', '.mov', '.m4v', '.webm', '.avi', '.mkv', '.mpeg')

    def __init__(self, creds: dict):
        self.creds = creds or {}

    def get_media_list(self, broadcast) -> list:
        """Returns the ordered list of media URLs attached to a broadcast."""
        return getattr(broadcast, 'all_media_urls', None) or (
            [broadcast.image_url] if getattr(broadcast, 'image_url', None) else []
        )

    def is_video_url(self, url: str, extra_data: dict = None) -> bool:
        """Returns True if the URL points to a video or extra_data forces VIDEO/REELS."""
        if extra_data and str(extra_data.get('media_type', '')).upper() in ('VIDEO', 'REELS'):
            return True
        if not url:
            return False
        clean_path = str(url).lower().split('?', 1)[0].split('#', 1)[0]
        return any(clean_path.endswith(ext) for ext in self.VIDEO_EXTENSIONS)

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

    def send_direct_message(self, recipient_id: str, text: str, media_url: str = None, extra_params: dict = None) -> dict:
        """
        Sends a private / direct message to a user on the target platform.
        Returns a dictionary matching:
        {
            'success': bool,
            'message_id': str or None,
            'conversation_id': str or None,
            'error': str or None,
            'raw_response': dict or None,
        }
        """
        return {
            'success': False,
            'message_id': None,
            'conversation_id': None,
            'error': f"Direct messaging is not supported for platform: {self.platform_name}",
            'raw_response': None
        }

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
