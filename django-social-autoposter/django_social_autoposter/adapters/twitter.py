import time
import mimetypes
import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class TwitterAdapter(BaseSocialAdapter):
    platform_name = "twitter"

    def _upload_media(self, media_url: str, auth, auth_headers: dict, is_video: bool = False):
        """
        Downloads media from media_url and uploads it to X/Twitter chunked media upload endpoint.
        Returns media_id string or None on failure.
        """
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        req_headers = {k: v for k, v in (auth_headers or {}).items() if k.lower() == 'authorization'}
        try:
            dl_res = requests.get(media_url, timeout=30)
            if dl_res.status_code != 200 or not getattr(dl_res, 'content', None):
                logger.warning("Twitter media download failed (%s): %s", dl_res.status_code, media_url)
                return None
            media_bytes = dl_res.content
            guessed_type, _ = mimetypes.guess_type(str(media_url).split('?', 1)[0])
            media_type = guessed_type or ('video/mp4' if is_video else 'image/jpeg')
            media_category = 'tweet_video' if is_video else 'tweet_image'

            init_res = requests.post(
                upload_url,
                data={
                    'command': 'INIT',
                    'total_bytes': len(media_bytes),
                    'media_type': media_type,
                    'media_category': media_category,
                },
                headers=req_headers,
                auth=auth,
                timeout=20,
            )
            init_data = init_res.json() if getattr(init_res, 'content', None) else {}
            media_id = init_data.get('media_id_string') or (str(init_data['media_id']) if 'media_id' in init_data else None)
            if init_res.status_code not in (200, 201, 202) or not media_id:
                logger.warning("Twitter media INIT failed: %s", init_data)
                return None

            chunk_size = 4 * 1024 * 1024
            for idx, offset in enumerate(range(0, len(media_bytes), chunk_size)):
                chunk = media_bytes[offset:offset + chunk_size]
                app_res = requests.post(
                    upload_url,
                    data={'command': 'APPEND', 'media_id': media_id, 'segment_index': idx},
                    files={'media': chunk},
                    headers=req_headers,
                    auth=auth,
                    timeout=60,
                )
                if app_res.status_code not in (200, 201, 202, 204):
                    logger.warning("Twitter media APPEND failed (%s): %s", app_res.status_code, app_res.text)
                    return None

            fin_res = requests.post(
                upload_url,
                data={'command': 'FINALIZE', 'media_id': media_id},
                headers=req_headers,
                auth=auth,
                timeout=20,
            )
            fin_data = fin_res.json() if getattr(fin_res, 'content', None) else {}
            if fin_res.status_code not in (200, 201):
                logger.warning("Twitter media FINALIZE failed: %s", fin_data)
                return None

            proc_info = fin_data.get('processing_info')
            attempts = 0
            while proc_info and proc_info.get('state') in ('pending', 'in_progress') and attempts < 10:
                wait_secs = min(int(proc_info.get('check_after_secs', 2)), 5)
                time.sleep(wait_secs)
                status_res = requests.get(
                    upload_url,
                    params={'command': 'STATUS', 'media_id': media_id},
                    headers=req_headers,
                    auth=auth,
                    timeout=15,
                )
                status_data = status_res.json() if getattr(status_res, 'content', None) else {}
                proc_info = status_data.get('processing_info')
                attempts += 1

            if proc_info and proc_info.get('state') == 'failed':
                logger.warning("Twitter video processing failed: %s", proc_info)
                return None

            return str(media_id)
        except Exception as e:
            logger.exception("Error uploading media to X / Twitter: %s", e)
            return None

    def publish(self, broadcast) -> dict:
        api_key = self.creds.get('api_key')
        api_secret = self.creds.get('api_secret')
        access_token = self.creds.get('access_token')
        access_token_secret = self.creds.get('access_token_secret')
        bearer_token = self.creds.get('bearer_token')

        auth = None
        headers = {"Content-Type": "application/json"}

        # Twitter/X API v2 (POST /2/tweets) strictly requires User Context authentication.
        # Option 1: OAuth 1.0a User Context (most common for bot/automated posting)
        is_oauth1_attempt = bool(api_key or access_token_secret)

        if is_oauth1_attempt:
            missing_keys = []
            if not api_key:
                missing_keys.append("api_key (TWITTER_API_KEY)")
            if not api_secret:
                missing_keys.append("api_secret (TWITTER_API_SECRET)")
            if not access_token:
                missing_keys.append("access_token (TWITTER_ACCESS_TOKEN)")
            if not access_token_secret:
                missing_keys.append("access_token_secret (TWITTER_ACCESS_TOKEN_SECRET)")

            if missing_keys:
                return {
                    'success': False,
                    'post_id': None,
                    'post_url': None,
                    'error': (
                        f"Missing Twitter OAuth 1.0a credentials: {', '.join(missing_keys)}. "
                        "POST /2/tweets requires User Context. Ensure your Twitter App has 'Read and Write' "
                        "permissions enabled in Developer Portal before generating Access Token & Secret."
                    ),
                    'raw_response': None
                }

            try:
                from requests_oauthlib import OAuth1
            except ImportError:
                return {
                    'success': False,
                    'post_id': None,
                    'post_url': None,
                    'error': (
                        "Library 'requests-oauthlib' is required for Twitter OAuth 1.0a User Context. "
                        "Install it with: pip install requests-oauthlib"
                    ),
                    'raw_response': None
                }

            auth = OAuth1(
                api_key,
                client_secret=api_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )

        # Option 2: OAuth 2.0 User Access Token (with tweet.write scope)
        elif bearer_token or access_token:
            token = bearer_token or access_token
            headers["Authorization"] = f"Bearer {token}"
        else:
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': (
                    "Missing X / Twitter credentials. POST /2/tweets requires User Context authentication: "
                    "either OAuth 1.0a (API Key, API Secret, Access Token, and Access Token Secret with "
                    "'Read and Write' permissions) or an OAuth 2.0 User Access Token with 'tweet.write' scope."
                ),
                'raw_response': None
            }

        url = "https://api.twitter.com/2/tweets"
        text = self.build_text_message(broadcast, max_length=280)
        json_payload = {"text": text}

        extra_data = getattr(broadcast, 'extra_data', None) or {}
        media_list = self.get_media_list(broadcast)
        if media_list:
            media_ids = []
            for item_url in media_list[:4]:
                is_vid = self.is_video_url(item_url, extra_data if len(media_list) == 1 else None)
                mid = self._upload_media(item_url, auth=auth, auth_headers=headers, is_video=is_vid)
                if mid:
                    media_ids.append(mid)
            if media_ids:
                json_payload["media"] = {"media_ids": media_ids}

        try:
            res = requests.post(url, json=json_payload, headers=headers, auth=auth, timeout=20)
            data = res.json() if res.content else {}

            if res.status_code == 201 and 'data' in data:
                tweet_id = data['data']['id']
                return {
                    'success': True,
                    'post_id': str(tweet_id),
                    'post_url': f"https://x.com/i/web/status/{tweet_id}",
                    'error': None,
                    'raw_response': data
                }

            error_detail = data.get('detail') or data.get('errors') or str(data)

            # Detect App-Only Bearer token usage and provide explicit diagnostics
            if "Application-Only" in str(error_detail) or res.status_code == 403:
                error_msg = (
                    f"X / Twitter API Error ({res.status_code}): {error_detail}. "
                    "Notice: Bearer Token alone (App-Only) is forbidden for POST /2/tweets. "
                    "You must use OAuth 1.0a User Context tokens (API Key, API Secret, Access Token, "
                    "and Access Token Secret) with 'Read and write' permissions enabled under User "
                    "authentication settings, or an OAuth 2.0 User Access Token."
                )
            else:
                error_msg = f"X / Twitter API Error ({res.status_code}): {error_detail}"

            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': error_msg,
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error executing X / Twitter broadcast")
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': str(e),
                'raw_response': None
            }

    def send_direct_message(self, recipient_id: str, text: str, media_url: str = None, extra_params: dict = None) -> dict:
        api_key = self.creds.get('api_key')
        api_secret = self.creds.get('api_secret')
        access_token = self.creds.get('access_token')
        access_token_secret = self.creds.get('access_token_secret')
        bearer_token = self.creds.get('bearer_token')

        auth = None
        headers = {"Content-Type": "application/json"}

        is_oauth1_attempt = bool(api_key or access_token_secret)

        if is_oauth1_attempt:
            missing_keys = []
            if not api_key:
                missing_keys.append("api_key")
            if not api_secret:
                missing_keys.append("api_secret")
            if not access_token:
                missing_keys.append("access_token")
            if not access_token_secret:
                missing_keys.append("access_token_secret")

            if missing_keys:
                return {
                    'success': False,
                    'message_id': None,
                    'conversation_id': None,
                    'error': f"Missing Twitter OAuth 1.0a credentials: {', '.join(missing_keys)}.",
                    'raw_response': None
                }

            try:
                from requests_oauthlib import OAuth1
                auth = OAuth1(api_key, client_secret=api_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)
            except ImportError:
                return {
                    'success': False,
                    'message_id': None,
                    'conversation_id': None,
                    'error': "Library 'requests-oauthlib' is required for Twitter OAuth 1.0a.",
                    'raw_response': None
                }
        elif bearer_token or access_token:
            token = bearer_token or access_token
            headers["Authorization"] = f"Bearer {token}"
        else:
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': (
                    "Missing Twitter credentials. Direct messaging requires User Context: "
                    "OAuth 1.0a (with 'Read, write, and Direct message' permissions) or OAuth 2.0 with 'dm.write' scope."
                ),
                'raw_response': None
            }

        url = f"https://api.twitter.com/2/dm_conversations/with/{recipient_id}/messages"
        payload = {"message": {"text": text}}

        try:
            res = requests.post(url, json=payload, headers=headers, auth=auth, timeout=20)
            data = res.json() if res.content else {}

            if res.status_code in [200, 201] and 'data' in data:
                dm_data = data['data']
                return {
                    'success': True,
                    'message_id': str(dm_data.get('dm_event_id')),
                    'conversation_id': str(dm_data.get('dm_conversation_id')),
                    'error': None,
                    'raw_response': data
                }

            error_detail = data.get('detail') or data.get('errors') or str(data)
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': f"Twitter DM Error ({res.status_code}): {error_detail}",
                'raw_response': data
            }
        except Exception as e:
            logger.exception("Error sending Twitter direct message")
            return {
                'success': False,
                'message_id': None,
                'conversation_id': None,
                'error': str(e),
                'raw_response': None
            }

