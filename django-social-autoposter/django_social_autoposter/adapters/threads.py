import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class ThreadsAdapter(BaseSocialAdapter):
    platform_name = "threads"

    def publish(self, broadcast) -> dict:
        user_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not user_id or not access_token:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': (
                    'Missing Threads User ID or Access Token in configuration / .env. '
                    'Provide THREADS_USER_ID and THREADS_ACCESS_TOKEN.'
                ),
                'raw_response': None
            }

        # Threads posts support up to 500 characters
        text = self.build_text_message(broadcast, max_length=500)

        # Prepare payload for container creation
        payload = {
            'text': text,
            'access_token': access_token,
        }

        if broadcast.image_url:
            payload['media_type'] = 'IMAGE'
            payload['image_url'] = broadcast.image_url
        else:
            payload['media_type'] = 'TEXT'

        try:
            # Step 1: Create Threads Media Container
            container_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
            res_container = requests.post(container_url, data=payload, timeout=25)
            data_container = res_container.json() if res_container.content else {}

            if res_container.status_code != 200 or 'id' not in data_container:
                err = data_container.get('error', {}).get('message') if isinstance(data_container.get('error'), dict) else str(data_container)
                return {
                    'success': False,
                    'post_id': None,
                    'post_url': None,
                    'error': f"Threads media container creation failed: {err}",
                    'raw_response': data_container
                }

            creation_id = data_container['id']

            # Step 2: Publish Threads Container
            publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
            res_publish = requests.post(publish_url, data={
                'creation_id': creation_id,
                'access_token': access_token,
            }, timeout=25)
            data_publish = res_publish.json() if res_publish.content else {}

            if res_publish.status_code == 200 and 'id' in data_publish:
                post_id = str(data_publish['id'])
                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': f"https://www.threads.net/post/{post_id}",
                    'error': None,
                    'raw_response': data_publish
                }

            err = data_publish.get('error', {}).get('message') if isinstance(data_publish.get('error'), dict) else str(data_publish)
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': f"Threads container publish failed: {err}",
                'raw_response': data_publish
            }

        except Exception as e:
            logger.exception("Error executing Threads broadcast")
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': str(e),
                'raw_response': None
            }
