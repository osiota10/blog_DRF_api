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
                'page_or_account_id': db_config.page_or_account_id or env_config.get('PAGE_ID') or env_config.get('ACCOUNT_ID') or env_config.get('ORGANIZATION_ID', ''),
                'api_key': db_config.api_key or env_config.get('API_KEY', ''),
                'api_secret': db_config.api_secret or env_config.get('API_SECRET', ''),
                'bearer_token': env_config.get('BEARER_TOKEN', ''),
            }
    except Exception as e:
        logger.warning(f"Error fetching SocialPlatformConfig from DB: {e}")

    # Fallback to .env / settings.py
    return {
        'enabled': env_config.get('ENABLED', False),
        'access_token': env_config.get('ACCESS_TOKEN', ''),
        'page_or_account_id': env_config.get('PAGE_ID') or env_config.get('ACCOUNT_ID') or env_config.get('ORGANIZATION_ID', ''),
        'api_key': env_config.get('API_KEY', ''),
        'api_secret': env_config.get('API_SECRET', ''),
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
        bearer_token = self.creds.get('bearer_token') or self.creds.get('access_token')
        if not bearer_token:
            return {'success': False, 'error': 'Missing X / Twitter Bearer Token or Access Token'}

        url = "https://api.twitter.com/2/tweets"
        text = f"{post.title}\n\n{article_url}"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        try:
            res = requests.post(url, json={"text": text}, headers=headers, timeout=15)
            data = res.json()
            if res.status_code == 201 and 'data' in data:
                tweet_id = data['data']['id']
                return {'success': True, 'post_id': tweet_id, 'post_url': f"https://x.com/i/web/status/{tweet_id}"}
            return {'success': False, 'error': str(data)}
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
