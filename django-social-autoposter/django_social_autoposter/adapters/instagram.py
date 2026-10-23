import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class InstagramAdapter(BaseSocialAdapter):
    platform_name = "instagram"

    def publish(self, broadcast) -> dict:
        ig_account_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not ig_account_id or not access_token:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': 'Missing Instagram Account ID or Access Token in configuration / .env',
                'raw_response': None
            }

        if not broadcast.image_url:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': 'Instagram Business API requires an image attachment (image_url).',
                'raw_response': None
            }

        caption_parts = []
        if broadcast.title:
            caption_parts.append(broadcast.title)
        if broadcast.message:
            caption_parts.append(broadcast.message)
        if broadcast.link_url:
            caption_parts.append(f"\nLink: {broadcast.link_url}")
        caption = "\n\n".join(filter(None, caption_parts))

        try:
            # Step 1: Create Instagram Media Container
            container_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"
            res_container = requests.post(container_url, data={
                'image_url': broadcast.image_url,
                'caption': caption,
                'access_token': access_token
            }, timeout=25)
            data_container = res_container.json()

            if res_container.status_code != 200 or 'id' not in data_container:
                err = data_container.get('error', {}).get('message') if isinstance(data_container.get('error'), dict) else str(data_container)
                return {
                    'success': False,
                    'post_id': None,
                    'post_url': None,
                    'error': f"Instagram container creation failed: {err}",
                    'raw_response': data_container
                }

            creation_id = data_container['id']

            # Step 2: Publish Media Container
            publish_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media_publish"
            res_publish = requests.post(publish_url, data={
                'creation_id': creation_id,
                'access_token': access_token
            }, timeout=25)
            data_publish = res_publish.json()

            if res_publish.status_code == 200 and 'id' in data_publish:
                post_id = data_publish['id']
                return {
                    'success': True,
                    'post_id': str(post_id),
                    'post_url': f"https://instagram.com/p/{post_id}",
                    'error': None,
                    'raw_response': data_publish
                }

            err = data_publish.get('error', {}).get('message') if isinstance(data_publish.get('error'), dict) else str(data_publish)
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': f"Instagram media publish failed: {err}",
                'raw_response': data_publish
            }
        except Exception as e:
            logger.exception("Error executing Instagram broadcast")
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': str(e),
                'raw_response': None
            }
