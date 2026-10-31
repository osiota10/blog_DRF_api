import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.m4v', '.avi', '.mkv')


class TikTokAdapter(BaseSocialAdapter):
    platform_name = "tiktok"

    def publish(self, broadcast) -> dict:
        access_token = self.creds.get('access_token')
        account_id = self.creds.get('page_or_account_id')
        extra_data = self.creds.get('extra_data') or {}

        if not access_token:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': (
                    'Missing TikTok Access Token in configuration / .env. '
                    'Provide TIKTOK_ACCESS_TOKEN.'
                ),
                'raw_response': None
            }

        media_url = broadcast.image_url
        if not media_url:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': (
                    'TikTok Content Posting API requires a media URL (image_url). '
                    'Pure text posts are not supported by TikTok.'
                ),
                'raw_response': None
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }

        # Check if the media URL is a video or photo
        is_video = (
            extra_data.get('media_type') == 'VIDEO' or
            any(media_url.lower().split('?')[0].endswith(ext) for ext in VIDEO_EXTENSIONS)
        )

        privacy_level = extra_data.get('privacy_level', 'PUBLIC_TO_EVERYONE')
        title = (broadcast.title or broadcast.message or 'New Post')[:150]
        description = self.build_text_message(broadcast, max_length=2200)

        if is_video:
            endpoint = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            payload = {
                "post_info": {
                    "title": title,
                    "description": description,
                    "privacy_level": privacy_level,
                    "disable_duet": extra_data.get('disable_duet', False),
                    "disable_comment": extra_data.get('disable_comment', False),
                    "disable_stitch": extra_data.get('disable_stitch', False)
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": media_url
                },
                "post_mode": "DIRECT_POST",
                "media_type": "VIDEO"
            }
        else:
            endpoint = "https://open.tiktokapis.com/v2/post/publish/content/init/"
            payload = {
                "post_info": {
                    "title": title,
                    "description": description,
                    "privacy_level": privacy_level,
                    "disable_duet": extra_data.get('disable_duet', False),
                    "disable_comment": extra_data.get('disable_comment', False),
                    "disable_stitch": extra_data.get('disable_stitch', False),
                    "auto_add_music": extra_data.get('auto_add_music', True)
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "photo_cover_index": 1,
                    "photo_images": [media_url]
                },
                "post_mode": "DIRECT_POST",
                "media_type": "PHOTO"
            }

        try:
            res = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            data = res.json() if res.content else {}

            # TikTok response structure: {"data": {"publish_id": "..."}, "error": {"code": "ok", "message": ""}}
            inner_data = data.get('data') or {}
            publish_id = inner_data.get('publish_id')

            err_info = data.get('error') or {}
            err_code = err_info.get('code') if isinstance(err_info, dict) else None

            if res.status_code in [200, 201] and publish_id and (err_code is None or err_code == 'ok'):
                post_url = f"https://www.tiktok.com/@{account_id}/video/{publish_id}" if account_id else f"https://www.tiktok.com"
                return {
                    'success': True,
                    'post_id': str(publish_id),
                    'post_url': post_url,
                    'error': None,
                    'raw_response': data
                }

            error_msg = err_info.get('message') or err_code or str(data)
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': f"TikTok post failed ({res.status_code}): {error_msg}",
                'raw_response': data
            }

        except Exception as e:
            logger.exception("Error executing TikTok broadcast")
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': str(e),
                'raw_response': None
            }
