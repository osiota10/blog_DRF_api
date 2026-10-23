from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

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
