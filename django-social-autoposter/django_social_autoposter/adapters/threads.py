import time
import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class ThreadsAdapter(BaseSocialAdapter):
    platform_name = "threads"

    def _wait_for_container_ready(self, container_id: str, access_token: str, max_attempts: int = 10, sleep_seconds: float = 2.0):
        """Polls Threads Graph API until a video container finishes processing."""
        status_url = f"https://graph.threads.net/v1.0/{container_id}"
        for attempt in range(max_attempts):
            try:
                res = requests.get(
                    status_url,
                    params={'fields': 'status,error_message', 'access_token': access_token},
                    timeout=15
                )
                data = res.json() if getattr(res, 'content', None) and callable(getattr(res, 'json', None)) else {}
                status = str(data.get('status', '')).upper()
                if status in ('FINISHED', 'PUBLISHED', ''):
                    return True, None
                if status in ('ERROR', 'EXPIRED'):
                    return False, data.get('error_message') or f"Threads video container failed with status {status}"
            except Exception as e:
                logger.warning("Threads container status poll error: %s", e)
            if attempt < max_attempts - 1:
                time.sleep(sleep_seconds)
        return False, "Threads video container processing timed out."

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
        extra_data = getattr(broadcast, 'extra_data', None) or {}
        media_list = self.get_media_list(broadcast)
        container_url = f"https://graph.threads.net/v1.0/{user_id}/threads"

        try:
            # Case A: Carousel post (2 to 20 media items: images and/or videos)
            if len(media_list) > 1:
                child_ids = []
                for item_url in media_list[:20]:
                    is_vid = self.is_video_url(item_url)
                    child_payload = {
                        'media_type': 'VIDEO' if is_vid else 'IMAGE',
                        'is_carousel_item': 'true',
                        'access_token': access_token,
                    }
                    if is_vid:
                        child_payload['video_url'] = item_url
                    else:
                        child_payload['image_url'] = item_url

                    child_res = requests.post(container_url, data=child_payload, timeout=25)
                    child_data = child_res.json() if child_res.content else {}
                    if child_res.status_code != 200 or 'id' not in child_data:
                        err = child_data.get('error', {}).get('message') if isinstance(child_data.get('error'), dict) else str(child_data)
                        return {
                            'success': False,
                            'post_id': None,
                            'post_url': None,
                            'error': f"Threads carousel child container creation failed: {err}",
                            'raw_response': child_data
                        }
                    child_id = str(child_data['id'])
                    if is_vid:
                        ready, poll_err = self._wait_for_container_ready(child_id, access_token)
                        if not ready:
                            return {
                                'success': False,
                                'post_id': None,
                                'post_url': None,
                                'error': poll_err,
                                'raw_response': child_data
                            }
                    child_ids.append(child_id)

                # Create parent CAROUSEL container
                parent_res = requests.post(container_url, data={
                    'media_type': 'CAROUSEL',
                    'children': ','.join(child_ids),
                    'text': text,
                    'access_token': access_token,
                }, timeout=25)
                parent_data = parent_res.json() if parent_res.content else {}
                if parent_res.status_code != 200 or 'id' not in parent_data:
                    err = parent_data.get('error', {}).get('message') if isinstance(parent_data.get('error'), dict) else str(parent_data)
                    return {
                        'success': False,
                        'post_id': None,
                        'post_url': None,
                        'error': f"Threads carousel parent container creation failed: {err}",
                        'raw_response': parent_data
                    }
                creation_id = parent_data['id']

            # Case B: Single Video, Single Image, or Text post
            else:
                payload = {
                    'text': text,
                    'access_token': access_token,
                }
                is_vid = False
                if len(media_list) == 1:
                    single_url = media_list[0]
                    is_vid = self.is_video_url(single_url, extra_data)
                    if is_vid:
                        payload['media_type'] = 'VIDEO'
                        payload['video_url'] = single_url
                    else:
                        payload['media_type'] = 'IMAGE'
                        payload['image_url'] = single_url
                else:
                    payload['media_type'] = 'TEXT'

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
                if is_vid:
                    ready, poll_err = self._wait_for_container_ready(str(creation_id), access_token)
                    if not ready:
                        return {
                            'success': False,
                            'post_id': None,
                            'post_url': None,
                            'error': poll_err,
                            'raw_response': data_container
                        }

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
