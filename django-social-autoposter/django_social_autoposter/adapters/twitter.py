import requests
import logging
from .base import BaseSocialAdapter

logger = logging.getLogger(__name__)


class TwitterAdapter(BaseSocialAdapter):
    platform_name = "twitter"

    def publish(self, broadcast) -> dict:
        bearer_token = self.creds.get('bearer_token') or self.creds.get('access_token')
        api_key = self.creds.get('api_key')
        api_secret = self.creds.get('api_secret')
        access_token_secret = self.creds.get('access_token_secret')

        if not bearer_token and not (api_key and self.creds.get('access_token')):
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': 'Missing X / Twitter credentials (Bearer Token or OAuth Keys)',
                'raw_response': None
            }

        url = "https://api.twitter.com/2/tweets"
        text = self.build_text_message(broadcast, max_length=280)
        json_payload = {"text": text}

        headers = {"Content-Type": "application/json"}
        auth = None

        if api_key and api_secret and self.creds.get('access_token') and access_token_secret:
            try:
                from requests_oauthlib import OAuth1
                auth = OAuth1(
                    api_key,
                    client_secret=api_secret,
                    resource_owner_key=self.creds.get('access_token'),
                    resource_owner_secret=access_token_secret
                )
            except ImportError:
                headers["Authorization"] = f"Bearer {bearer_token}"
        else:
            headers["Authorization"] = f"Bearer {bearer_token}"

        try:
            res = requests.post(url, json=json_payload, headers=headers, auth=auth, timeout=20)
            data = res.json()

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
            return {
                'success': False,
                'post_id': None,
                'post_url': None,
                'error': f"X / Twitter API Error ({res.status_code}): {error_detail}",
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
