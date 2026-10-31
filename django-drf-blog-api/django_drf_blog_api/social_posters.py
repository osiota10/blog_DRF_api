import requests
import logging
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
    def publish(self, post, article_url: str) -> dict:
        org_id = self.creds.get('page_or_account_id')
        access_token = self.creds.get('access_token')

        if not org_id or not access_token:
            return {'success': False, 'error': 'Missing LinkedIn Organization ID or Access Token'}

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        author_urn = f"urn:li:organization:{org_id}" if org_id.isdigit() else f"urn:li:person:{org_id}"
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": f"{post.title}\n\n{post.excerpt or ''}"},
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": article_url,
                        "title": {"text": post.title}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            data = res.json()
            if res.status_code in [200, 201] and 'id' in data:
                return {'success': True, 'post_id': data['id'], 'post_url': ''}
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
