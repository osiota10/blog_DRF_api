import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class FacebookAdapter(BaseSocialAdapter):
    platform_name = "facebook"

    def publish(self, broadcast) -> dict:
        page_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not page_id or not access_token:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': 'Missing Facebook Page ID or Access Token in configuration / .env',
                'raw_response': None
            }

        message_parts = []
        if broadcast.title:
            message_parts.append(broadcast.title)
        if broadcast.message:
            message_parts.append(broadcast.message)
        message = "\n\n".join(filter(None, message_parts))

        # If image is provided but no link, post to /photos; otherwise post to /feed
        if broadcast.image_url and not broadcast.link_url:
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            payload = {
                'url': broadcast.image_url,
                'caption': message,
                'access_token': access_token,
            }
        else:
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            payload = {
                'message': message,
                'access_token': access_token,
            }
            if broadcast.link_url:
                payload['link'] = broadcast.link_url

        try:
            res = requests.post(url, data=payload, timeout=20)
            data = res.json()
            if res.status_code == 200 and ('id' in data or 'post_id' in data):
                post_id = data.get('post_id') or data.get('id')
                return {
                    'success': True,
                    'post_id': str(post_id),
                    'post_url': f"https://facebook.com/{post_id}",
                    'error': None,
                    'raw_response': data
                }
            error_msg = data.get('error', {}).get('message') if isinstance(data.get('error'), dict) else str(data)
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': f"Facebook API Error: {error_msg}",
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error executing Facebook broadcast")
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': str(e),
                'raw_response': None
            }
