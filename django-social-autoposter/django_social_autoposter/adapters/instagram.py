import time
import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class InstagramAdapter(BaseSocialAdapter):
    platform_name = "instagram"

    def _wait_for_container_ready(self, container_id: str, access_token: str, max_attempts: int = 10, sleep_seconds: float = 2.0):
        """Polls Meta Graph API until a video container finishes processing."""
        status_url = f"https://graph.facebook.com/v19.0/{container_id}"
        for attempt in range(max_attempts):
            try:
                res = requests.get(
                    status_url,
                    params={'fields': 'status_code,status', 'access_token': access_token},
                    timeout=15
                )
                data = res.json() if getattr(res, 'content', None) and callable(getattr(res, 'json', None)) else {}
                status_code = str(data.get('status_code', '')).upper()
                if status_code in ('FINISHED', 'PUBLISHED', ''):
                    return True, None
                if status_code in ('ERROR', 'EXPIRED'):
                    return False, data.get('status') or f"Instagram video container failed with status {status_code}"
            except Exception as e:
                logger.warning("Instagram container status poll error: %s", e)
            if attempt < max_attempts - 1:
                time.sleep(sleep_seconds)
        return False, "Instagram video container processing timed out."

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

        extra_data = getattr(broadcast, 'extra_data', None) or {}
        media_list = self.get_media_list(broadcast)
        if not media_list:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': 'Instagram Business API requires a media attachment (image_url or media_urls).',
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
            container_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"

            # Case A: Carousel / Multi-Media Post (2 to 10 images/videos)
            if len(media_list) > 1:
                child_ids = []
                for item_url in media_list[:10]:
                    is_vid = self.is_video_url(item_url)
                    child_payload = {
                        'is_carousel_item': 'true',
                        'access_token': access_token
                    }
                    if is_vid:
                        child_payload['media_type'] = 'VIDEO'
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
                            'error': f"Instagram carousel child container creation failed: {err}",
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
                    'caption': caption,
                    'access_token': access_token
                }, timeout=25)
                parent_data = parent_res.json() if parent_res.content else {}
                if parent_res.status_code != 200 or 'id' not in parent_data:
                    err = parent_data.get('error', {}).get('message') if isinstance(parent_data.get('error'), dict) else str(parent_data)
                    return {
                        'success': False,
                        'post_id': None,
                        'post_url': None,
                        'error': f"Instagram carousel parent container creation failed: {err}",
                        'raw_response': parent_data
                    }
                creation_id = parent_data['id']

            # Case B: Single Video (Reels) or Single Image Post
            else:
                single_url = media_list[0]
                is_vid = self.is_video_url(single_url, extra_data)
                container_payload = {
                    'caption': caption,
                    'access_token': access_token
                }
                if is_vid:
                    container_payload['media_type'] = 'REELS'
                    container_payload['video_url'] = single_url
                    container_payload['share_to_feed'] = 'true'
                else:
                    container_payload['image_url'] = single_url

                res_container = requests.post(container_url, data=container_payload, timeout=25)
                data_container = res_container.json() if res_container.content else {}

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

    def send_direct_message(self, recipient_id: str, text: str, media_url: str = None, extra_params: dict = None) -> dict:
        access_token = self.creds.get('access_token')
        if not access_token:
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': 'Missing Instagram Access Token in configuration / .env',
                'raw_response': None
            }

        url = "https://graph.facebook.com/v19.0/me/messages"
        params = extra_params or {}

        payload = {
            'recipient': {'id': str(recipient_id)},
            'access_token': access_token,
        }

        if media_url:
            payload['message'] = {
                'attachment': {
                    'type': params.get('attachment_type', 'image'),
                    'payload': {'url': media_url}
                }
            }
        else:
            payload['message'] = {'text': text}

        try:
            res = requests.post(url, json=payload, timeout=20)
            data = res.json() if res.content else {}

            if res.status_code == 200 and 'message_id' in data:
                return {
                    'success': True,
                    'message_id': str(data['message_id']),
                    'conversation_id': None,
                    'error': None,
                    'raw_response': data
                }

            err_dict = data.get('error', {}) if isinstance(data.get('error'), dict) else {}
            error_msg = err_dict.get('message') or str(data)
            error_subcode = err_dict.get('error_subcode')
            if error_subcode in [2018001, 2018028] or 'window' in error_msg.lower():
                error_msg += " (Note: Outside 24-hour standard messaging window. Instagram users must initiate conversation or use human agent / approved messaging tags)."

            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': f"Instagram Direct Error ({res.status_code}): {error_msg}",
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error sending Instagram direct message")
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': str(e),
                'raw_response': None
            }

