import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class TwitterAdapter(BaseSocialAdapter):
    platform_name = "twitter"

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
