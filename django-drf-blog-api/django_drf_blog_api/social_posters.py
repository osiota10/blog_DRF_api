import requests
import logging
import os
import time
import mimetypes
from abc import ABC, abstractmethod
from django.conf import settings
from .models import SocialPlatformConfig

logger = logging.getLogger(__name__)


def get_platform_credentials(platform_name: str) -> dict:
    """
    Returns platform credentials by checking Database override first,
    falling back to django-environ / settings.SOCIAL_AUTO_POST.
    """
    key = platform_name.upper()
    env_config = getattr(settings, 'SOCIAL_AUTO_POST', {}).get(key, {})

    # Check Database Config override
    try:
        db_config = SocialPlatformConfig.objects.filter(platform=platform_name.lower()).first()
        if db_config:
            if not db_config.is_enabled:
                return {'enabled': False}

            return {
                'enabled': True,
                'access_token': db_config.access_token or env_config.get('ACCESS_TOKEN', ''),
                'page_or_account_id': db_config.page_or_account_id or env_config.get('PAGE_ID') or env_config.get('ACCOUNT_ID') or env_config.get('USER_ID') or env_config.get('ORGANIZATION_ID', ''),
                'api_key': db_config.api_key or env_config.get('API_KEY', ''),
                'api_secret': db_config.api_secret or env_config.get('API_SECRET', ''),
                'access_token_secret': getattr(db_config, 'access_token_secret', None) or env_config.get('ACCESS_TOKEN_SECRET', ''),
                'bearer_token': env_config.get('BEARER_TOKEN', ''),
            }
    except Exception as e:
        logger.warning(f"Error fetching SocialPlatformConfig from DB: {e}")

    # Fallback to .env / settings.py
    return {
        'enabled': env_config.get('ENABLED', False),
        'access_token': env_config.get('ACCESS_TOKEN', ''),
        'page_or_account_id': env_config.get('PAGE_ID') or env_config.get('ACCOUNT_ID') or env_config.get('USER_ID') or env_config.get('ORGANIZATION_ID', ''),
        'api_key': env_config.get('API_KEY', ''),
        'api_secret': env_config.get('API_SECRET', ''),
        'access_token_secret': env_config.get('ACCESS_TOKEN_SECRET', ''),
        'bearer_token': env_config.get('BEARER_TOKEN', ''),
    }


class BaseSocialPoster(ABC):
    def __init__(self, creds: dict):
        self.creds = creds

    @abstractmethod
    def publish(self, post, article_url: str) -> dict:
        """
        Publishes post to platform.
        Returns: {'success': bool, 'post_id': str, 'post_url': str, 'error': str}
        """
        pass


class FacebookPoster(BaseSocialPoster):
    def publish(self, post, article_url: str) -> dict:
        page_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not page_id or not access_token:
            return {'success': False, 'error': 'Missing Facebook Page ID or Access Token'}

        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        message = f"{post.title}\n\n{post.excerpt or ''}\n\nRead full article: {article_url}"
        payload = {
            'message': message,
            'link': article_url,
            'access_token': access_token
        }
        try:
            res = requests.post(url, data=payload, timeout=15)
            data = res.json()
            if res.status_code == 200 and 'id' in data:
                return {'success': True, 'post_id': data['id'], 'post_url': f"https://facebook.com/{data['id']}"}
            return {'success': False, 'error': str(data.get('error', data))}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class InstagramPoster(BaseSocialPoster):
    def publish(self, post, article_url: str) -> dict:
        ig_account_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')
        image_url = post.featured_image

        if not ig_account_id or not access_token:
            return {'success': False, 'error': 'Missing Instagram Account ID or Access Token'}
        if not image_url:
            return {'success': False, 'error': 'Instagram requires a featured image URL.'}

        try:
            # 1. Create Media Container
            container_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"
            caption = f"{post.title}\n\n{post.excerpt or ''}\n\nLink in bio / {article_url}"
            res1 = requests.post(container_url, data={
                'image_url': image_url,
                'caption': caption,
                'access_token': access_token
            }, timeout=15)
            d1 = res1.json()
            if res1.status_code != 200 or 'id' not in d1:
                return {'success': False, 'error': f"Container creation failed: {d1}"}

            container_id = d1['id']

            # 2. Publish Container
            publish_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media_publish"
            res2 = requests.post(publish_url, data={
                'creation_id': container_id,
                'access_token': access_token
            }, timeout=15)
            d2 = res2.json()
            if res2.status_code == 200 and 'id' in d2:
                return {'success': True, 'post_id': d2['id'], 'post_url': f"https://instagram.com/p/{d2['id']}"}
            return {'success': False, 'error': f"Media publish failed: {d2}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class XPoster(BaseSocialPoster):
    def publish(self, post, article_url: str) -> dict:
        api_key = self.creds.get('api_key')
        api_secret = self.creds.get('api_secret')
        access_token = self.creds.get('access_token')
        access_token_secret = self.creds.get('access_token_secret')
        bearer_token = self.creds.get('bearer_token')

        auth = None
        headers = {"Content-Type": "application/json"}

        # Twitter/X API v2 (POST /2/tweets) strictly requires User Context authentication.
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
                    'error': (
                        f"Missing Twitter OAuth 1.0a credentials: {', '.join(missing_keys)}. "
                        "POST /2/tweets requires User Context. Ensure your Twitter App has 'Read and Write' "
                        "permissions enabled in Developer Portal before generating Access Token & Secret."
                    )
                }

            try:
                from requests_oauthlib import OAuth1
            except ImportError:
                return {
                    'success': False,
                    'error': (
                        "Library 'requests-oauthlib' is required for Twitter OAuth 1.0a User Context. "
                        "Install it with: pip install requests-oauthlib"
                    )
                }

            auth = OAuth1(
                api_key,
                client_secret=api_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )
        elif bearer_token or access_token:
            token = bearer_token or access_token
            headers["Authorization"] = f"Bearer {token}"
        else:
            return {
                'success': False,
                'error': (
                    "Missing X / Twitter credentials. POST /2/tweets requires User Context authentication: "
                    "either OAuth 1.0a (API Key, API Secret, Access Token, and Access Token Secret with "
                    "'Read and Write' permissions) or an OAuth 2.0 User Access Token with 'tweet.write' scope."
                )
            }

        url = "https://api.twitter.com/2/tweets"
        text = f"{post.title}\n\n{article_url}"
        if len(text) > 280:
            suffix = f"...\n{article_url}"
            text = text[:max(0, 280 - len(suffix))].rstrip() + suffix

        try:
            res = requests.post(url, json={"text": text}, headers=headers, auth=auth, timeout=20)
            data = res.json() if res.content else {}

            if res.status_code == 201 and 'data' in data:
                tweet_id = data['data']['id']
                return {'success': True, 'post_id': tweet_id, 'post_url': f"https://x.com/i/web/status/{tweet_id}"}

            error_detail = data.get('detail') or data.get('errors') or str(data)
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

            return {'success': False, 'error': error_msg}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LinkedInPoster(BaseSocialPoster):
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
                    asset_info = check_res.json()
                    recipes = asset_info.get("recipes", [])
                    if any(r.get("status") == "AVAILABLE" for r in recipes):
                        return asset_urn
                    if any(r.get("status") == "CLIENT_ERROR" for r in recipes):
                        logger.warning(f"LinkedIn asset {asset_urn} failed processing: {asset_info}")
                        return None
                time.sleep(1)

            return asset_urn
        except Exception as e:
            logger.exception(f"Error during LinkedIn image upload: {e}")
            return None

    def publish(self, post, article_url: str) -> dict:
        org_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not org_id or not access_token:
            return {'success': False, 'error': 'Missing LinkedIn Organization ID or Access Token'}

        if str(org_id).startswith("urn:li:"):
            author_urn = str(org_id)
        elif str(org_id).isdigit():
            author_urn = f"urn:li:organization:{org_id}"
        else:
            author_urn = f"urn:li:person:{org_id}"

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        commentary_parts = [post.title]
        if post.excerpt:
            commentary_parts.append(post.excerpt)

        # Check for featured image and upload to LinkedIn Assets if available
        image_source = getattr(post, 'featured_image', None) or getattr(post, 'featured_image_url', None)
        asset_urn = None
        if image_source:
            image_bytes = self._fetch_image_bytes(image_source)
            if image_bytes:
                asset_urn = self._upload_image(author_urn, access_token, image_bytes, filename=str(image_source))

        if asset_urn:
            if article_url:
                commentary_parts.append(f"Read full article: {article_url}")
            commentary = "\n\n".join(filter(None, commentary_parts))

            share_content = {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "media": asset_urn,
                    "title": {"text": post.title or "Featured Image"}
                }]
            }
        else:
            commentary = "\n\n".join(filter(None, commentary_parts))
            share_content = {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": article_url,
                    "title": {"text": post.title}
                }]
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
                    'post_url': f"https://www.linkedin.com/feed/update/{ugc_id}"
                }
            return {'success': False, 'error': str(data)}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ThreadsPoster(BaseSocialPoster):
    def publish(self, post, article_url: str) -> dict:
        user_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not user_id or not access_token:
            return {'success': False, 'error': 'Missing Threads User ID or Access Token'}

        text = f"{post.title}\n\n{post.excerpt or ''}\n\n{article_url}"
        if len(text) > 500:
            suffix = f"...\n{article_url}"
            text = text[:max(0, 500 - len(suffix))].rstrip() + suffix

        payload = {
            'text': text,
            'access_token': access_token,
        }
        if getattr(post, 'featured_image', None):
            payload['media_type'] = 'IMAGE'
            payload['image_url'] = post.featured_image
        else:
            payload['media_type'] = 'TEXT'

        try:
            # Step 1: Create Container
            container_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
            res1 = requests.post(container_url, data=payload, timeout=25)
            d1 = res1.json() if res1.content else {}
            if res1.status_code != 200 or 'id' not in d1:
                err = d1.get('error', {}).get('message') if isinstance(d1.get('error'), dict) else str(d1)
                return {'success': False, 'error': f"Threads container failed: {err}"}

            creation_id = d1['id']

            # Step 2: Publish Container
            publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
            res2 = requests.post(publish_url, data={
                'creation_id': creation_id,
                'access_token': access_token,
            }, timeout=25)
            d2 = res2.json() if res2.content else {}
            if res2.status_code == 200 and 'id' in d2:
                post_id = str(d2['id'])
                return {'success': True, 'post_id': post_id, 'post_url': f"https://www.threads.net/post/{post_id}"}

            err = d2.get('error', {}).get('message') if isinstance(d2.get('error'), dict) else str(d2)
            return {'success': False, 'error': f"Threads publish failed: {err}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TikTokPoster(BaseSocialPoster):
    def publish(self, post, article_url: str) -> dict:
        access_token = self.creds.get('access_token')
        account_id = self.creds.get('page_or_account_id')
        media_url = getattr(post, 'featured_image', None)

        if not access_token:
            return {'success': False, 'error': 'Missing TikTok Access Token'}

        if not media_url:
            return {'success': False, 'error': 'TikTok requires a featured image URL to create a post.'}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }

        title = post.title[:150]
        description = f"{post.title}\n\n{post.excerpt or ''}\n\nRead more: {article_url}"[:2200]

        payload = {
            "post_info": {
                "title": title,
                "description": description,
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "auto_add_music": True
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 1,
                "photo_images": [media_url]
            },
            "post_mode": "DIRECT_POST",
            "media_type": "PHOTO"
        }

        try:
            url = "https://open.tiktokapis.com/v2/post/publish/content/init/"
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            data = res.json() if res.content else {}

            inner_data = data.get('data') or {}
            publish_id = inner_data.get('publish_id')
            err_info = data.get('error') or {}
            err_code = err_info.get('code') if isinstance(err_info, dict) else None

            if res.status_code in [200, 201] and publish_id and (err_code is None or err_code == 'ok'):
                post_url = f"https://www.tiktok.com/@{account_id}/video/{publish_id}" if account_id else "https://www.tiktok.com"
                return {'success': True, 'post_id': str(publish_id), 'post_url': post_url}

            error_msg = err_info.get('message') or err_code or str(data)
            return {'success': False, 'error': f"TikTok post failed ({res.status_code}): {error_msg}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
