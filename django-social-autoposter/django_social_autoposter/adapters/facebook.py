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

        media_list = getattr(broadcast, 'all_media_urls', None) or ([broadcast.image_url] if broadcast.image_url else [])

        # Case 1: Multi-image carousel / album (2 or more images, without overriding link_url)
        if len(media_list) > 1 and not broadcast.link_url:
            photo_ids = []
            for img_url in media_list:
                photo_upload_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                p_res = requests.post(photo_upload_url, data={
                    'url': img_url,
                    'published': 'false',
                    'temporary': 'true',
                    'access_token': access_token,
                }, timeout=20)
                p_data = p_res.json() if p_res.content else {}
                if p_res.status_code == 200 and 'id' in p_data:
                    photo_ids.append(p_data['id'])
                else:
                    logger.warning("Failed to upload unpublished Facebook photo: %s", p_data)

            import json
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            payload = {
                'message': message,
                'access_token': access_token,
            }
            if photo_ids:
                for i, pid in enumerate(photo_ids):
                    payload[f'attached_media[{i}]'] = json.dumps({'media_fbid': pid})

        # Case 2: Single image post (no link)
        elif len(media_list) == 1 and not broadcast.link_url:
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            payload = {
                'url': media_list[0],
                'caption': message,
                'access_token': access_token,
            }

        # Case 3: Feed post with link or plain text
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

    def send_direct_message(self, recipient_id: str, text: str, media_url: str = None, extra_params: dict = None) -> dict:
        access_token = self.creds.get('access_token')
        if not access_token:
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': 'Missing Facebook Page Access Token in configuration / .env',
                'raw_response': None
            }

        url = "https://graph.facebook.com/v19.0/me/messages"
        params = extra_params or {}

        payload = {
            'recipient': {'id': str(recipient_id)},
            'access_token': access_token,
        }

        # Handle Message Tag or Standard Response
        if params.get('tag'):
            payload['messaging_type'] = 'MESSAGE_TAG'
            payload['tag'] = params['tag']
        else:
            payload['messaging_type'] = params.get('messaging_type', 'RESPONSE')

        if media_url:
            payload['message'] = {
                'attachment': {
                    'type': params.get('attachment_type', 'image'),
                    'payload': {'url': media_url, 'is_reusable': True}
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
                error_msg += " (Note: Outside 24-hour standard messaging window. Use an approved Meta Message Tag such as ACCOUNT_UPDATE, CONFIRMED_EVENT_UPDATE, or POST_PURCHASE_UPDATE in extra_params={'tag': '...'})."

            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': f"Facebook Messenger Error ({res.status_code}): {error_msg}",
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error sending Facebook direct message")
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': str(e),
                'raw_response': None
            }

