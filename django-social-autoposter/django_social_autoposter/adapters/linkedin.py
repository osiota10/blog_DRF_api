import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class LinkedInAdapter(BaseSocialAdapter):
    platform_name = "linkedin"

    def publish(self, broadcast) -> dict:
        org_or_person_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not org_or_person_id or not access_token:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': 'Missing LinkedIn Organization/Person ID or Access Token in configuration / .env',
                'raw_response': None
            }

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        # Resolve author URN
        if str(org_or_person_id).startswith("urn:li:"):
            author_urn = str(org_or_person_id)
        elif str(org_or_person_id).isdigit():
            author_urn = f"urn:li:organization:{org_or_person_id}"
        else:
            author_urn = f"urn:li:person:{org_or_person_id}"

        commentary_parts = []
        if broadcast.title:
            commentary_parts.append(broadcast.title)
        if broadcast.message:
            commentary_parts.append(broadcast.message)
        commentary = "\n\n".join(filter(None, commentary_parts))

        share_content = {
            "shareCommentary": {"text": commentary}
        }

        if broadcast.link_url:
            share_content["shareMediaCategory"] = "ARTICLE"
            share_content["media"] = [{
                "status": "READY",
                "originalUrl": broadcast.link_url,
                "title": {"text": broadcast.title or "Read More"}
            }]
            if broadcast.image_url:
                share_content["media"][0]["thumbnails"] = [{"url": broadcast.image_url}]
        else:
            share_content["shareMediaCategory"] = "NONE"

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": share_content
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=20)
            data = res.json() if res.content else {}

            if res.status_code in [200, 201] and 'id' in data:
                ugc_id = data['id']
                return {
                    'success': True,
                    'post_id': str(ugc_id),
                    'post_url': f"https://www.linkedin.com/feed/update/{ugc_id}",
                    'error': None,
                    'raw_response': data
                }

            error_msg = data.get('message') or str(data)
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': f"LinkedIn API Error ({res.status_code}): {error_msg}",
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error executing LinkedIn broadcast")
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
                'error': 'Missing LinkedIn Access Token in configuration / .env',
                'raw_response': None
            }

        url = "https://api.linkedin.com/v2/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        recipient_urn = str(recipient_id)
        if not recipient_urn.startswith("urn:li:"):
            recipient_urn = f"urn:li:person:{recipient_urn}"

        payload = {
            "recipients": [recipient_urn],
            "message": {"body": text}
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=20)
            data = res.json() if res.content else {}

            if res.status_code in [200, 201]:
                msg_id = data.get('id') or data.get('entity', {}).get('id') or str(res.status_code)
                conv_id = data.get('conversation') or data.get('value', {}).get('conversation') or data.get('conversationUrn')
                return {
                    'success': True,
                    'message_id': str(msg_id),
                    'conversation_id': str(conv_id) if conv_id else None,
                    'error': None,
                    'raw_response': data
                }

            error_msg = data.get('message') or str(data)
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': (
                    f"LinkedIn Messaging Error ({res.status_code}): {error_msg}. "
                    "Notice: Direct messaging on LinkedIn requires approved LinkedIn Partner / InMail access."
                ),
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error sending LinkedIn direct message")
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': str(e),
                'raw_response': None
            }

