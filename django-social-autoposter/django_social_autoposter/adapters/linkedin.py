import requests
import logging
import os
import time
import mimetypes
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class LinkedInAdapter(BaseSocialAdapter):
    platform_name = "linkedin"

    def _fetch_image_bytes(self, image_source: str):
        if not image_source:
            return None
        image_source = str(image_source).strip()

        # 1. Full HTTP/HTTPS URL
        if image_source.startswith(('http://', 'https://')):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
                }
                res = requests.get(image_source, headers=headers, timeout=25)
                if res.status_code == 200:
                    return res.content
                logger.warning(f"Failed to fetch image from URL {image_source} ({res.status_code})")
            except Exception as e:
                logger.warning(f"Exception downloading image {image_source}: {e}")
            return None

        # 2. Local filesystem path
        if os.path.exists(image_source):
            try:
                with open(image_source, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Exception reading local image file {image_source}: {e}")
            return None

        # 3. Relative to Django MEDIA_ROOT if available
        try:
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root:
                clean_rel = image_source.lstrip('/')
                media_url = getattr(settings, 'MEDIA_URL', '/media/').strip('/')
                if clean_rel.startswith(media_url):
                    clean_rel = clean_rel[len(media_url):].lstrip('/')
                full_path = os.path.join(media_root, clean_rel)
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as f:
                        return f.read()
        except Exception as e:
            logger.warning(f"Exception reading media file relative to MEDIA_ROOT: {e}")

        return None

    def _upload_image(self, author_urn: str, access_token: str, image_bytes: bytes, filename: str = None) -> str:
        """
        Registers an upload with LinkedIn Assets API, uploads the raw image bytes via PUT,
        verifies that the Digital Media Asset transitions to AVAILABLE, and returns the asset URN.
        """
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ],
                "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
            }
        }

        try:
            reg_res = requests.post(register_url, json=payload, headers=headers, timeout=20)
            if reg_res.status_code not in [200, 201]:
                logger.warning(f"LinkedIn image registerUpload failed ({reg_res.status_code}): {reg_res.text}")
                return None

            data = reg_res.json() if reg_res.content else {}
            val = data.get('value', {})
            asset_urn = val.get('asset')
            upload_mechanism = val.get('uploadMechanism', {})
            media_upload_http = upload_mechanism.get('com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest', {})
            upload_url = media_upload_http.get('uploadUrl')

            if not upload_url or not asset_urn:
                logger.warning(f"LinkedIn registerUpload response missing uploadUrl or asset: {data}")
                return None

            upload_headers = dict(media_upload_http.get('headers') or {})
            if 'Authorization' not in upload_headers:
                upload_headers['Authorization'] = f"Bearer {access_token}"

            # Detect content-type if possible
            content_type = None
            if filename:
                content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                if image_bytes.startswith(b'\x89PNG'):
                    content_type = 'image/png'
                elif image_bytes.startswith(b'\xff\xd8'):
                    content_type = 'image/jpeg'
                elif image_bytes.startswith(b'GIF8'):
                    content_type = 'image/gif'
                elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:16]:
                    content_type = 'image/webp'
                else:
                    content_type = 'application/octet-stream'

            if 'Content-Type' not in upload_headers:
                upload_headers['Content-Type'] = content_type

            upload_res = requests.put(upload_url, data=image_bytes, headers=upload_headers, timeout=40)
            if upload_res.status_code not in [200, 201]:
                logger.warning(f"LinkedIn image binary upload failed ({upload_res.status_code}): {upload_res.text}")
                return None

            # Verify asset status is AVAILABLE
            asset_id = asset_urn.split(":")[-1]
            status_url = f"https://api.linkedin.com/v2/assets/{asset_id}"

            for _ in range(5):
                check_res = requests.get(status_url, headers=headers, timeout=15)
                if check_res.status_code == 200:
                    try:
                        asset_info = check_res.json() if callable(getattr(check_res, 'json', None)) else {}
                    except Exception:
                        asset_info = {}
                    recipes = asset_info.get("recipes", [])
                    if any(r.get("status") == "AVAILABLE" for r in recipes):
                        return asset_urn
                    if any(r.get("status") == "CLIENT_ERROR" for r in recipes):
                        logger.warning(f"LinkedIn asset {asset_urn} failed processing: {asset_info}")
                        return None
                time.sleep(0.5)

            return asset_urn
        except Exception as e:
            logger.exception(f"Error during LinkedIn image upload: {e}")
            return None

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

        # 1. Attempt to upload all images if image_url or media_urls provided
        media_list = getattr(broadcast, 'all_media_urls', None) or ([broadcast.image_url] if broadcast.image_url else [])
        asset_urns = []
        for img_src in media_list:
            image_bytes = self._fetch_image_bytes(img_src)
            if image_bytes:
                urn = self._upload_image(author_urn, access_token, image_bytes, filename=str(img_src))
                if urn:
                    asset_urns.append(urn)
            else:
                logger.warning(f"Could not retrieve image bytes from image URL/path: {img_src}")

        # 2. Build share_content based on uploaded assets or link
        if asset_urns:
            if broadcast.link_url:
                commentary_parts.append(broadcast.link_url)
            commentary = "\n\n".join(filter(None, commentary_parts)) or "New Update"

            media_items = [
                {
                    "status": "READY",
                    "media": urn,
                    "title": {
                        "text": f"{broadcast.title or 'Post Image'} ({idx + 1})" if len(asset_urns) > 1 else (broadcast.title or "Post Image")
                    }
                }
                for idx, urn in enumerate(asset_urns)
            ]

            share_content = {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "IMAGE",
                "media": media_items
            }
        elif broadcast.link_url:
            commentary = "\n\n".join(filter(None, commentary_parts)) or "New Update"
            share_content = {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": broadcast.link_url,
                    "title": {"text": broadcast.title or "Read More"}
                }]
            }
        else:
            commentary = "\n\n".join(filter(None, commentary_parts)) or "New Update"
            share_content = {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "NONE"
            }

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

