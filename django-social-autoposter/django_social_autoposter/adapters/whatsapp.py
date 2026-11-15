import re
import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class WhatsAppAdapter(BaseSocialAdapter):
    platform_name = "whatsapp"

    def _get_phone_number_id(self) -> str:
        return (
            self.creds.get('page_or_account_id') or
            (self.creds.get('extra_data') or {}).get('phone_number_id') or
            ''
        )

    def publish(self, broadcast) -> dict:
        """
        Broadcasting fallback: sends message to default channel or admin recipient
        specified in extra_data or page_or_account_id.
        """
        target_recipient = (self.creds.get('extra_data') or {}).get('broadcast_to')
        if not target_recipient:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': (
                    "WhatsApp is primarily a direct messaging platform. "
                    "To broadcast via WhatsApp, configure 'broadcast_to' phone number in extra_data."
                ),
                'raw_response': None
            }

        text = self.build_text_message(broadcast)
        dm_res = self.send_direct_message(
            recipient_id=target_recipient,
            text=text,
            media_url=broadcast.image_url
        )

        return {
            'success': dm_res.get('success', False),
            'post_id': dm_res.get('message_id'),
            'post_url': None,
            'error': dm_res.get('error'),
            'raw_response': dm_res.get('raw_response')
        }

    def send_direct_message(self, recipient_id: str, text: str, media_url: str = None, extra_params: dict = None) -> dict:
        access_token = self.creds.get('access_token')
        phone_number_id = self._get_phone_number_id()

        if not access_token or not phone_number_id:
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': (
                    "Missing WhatsApp credentials. Ensure WHATSAPP_ACCESS_TOKEN and "
                    "WHATSAPP_PHONE_NUMBER_ID are configured in .env or database."
                ),
                'raw_response': None
            }

        # Clean recipient phone number (remove +, spaces, hyphens)
        clean_phone = re.sub(r'\D', '', str(recipient_id))
        if not clean_phone:
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': f"Invalid WhatsApp recipient phone number: '{recipient_id}'",
                'raw_response': None
            }

        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        params = extra_params or {}

        # 1. Template Message (if specified)
        if params.get('template'):
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "template",
                "template": params['template']
            }
        # 2. Media Message (image, document, video, audio)
        elif media_url:
            media_type = params.get('media_type', 'image').lower()
            media_obj = {"link": media_url}
            if text and media_type in ['image', 'video', 'document']:
                media_obj["caption"] = text
            if params.get('filename') and media_type == 'document':
                media_obj["filename"] = params['filename']

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": media_type,
                media_type: media_obj
            }
        # 3. Standard Text Message
        else:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "preview_url": True,
                    "body": text
                }
            }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=25)
            data = res.json() if res.content else {}

            messages = data.get('messages', [])
            if res.status_code in [200, 201] and messages and 'id' in messages[0]:
                msg_id = messages[0]['id']
                return {
                    'success': True,
                    'message_id': str(msg_id),
                    'conversation_id': None,
                    'error': None,
                    'raw_response': data
                }

            error_msg = data.get('error', {}).get('message') if isinstance(data.get('error'), dict) else str(data)
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': f"WhatsApp Cloud API Error ({res.status_code}): {error_msg}",
                'raw_response': data
            }

        except Exception as e:
            logger.exception("Error sending WhatsApp message")
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': str(e),
                'raw_response': None
            }
