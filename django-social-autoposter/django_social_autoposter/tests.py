from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import unittest
from unittest.mock import patch, MagicMock

from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog
from .services import SocialBroadcastService, get_platform_credentials
from .adapters import FacebookAdapter, InstagramAdapter, TwitterAdapter, LinkedInAdapter

User = get_user_model()


class SocialAutoPosterModelAndServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='socialtester@example.com', password='password123'
        )

    def test_platform_credentials_db_and_fallback(self):
        # 1. Fallback when no DB row
        creds = get_platform_credentials('facebook')
        self.assertIsInstance(creds, dict)

        # 2. DB override takes precedence
        config = SocialPlatformConfig.objects.create(
            platform='facebook',
            is_enabled=True,
            page_or_account_id='page_123',
            access_token='token_abc'
        )
        creds_db = get_platform_credentials('facebook')
        self.assertTrue(creds_db['enabled'])
        self.assertEqual(creds_db['page_or_account_id'], 'page_123')
        self.assertEqual(creds_db['access_token'], 'token_abc')

        # 3. Disable platform in DB
        config.is_enabled = False
        config.save()
        creds_disabled = get_platform_credentials('facebook')
        self.assertFalse(creds_disabled['enabled'])

    @patch('django_social_autoposter.adapters.facebook.FacebookAdapter.publish')
    @patch('django_social_autoposter.adapters.twitter.TwitterAdapter.publish')
    def test_broadcast_service_multiple_platforms(self, mock_twitter_publish, mock_fb_publish):
        mock_fb_publish.return_value = {
            'success': True,
            'post_id': 'fb_post_999',
            'post_url': 'https://facebook.com/fb_post_999',
            'error': None,
            'raw_response': {'id': 'fb_post_999'}
        }
        mock_twitter_publish.return_value = {
            'success': True,
            'post_id': 'tweet_888',
            'post_url': 'https://x.com/i/web/status/tweet_888',
            'error': None,
            'raw_response': {'data': {'id': 'tweet_888'}}
        }

        # Enable facebook and twitter
        SocialPlatformConfig.objects.create(
            platform='facebook', is_enabled=True,
            page_or_account_id='fb_page_1', access_token='fb_token_1'
        )
        SocialPlatformConfig.objects.create(
            platform='twitter', is_enabled=True,
            bearer_token='x_token_1'
        )

        broadcast = SocialBroadcastService.broadcast(
            title="Launch Day!",
            message="We are thrilled to announce our new platform launch.",
            link_url="https://example.com/launch",
            image_url="https://example.com/cover.png",
            platforms=['facebook', 'twitter'],
            source_instance=self.user,
            async_dispatch=False
        )

        self.assertEqual(broadcast.title, "Launch Day!")
        self.assertEqual(broadcast.content_object, self.user)
        self.assertEqual(broadcast.logs.count(), 2)

        fb_log = broadcast.logs.get(platform='facebook')
        self.assertEqual(fb_log.status, 'published')
        self.assertEqual(fb_log.external_post_id, 'fb_post_999')

        tw_log = broadcast.logs.get(platform='twitter')
        self.assertEqual(tw_log.status, 'published')
        self.assertEqual(tw_log.external_post_id, 'tweet_888')

    @patch('requests.post')
    def test_twitter_adapter_oauth1_user_context(self, mock_post):
        # 1. Missing keys returns descriptive error
        adapter_missing = TwitterAdapter({
            'api_key': 'key_123',
            'api_secret': 'sec_456'
            # missing access_token and access_token_secret
        })
        fake_broadcast = SocialBroadcast.objects.create(message="Test Tweet")
        res_missing = adapter_missing.publish(fake_broadcast)
        self.assertFalse(res_missing['success'])
        self.assertIn("Missing Twitter OAuth 1.0a credentials", res_missing['error'])

        # 2. Complete 4 keys successfully executes with OAuth1
        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 201
        mock_response.content = b'{"data": {"id": "1850000000000000000"}}'
        mock_response.json.return_value = {"data": {"id": "1850000000000000000"}}
        mock_post.return_value = mock_response

        adapter_valid = TwitterAdapter({
            'api_key': 'my_key',
            'api_secret': 'my_secret',
            'access_token': 'my_token',
            'access_token_secret': 'my_token_secret'
        })
        res_valid = adapter_valid.publish(fake_broadcast)
        self.assertTrue(res_valid['success'])
        self.assertEqual(res_valid['post_id'], "1850000000000000000")
        self.assertIn("x.com/i/web/status/1850000000000000000", res_valid['post_url'])

        # 3. 403 Forbidden with App-Only message gives explicit diagnostics
        mock_403 = unittest.mock.MagicMock()
        mock_403.status_code = 403
        mock_403.content = b'{"detail": "Authenticating with OAuth 2.0 Application-Only is forbidden for this endpoint."}'
        mock_403.json.return_value = {"detail": "Authenticating with OAuth 2.0 Application-Only is forbidden for this endpoint."}
        mock_post.return_value = mock_403

        adapter_bearer = TwitterAdapter({'bearer_token': 'app_only_bearer'})
        res_403 = adapter_bearer.publish(fake_broadcast)
        self.assertFalse(res_403['success'])
        self.assertIn("Bearer Token alone (App-Only) is forbidden", res_403['error'])


class SocialAutoPosterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='apiadmin@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_social_platform_config_api(self):
        # Create config
        res = self.client.post('/social/configs/', {
            'platform': 'linkedin',
            'is_enabled': True,
            'page_or_account_id': '12345678',
            'access_token': 'li_token_sec'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['platform'], 'linkedin')

        # List configs
        res_list = self.client.get('/social/configs/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)

    @patch('django_social_autoposter.services.SocialBroadcastService.broadcast')
    def test_social_broadcast_api_post(self, mock_broadcast):
        fake_broadcast = SocialBroadcast.objects.create(
            title="API Broadcast",
            message="Posting from REST API",
            link_url="https://example.com/blog",
            target_platforms=['facebook', 'twitter']
        )
        mock_broadcast.return_value = fake_broadcast

        res = self.client.post('/social/broadcast/', {
            'title': 'API Broadcast',
            'message': 'Posting from REST API',
            'link_url': 'https://example.com/blog',
            'platforms': ['facebook', 'twitter']
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], 'API Broadcast')

        # List broadcasts
        res_list = self.client.get('/social/broadcast/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)
