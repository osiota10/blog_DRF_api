from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import call_command
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
import unittest
from unittest.mock import patch, MagicMock

from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog, SocialDirectMessage
from .services import (
    SocialBroadcastService,
    SocialMessagingService,
    SocialSchedulerService,
    get_platform_credentials,
)
from .adapters import (
    FacebookAdapter, InstagramAdapter, TwitterAdapter, LinkedInAdapter,
    ThreadsAdapter, TikTokAdapter, WhatsAppAdapter
)

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

    @patch('requests.post')
    def test_threads_adapter_publish(self, mock_post):
        fake_broadcast = SocialBroadcast.objects.create(
            title="Threads News",
            message="Exploring Meta Threads API",
            link_url="https://example.com/threads",
            image_url="https://example.com/image.jpg"
        )

        # 1. Missing credentials
        adapter_missing = ThreadsAdapter({})
        res_missing = adapter_missing.publish(fake_broadcast)
        self.assertFalse(res_missing['success'])
        self.assertIn("Missing Threads User ID", res_missing['error'])

        # 2. Successful 2-step publish
        mock_container_res = MagicMock()
        mock_container_res.status_code = 200
        mock_container_res.content = b'{"id": "c_threads_123"}'
        mock_container_res.json.return_value = {"id": "c_threads_123"}

        mock_publish_res = MagicMock()
        mock_publish_res.status_code = 200
        mock_publish_res.content = b'{"id": "p_threads_999"}'
        mock_publish_res.json.return_value = {"id": "p_threads_999"}

        mock_post.side_effect = [mock_container_res, mock_publish_res]

        adapter_valid = ThreadsAdapter({
            'page_or_account_id': 'threads_user_1',
            'access_token': 'threads_tok_abc'
        })
        res_valid = adapter_valid.publish(fake_broadcast)
        self.assertTrue(res_valid['success'])
        self.assertEqual(res_valid['post_id'], 'p_threads_999')
        self.assertIn('threads.net/post/p_threads_999', res_valid['post_url'])

    @patch('requests.post')
    def test_tiktok_adapter_publish(self, mock_post):
        # 1. Missing access token
        adapter_missing = TikTokAdapter({})
        broadcast_no_image = SocialBroadcast.objects.create(message="TikTok Text Only")
        res_missing = adapter_missing.publish(broadcast_no_image)
        self.assertFalse(res_missing['success'])
        self.assertIn("Missing TikTok Access Token", res_missing['error'])

        # 2. Missing image URL
        adapter_valid = TikTokAdapter({'access_token': 'tiktok_token_xyz'})
        res_no_media = adapter_valid.publish(broadcast_no_image)
        self.assertFalse(res_no_media['success'])
        self.assertIn("TikTok Content Posting API requires a media URL", res_no_media['error'])

        # 3. Successful photo direct post
        broadcast_with_media = SocialBroadcast.objects.create(
            title="TikTok Photo Post",
            message="Check out our visual announcement",
            image_url="https://example.com/banner.jpg"
        )
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.content = b'{"data": {"publish_id": "v_pub_tiktok_456"}, "error": {"code": "ok"}}'
        mock_res.json.return_value = {
            "data": {"publish_id": "v_pub_tiktok_456"},
            "error": {"code": "ok"}
        }
        mock_post.return_value = mock_res

        res_ok = adapter_valid.publish(broadcast_with_media)
        self.assertTrue(res_ok['success'])
        self.assertEqual(res_ok['post_id'], 'v_pub_tiktok_456')

    @patch('requests.put')
    @patch('requests.get')
    @patch('requests.post')
    def test_linkedin_adapter_publish_image_and_article(self, mock_post, mock_get, mock_put):
        adapter = LinkedInAdapter({
            'page_or_account_id': '12345678',
            'access_token': 'li_test_token'
        })

        # 1. Post with image_url -> registers upload, PUTs binary, posts as IMAGE
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.content = b'fake_image_bytes'
        mock_get.return_value = mock_get_res

        mock_reg_res = MagicMock()
        mock_reg_res.status_code = 200
        mock_reg_res.content = b'{"value": {"asset": "urn:li:digitalmediaAsset:123", "uploadMechanism": {"com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {"uploadUrl": "https://upload.linkedin.com/123"}}}}'
        mock_reg_res.json.return_value = {
            "value": {
                "asset": "urn:li:digitalmediaAsset:123",
                "uploadMechanism": {
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                        "uploadUrl": "https://upload.linkedin.com/123"
                    }
                }
            }
        }

        mock_ugc_res = MagicMock()
        mock_ugc_res.status_code = 201
        mock_ugc_res.content = b'{"id": "urn:li:share:98765"}'
        mock_ugc_res.json.return_value = {"id": "urn:li:share:98765"}

        mock_post.side_effect = [mock_reg_res, mock_ugc_res]

        mock_put_res = MagicMock()
        mock_put_res.status_code = 201
        mock_put.return_value = mock_put_res

        broadcast_image = SocialBroadcast.objects.create(
            title="Image Post on LinkedIn",
            message="Check out our visual announcement",
            image_url="https://example.com/banner.jpg",
            link_url="https://example.com/blog/article"
        )

        res = adapter.publish(broadcast_image)
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'urn:li:share:98765')
        self.assertIn("https://www.linkedin.com/feed/update/urn:li:share:98765", res['post_url'])

        # Check UGC post payload
        ugc_call = mock_post.call_args_list[1]
        payload = ugc_call[1]['json']
        share_content = payload['specificContent']['com.linkedin.ugc.ShareContent']
        self.assertEqual(share_content['shareMediaCategory'], 'IMAGE')
        self.assertEqual(share_content['media'][0]['media'], 'urn:li:digitalmediaAsset:123')
        self.assertIn("https://example.com/blog/article", share_content['shareCommentary']['text'])

        # 2. Post with article link only (no image)
        mock_post.side_effect = None
        mock_post.return_value = mock_ugc_res
        broadcast_link = SocialBroadcast.objects.create(
            title="Article Post",
            message="Article without image",
            link_url="https://example.com/blog/article2"
        )
        res_link = adapter.publish(broadcast_link)
        self.assertTrue(res_link['success'])
        ugc_call_link = mock_post.call_args[1]['json']
        share_content_link = ugc_call_link['specificContent']['com.linkedin.ugc.ShareContent']
        self.assertEqual(share_content_link['shareMediaCategory'], 'ARTICLE')
        self.assertEqual(share_content_link['media'][0]['originalUrl'], 'https://example.com/blog/article2')

    @patch('requests.post')
    def test_instagram_adapter_carousel(self, mock_post):
        adapter = InstagramAdapter({'page_or_account_id': 'ig_123', 'access_token': 'tok_456'})
        broadcast = SocialBroadcast.objects.create(
            title="Carousel Post",
            message="Swipe to see more",
            media_urls=["https://example.com/slide1.jpg", "https://example.com/slide2.jpg"]
        )

        mock_child1 = MagicMock(status_code=200, content=b'{"id": "child_1"}')
        mock_child1.json.return_value = {"id": "child_1"}

        mock_child2 = MagicMock(status_code=200, content=b'{"id": "child_2"}')
        mock_child2.json.return_value = {"id": "child_2"}

        mock_parent = MagicMock(status_code=200, content=b'{"id": "parent_carousel"}')
        mock_parent.json.return_value = {"id": "parent_carousel"}

        mock_pub = MagicMock(status_code=200, content=b'{"id": "ig_post_999"}')
        mock_pub.json.return_value = {"id": "ig_post_999"}

        mock_post.side_effect = [mock_child1, mock_child2, mock_parent, mock_pub]

        res = adapter.publish(broadcast)
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'ig_post_999')

        parent_call = mock_post.call_args_list[2]
        self.assertEqual(parent_call[1]['data']['media_type'], 'CAROUSEL')
        self.assertEqual(parent_call[1]['data']['children'], 'child_1,child_2')

    @patch('requests.post')
    def test_facebook_adapter_carousel(self, mock_post):
        adapter = FacebookAdapter({'page_or_account_id': 'fb_123', 'access_token': 'tok_456'})
        broadcast = SocialBroadcast.objects.create(
            title="Album Post",
            message="Check out our album",
            media_urls=["https://example.com/pic1.jpg", "https://example.com/pic2.jpg"]
        )

        mock_p1 = MagicMock(status_code=200, content=b'{"id": "photo_1"}')
        mock_p1.json.return_value = {"id": "photo_1"}

        mock_p2 = MagicMock(status_code=200, content=b'{"id": "photo_2"}')
        mock_p2.json.return_value = {"id": "photo_2"}

        mock_feed = MagicMock(status_code=200, content=b'{"id": "feed_post_100"}')
        mock_feed.json.return_value = {"id": "feed_post_100"}

        mock_post.side_effect = [mock_p1, mock_p2, mock_feed]

        res = adapter.publish(broadcast)
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'feed_post_100')

        feed_call = mock_post.call_args_list[2]
        self.assertIn('attached_media[0]', feed_call[1]['data'])
        self.assertIn('attached_media[1]', feed_call[1]['data'])

    @patch('requests.post')
    def test_threads_adapter_carousel(self, mock_post):
        adapter = ThreadsAdapter({'page_or_account_id': 'th_123', 'access_token': 'tok_456'})
        broadcast = SocialBroadcast.objects.create(
            title="Threads Carousel",
            message="Multiple slides on Threads",
            media_urls=["https://example.com/t1.jpg", "https://example.com/t2.jpg"]
        )

        mock_c1 = MagicMock(status_code=200, content=b'{"id": "tc_1"}')
        mock_c1.json.return_value = {"id": "tc_1"}

        mock_c2 = MagicMock(status_code=200, content=b'{"id": "tc_2"}')
        mock_c2.json.return_value = {"id": "tc_2"}

        mock_parent = MagicMock(status_code=200, content=b'{"id": "th_parent"}')
        mock_parent.json.return_value = {"id": "th_parent"}

        mock_pub = MagicMock(status_code=200, content=b'{"id": "th_post_777"}')
        mock_pub.json.return_value = {"id": "th_post_777"}

        mock_post.side_effect = [mock_c1, mock_c2, mock_parent, mock_pub]

        res = adapter.publish(broadcast)
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'th_post_777')
        parent_call = mock_post.call_args_list[2]
        self.assertEqual(parent_call[1]['data']['media_type'], 'CAROUSEL')
        self.assertEqual(parent_call[1]['data']['children'], 'tc_1,tc_2')

    @patch('requests.get')
    @patch('requests.post')
    def test_instagram_adapter_video_reels_and_mixed_carousel(self, mock_post, mock_get):
        adapter = InstagramAdapter({'page_or_account_id': 'ig_123', 'access_token': 'tok_456'})

        mock_status = MagicMock(status_code=200, content=b'{"status_code": "FINISHED"}')
        mock_status.json.return_value = {"status_code": "FINISHED"}
        mock_get.return_value = mock_status

        # 1. Single Video (Reels)
        vid_broadcast = SocialBroadcast.objects.create(
            title="Launch Reel",
            message="Watch our demo",
            image_url="https://example.com/demo.mp4"
        )
        m_c = MagicMock(status_code=200, content=b'{"id": "reel_c1"}')
        m_c.json.return_value = {"id": "reel_c1"}
        m_p = MagicMock(status_code=200, content=b'{"id": "reel_pub1"}')
        m_p.json.return_value = {"id": "reel_pub1"}
        mock_post.side_effect = [m_c, m_p]

        res_reel = adapter.publish(vid_broadcast)
        self.assertTrue(res_reel['success'])
        self.assertEqual(mock_post.call_args_list[0][1]['data']['media_type'], 'REELS')
        self.assertEqual(mock_post.call_args_list[0][1]['data']['video_url'], 'https://example.com/demo.mp4')

        # 2. Mixed Image + Video Carousel
        mock_post.reset_mock()
        mix_broadcast = SocialBroadcast.objects.create(
            title="Mixed Carousel",
            message="Photo and video slides",
            media_urls=["https://example.com/photo.jpg", "https://example.com/clip.mp4"]
        )
        mc1 = MagicMock(status_code=200, content=b'{"id": "c_img"}')
        mc1.json.return_value = {"id": "c_img"}
        mc2 = MagicMock(status_code=200, content=b'{"id": "c_vid"}')
        mc2.json.return_value = {"id": "c_vid"}
        mp = MagicMock(status_code=200, content=b'{"id": "c_parent"}')
        mp.json.return_value = {"id": "c_parent"}
        mpub = MagicMock(status_code=200, content=b'{"id": "ig_mix_99"}')
        mpub.json.return_value = {"id": "ig_mix_99"}
        mock_post.side_effect = [mc1, mc2, mp, mpub]

        res_mix = adapter.publish(mix_broadcast)
        self.assertTrue(res_mix['success'])
        self.assertEqual(mock_post.call_args_list[0][1]['data']['image_url'], 'https://example.com/photo.jpg')
        self.assertEqual(mock_post.call_args_list[1][1]['data']['media_type'], 'VIDEO')
        self.assertEqual(mock_post.call_args_list[1][1]['data']['video_url'], 'https://example.com/clip.mp4')
        self.assertEqual(mock_post.call_args_list[2][1]['data']['media_type'], 'CAROUSEL')

    @patch('requests.post')
    def test_facebook_adapter_video_and_mixed_carousel(self, mock_post):
        adapter = FacebookAdapter({'page_or_account_id': 'pg_123', 'access_token': 'tok_456'})

        # 1. Single Video
        b_vid = SocialBroadcast.objects.create(
            title="FB Video",
            message="Single video post",
            image_url="https://example.com/video.mp4"
        )
        m_vid = MagicMock(status_code=200, content=b'{"id": "fb_vid_1"}')
        m_vid.json.return_value = {"id": "fb_vid_1"}
        mock_post.return_value = m_vid

        res1 = adapter.publish(b_vid)
        self.assertTrue(res1['success'])
        self.assertIn('/pg_123/videos', mock_post.call_args[0][0])
        self.assertEqual(mock_post.call_args[1]['data']['file_url'], 'https://example.com/video.mp4')

        # 2. Mixed Image + Video Carousel
        mock_post.reset_mock()
        b_mix = SocialBroadcast.objects.create(
            title="FB Mixed Album",
            message="Photo + Video",
            media_urls=["https://example.com/p1.jpg", "https://example.com/v1.mp4"]
        )
        m1 = MagicMock(status_code=200, content=b'{"id": "ph_1"}')
        m1.json.return_value = {"id": "ph_1"}
        m2 = MagicMock(status_code=200, content=b'{"id": "vd_1"}')
        m2.json.return_value = {"id": "vd_1"}
        mf = MagicMock(status_code=200, content=b'{"id": "pg_123_feed_99"}')
        mf.json.return_value = {"id": "pg_123_feed_99"}
        mock_post.side_effect = [m1, m2, mf]

        res2 = adapter.publish(b_mix)
        self.assertTrue(res2['success'])
        self.assertIn('/pg_123/photos', mock_post.call_args_list[0][0][0])
        self.assertIn('/pg_123/videos', mock_post.call_args_list[1][0][0])
        self.assertIn('/pg_123/feed', mock_post.call_args_list[2][0][0])
        self.assertIn('attached_media[1]', mock_post.call_args_list[2][1]['data'])

    @patch('requests.get')
    @patch('requests.post')
    def test_threads_adapter_video_carousel(self, mock_post, mock_get):
        adapter = ThreadsAdapter({'page_or_account_id': 'th_123', 'access_token': 'tok_456'})
        mock_status = MagicMock(status_code=200, content=b'{"status": "FINISHED"}')
        mock_status.json.return_value = {"status": "FINISHED"}
        mock_get.return_value = mock_status

        broadcast = SocialBroadcast.objects.create(
            title="Threads Mixed Carousel",
            message="Image and video",
            media_urls=["https://example.com/t1.jpg", "https://example.com/t2.mp4"]
        )
        mc1 = MagicMock(status_code=200, content=b'{"id": "tc_1"}')
        mc1.json.return_value = {"id": "tc_1"}
        mc2 = MagicMock(status_code=200, content=b'{"id": "tc_2"}')
        mc2.json.return_value = {"id": "tc_2"}
        mp = MagicMock(status_code=200, content=b'{"id": "th_parent"}')
        mp.json.return_value = {"id": "th_parent"}
        mpub = MagicMock(status_code=200, content=b'{"id": "th_post_888"}')
        mpub.json.return_value = {"id": "th_post_888"}
        mock_post.side_effect = [mc1, mc2, mp, mpub]

        res = adapter.publish(broadcast)
        self.assertTrue(res['success'])
        self.assertEqual(mock_post.call_args_list[1][1]['data']['media_type'], 'VIDEO')
        self.assertEqual(mock_post.call_args_list[1][1]['data']['video_url'], 'https://example.com/t2.mp4')
        self.assertEqual(mock_post.call_args_list[2][1]['data']['media_type'], 'CAROUSEL')

    @patch('requests.put')
    @patch('requests.get')
    @patch('requests.post')
    def test_linkedin_adapter_video(self, mock_post, mock_get, mock_put):
        adapter = LinkedInAdapter({'page_or_account_id': '123456', 'access_token': 'li_tok'})
        broadcast = SocialBroadcast.objects.create(
            title="LinkedIn Video",
            message="Video update",
            image_url="https://example.com/promo.mp4"
        )

        mock_get_res = MagicMock(status_code=200, content=b'fake_video_bytes')
        mock_get_res.json.return_value = {'recipes': [{'status': 'AVAILABLE'}]}
        mock_get.return_value = mock_get_res

        mock_reg = MagicMock(status_code=200, content=b'{"value": {"asset": "urn:li:digitalmediaAsset:vid_1"}}')
        mock_reg.json.return_value = {
            "value": {
                "asset": "urn:li:digitalmediaAsset:vid_1",
                "uploadMechanism": {
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                        "uploadUrl": "https://upload.linkedin.com/video"
                    }
                }
            }
        }
        mock_ugc = MagicMock(status_code=201, content=b'{"id": "urn:li:share:999"}')
        mock_ugc.json.return_value = {"id": "urn:li:share:999"}
        mock_post.side_effect = [mock_reg, mock_ugc]
        mock_put.return_value = MagicMock(status_code=201, content=b'')

        res = adapter.publish(broadcast)
        self.assertTrue(res['success'])
        reg_payload = mock_post.call_args_list[0][1]['json']
        self.assertEqual(reg_payload['registerUploadRequest']['recipes'], ['urn:li:digitalmediaRecipe:feedshare-video'])
        ugc_payload = mock_post.call_args_list[1][1]['json']
        self.assertEqual(ugc_payload['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'], 'VIDEO')

    @patch('requests.get')
    @patch('requests.post')
    def test_twitter_adapter_video_upload(self, mock_post, mock_get):
        adapter = TwitterAdapter({
            'api_key': 'k', 'api_secret': 's',
            'access_token': 'at', 'access_token_secret': 'ats'
        })
        broadcast = SocialBroadcast.objects.create(
            title="X Video",
            message="Watch this",
            image_url="https://example.com/clip.mp4"
        )

        mock_get.return_value = MagicMock(status_code=200, content=b'video_bytes')
        m_init = MagicMock(status_code=202, content=b'{"media_id_string": "tw_vid_123"}')
        m_init.json.return_value = {"media_id_string": "tw_vid_123"}
        m_app = MagicMock(status_code=204, content=b'')
        m_fin = MagicMock(status_code=201, content=b'{"media_id_string": "tw_vid_123"}')
        m_fin.json.return_value = {"media_id_string": "tw_vid_123"}
        m_tweet = MagicMock(status_code=201, content=b'{"data": {"id": "tweet_999"}}')
        m_tweet.json.return_value = {"data": {"id": "tweet_999"}}
        mock_post.side_effect = [m_init, m_app, m_fin, m_tweet]

        res = adapter.publish(broadcast)
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'tweet_999')
        self.assertEqual(mock_post.call_args_list[0][1]['data']['media_category'], 'tweet_video')
        self.assertEqual(mock_post.call_args_list[3][1]['json']['media'], {'media_ids': ['tw_vid_123']})



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

    @patch('django_social_autoposter.services.SocialBroadcastService.broadcast')
    def test_social_broadcast_api_carousel_post(self, mock_broadcast):
        fake_broadcast = SocialBroadcast.objects.create(
            title="Carousel API Broadcast",
            message="Swipe for slides",
            media_urls=["https://example.com/s1.jpg", "https://example.com/s2.jpg"],
            target_platforms=['instagram', 'facebook']
        )
        mock_broadcast.return_value = fake_broadcast

        res = self.client.post('/social/broadcast/', {
            'title': 'Carousel API Broadcast',
            'message': 'Swipe for slides',
            'media_urls': ['https://example.com/s1.jpg', 'https://example.com/s2.jpg'],
            'platforms': ['instagram', 'facebook']
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], 'Carousel API Broadcast')
        self.assertEqual(len(res.data['media_urls']), 2)
        self.assertEqual(len(res.data['all_media_urls']), 2)

    @patch('django_social_autoposter.services.SocialMessagingService.send_message')
    def test_social_message_send_api(self, mock_send_message):
        mock_dm = SocialDirectMessage.objects.create(
            platform='whatsapp',
            recipient_id='+1234567890',
            message='Hello there!',
            direction='outbound',
            status='delivered',
            external_message_id='wamid.12345'
        )
        mock_send_message.return_value = mock_dm

        payload = {
            'platform': 'whatsapp',
            'recipient_id': '+1234567890',
            'message': 'Hello there!'
        }
        res = self.client.post('/social/messages/send/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['platform'], 'whatsapp')
        self.assertEqual(res.data['recipient_id'], '+1234567890')
        self.assertEqual(res.data['status'], 'delivered')
        self.assertEqual(res.data['external_message_id'], 'wamid.12345')

    def test_social_message_list_and_detail_api(self):
        dm1 = SocialDirectMessage.objects.create(
            platform='whatsapp',
            recipient_id='15551234567',
            message='WhatsApp Msg',
            direction='outbound',
            status='delivered'
        )
        dm2 = SocialDirectMessage.objects.create(
            platform='facebook',
            recipient_id='fb_psid_456',
            message='FB Msg',
            direction='outbound',
            status='failed'
        )

        # List all
        res = self.client.get('/social/messages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        # Filter by platform
        res_filtered = self.client.get('/social/messages/?platform=whatsapp')
        self.assertEqual(res_filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_filtered.data), 1)
        self.assertEqual(res_filtered.data[0]['recipient_id'], '15551234567')

        # Retrieve detail
        res_detail = self.client.get(f'/social/messages/{dm1.id}/')
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data['id'], dm1.id)
        self.assertEqual(res_detail.data['message'], 'WhatsApp Msg')


class SocialMessagingAdapterTests(TestCase):
    @patch('requests.post')
    def test_facebook_adapter_dm(self, mock_post):
        # 1. Missing credentials
        adapter_missing = FacebookAdapter({})
        res_missing = adapter_missing.send_direct_message('12345', 'Hello')
        self.assertFalse(res_missing['success'])
        self.assertIn("Missing Facebook Page Access Token", res_missing['error'])

        # 2. Successful text message
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.content = b'{"recipient_id": "12345", "message_id": "mid.fb.123"}'
        mock_res.json.return_value = {"recipient_id": "12345", "message_id": "mid.fb.123"}
        mock_post.return_value = mock_res

        adapter = FacebookAdapter({'access_token': 'fb_page_tok'})
        res = adapter.send_direct_message('12345', 'Hello FB user')
        self.assertTrue(res['success'])
        self.assertEqual(res['message_id'], 'mid.fb.123')

        # 3. 24-hour customer window error
        mock_err = MagicMock()
        mock_err.status_code = 400
        mock_err.content = b'{"error": {"message": "Message failed to send", "code": 10, "error_subcode": 2018001}}'
        mock_err.json.return_value = {
            "error": {"message": "Message failed to send", "code": 10, "error_subcode": 2018001}
        }
        mock_post.return_value = mock_err
        res_err = adapter.send_direct_message('12345', 'Outside window')
        self.assertFalse(res_err['success'])
        self.assertIn("24-hour standard messaging window", res_err['error'])

    @patch('requests.post')
    def test_instagram_adapter_dm(self, mock_post):
        # 1. Missing credentials
        adapter_missing = InstagramAdapter({})
        res_missing = adapter_missing.send_direct_message('ig_user_1', 'Hi IG')
        self.assertFalse(res_missing['success'])

        # 2. Success send
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.content = b'{"recipient_id": "ig_user_1", "message_id": "mid.ig.999"}'
        mock_res.json.return_value = {"recipient_id": "ig_user_1", "message_id": "mid.ig.999"}
        mock_post.return_value = mock_res

        adapter = InstagramAdapter({'access_token': 'ig_tok_abc'})
        res = adapter.send_direct_message('ig_user_1', 'Hi IG')
        self.assertTrue(res['success'])
        self.assertEqual(res['message_id'], 'mid.ig.999')

    @patch('requests.post')
    def test_twitter_adapter_dm(self, mock_post):
        # 1. Missing credentials
        adapter_missing = TwitterAdapter({})
        res_missing = adapter_missing.send_direct_message('x_user_123', 'Hey on X')
        self.assertFalse(res_missing['success'])
        self.assertIn("Direct messaging requires User Context", res_missing['error'])

        # 2. Success send via OAuth1
        mock_res = MagicMock()
        mock_res.status_code = 201
        mock_res.content = b'{"data": {"dm_event_id": "evt_tw_12345", "dm_conversation_id": "conv_999"}}'
        mock_res.json.return_value = {
            "data": {"dm_event_id": "evt_tw_12345", "dm_conversation_id": "conv_999"}
        }
        mock_post.return_value = mock_res

        adapter = TwitterAdapter({
            'api_key': 'k', 'api_secret': 's',
            'access_token': 't', 'access_token_secret': 'ts'
        })
        res = adapter.send_direct_message('x_user_123', 'Hey on X')
        self.assertTrue(res['success'])
        self.assertEqual(res['message_id'], 'evt_tw_12345')
        self.assertEqual(res['conversation_id'], 'conv_999')

    @patch('requests.post')
    def test_whatsapp_adapter(self, mock_post):
        # 1. Missing credentials
        adapter_missing = WhatsAppAdapter({})
        res_missing = adapter_missing.send_direct_message('+1 (555) 000-1111', 'Hello')
        self.assertFalse(res_missing['success'])
        self.assertIn("Missing WhatsApp credentials", res_missing['error'])

        # 2. Phone normalization and text message send
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.content = b'{"messages": [{"id": "wamid.HBgL..."}]}'
        mock_res.json.return_value = {"messages": [{"id": "wamid.HBgL..."}]}
        mock_post.return_value = mock_res

        adapter = WhatsAppAdapter({
            'page_or_account_id': '10987654321',
            'access_token': 'wa_tok_123'
        })
        res = adapter.send_direct_message('+1 (555) 234-5678', 'Hello WhatsApp!')
        self.assertTrue(res['success'])
        self.assertEqual(res['message_id'], 'wamid.HBgL...')

        # Verify normalized phone number in request body
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs['json']['to'], '15552345678')
        self.assertEqual(call_kwargs['json']['type'], 'text')
        self.assertEqual(call_kwargs['json']['text']['body'], 'Hello WhatsApp!')

        # 3. Media message send
        res_media = adapter.send_direct_message(
            '15552345678',
            'Image caption',
            media_url='https://example.com/receipt.pdf',
            extra_params={'media_type': 'document'}
        )
        self.assertTrue(res_media['success'])
        call_kwargs_media = mock_post.call_args[1]
        self.assertEqual(call_kwargs_media['json']['type'], 'document')
        self.assertEqual(call_kwargs_media['json']['document']['link'], 'https://example.com/receipt.pdf')

    @patch('requests.post')
    def test_linkedin_adapter_dm(self, mock_post):
        # 1. Missing access token
        adapter_missing = LinkedInAdapter({})
        res_missing = adapter_missing.send_direct_message('person_123', 'Hi on LinkedIn')
        self.assertFalse(res_missing['success'])
        self.assertIn("Missing LinkedIn Access Token", res_missing['error'])

        # 2. Successful send with URN formatting
        mock_res = MagicMock()
        mock_res.status_code = 201
        mock_res.content = b'{"value": {"conversation": "urn:li:fs_conversation:123"}, "id": "urn:li:fs_event:456"}'
        mock_res.json.return_value = {
            "value": {"conversation": "urn:li:fs_conversation:123"},
            "id": "urn:li:fs_event:456"
        }
        mock_post.return_value = mock_res

        adapter = LinkedInAdapter({'access_token': 'li_tok_abc'})
        res = adapter.send_direct_message('12345', 'Hi on LinkedIn')
        self.assertTrue(res['success'])
        self.assertEqual(res['message_id'], 'urn:li:fs_event:456')
        self.assertEqual(res['conversation_id'], 'urn:li:fs_conversation:123')

        # Verify URN formatted in payload
        call_kwargs = mock_post.call_args[1]
        recipients = call_kwargs['json']['recipients']
        self.assertEqual(recipients, ['urn:li:person:12345'])


class SocialMessagingServiceTests(TestCase):
    def test_validation(self):
        # Missing recipient
        with self.assertRaises(ValueError):
            SocialMessagingService.send_message(
                platform='whatsapp',
                recipient_id='',
                message='Hello'
            )

        # Missing both message and media_url
        with self.assertRaises(ValueError):
            SocialMessagingService.send_message(
                platform='whatsapp',
                recipient_id='12345',
                message='',
                media_url=None
            )

    @patch('django_social_autoposter.adapters.whatsapp.WhatsAppAdapter.send_direct_message')
    def test_service_execution(self, mock_send_dm):
        mock_send_dm.return_value = {
            'success': True,
            'message_id': 'wamid.success.123',
            'conversation_id': None,
            'error': None,
            'raw_response': {'id': 'wamid.success.123'}
        }

        # Enable whatsapp in DB
        SocialPlatformConfig.objects.create(
            platform='whatsapp',
            is_enabled=True,
            page_or_account_id='10987654321',
            access_token='wa_tok_valid'
        )

        dm = SocialMessagingService.send_message(
            platform='whatsapp',
            recipient_id='15551234567',
            message='Order confirmation #4321'
        )

        self.assertEqual(dm.status, 'delivered')
        self.assertEqual(dm.external_message_id, 'wamid.success.123')
        self.assertEqual(dm.direction, 'outbound')
        self.assertIsNone(dm.error_message)


class SocialSchedulingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='schedulertester@example.com', password='password123'
        )

    def test_broadcast_scheduling_reschedule_and_cancel(self):
        future_time = timezone.now() + timedelta(days=2)
        broadcast = SocialBroadcastService.broadcast(
            title="Scheduled Post",
            message="This post is queued for next week.",
            platforms=['facebook'],
            scheduled_at=future_time
        )

        self.assertEqual(broadcast.status, 'scheduled')
        self.assertEqual(broadcast.scheduled_at, future_time)
        self.assertIsNone(broadcast.published_at)
        self.assertEqual(broadcast.logs.count(), 0)

        # Reschedule
        new_time = timezone.now() + timedelta(days=5)
        rescheduled = SocialBroadcastService.reschedule_broadcast(broadcast.id, new_time)
        self.assertEqual(rescheduled.scheduled_at, new_time)
        self.assertEqual(rescheduled.status, 'scheduled')

        # Cancel
        cancelled = SocialBroadcastService.cancel_broadcast(broadcast.id)
        self.assertEqual(cancelled.status, 'cancelled')

        # Cannot reschedule cancelled
        with self.assertRaises(ValueError):
            SocialBroadcastService.reschedule_broadcast(broadcast.id, timezone.now() + timedelta(days=6))

    def test_direct_message_scheduling_reschedule_and_cancel(self):
        future_time = timezone.now() + timedelta(hours=12)
        dm = SocialMessagingService.send_message(
            platform='whatsapp',
            recipient_id='15551234567',
            message='Your appointment reminder',
            scheduled_at=future_time
        )

        self.assertEqual(dm.status, 'scheduled')
        self.assertEqual(dm.scheduled_at, future_time)
        self.assertIsNone(dm.sent_at)

        # Reschedule
        new_time = timezone.now() + timedelta(days=1)
        rescheduled = SocialMessagingService.reschedule_message(dm.id, new_time)
        self.assertEqual(rescheduled.scheduled_at, new_time)
        self.assertEqual(rescheduled.status, 'scheduled')

        # Cancel
        cancelled = SocialMessagingService.cancel_message(dm.id)
        self.assertEqual(cancelled.status, 'cancelled')

    @patch('django_social_autoposter.adapters.facebook.FacebookAdapter.publish')
    @patch('django_social_autoposter.adapters.whatsapp.WhatsAppAdapter.send_direct_message')
    def test_scheduler_process_due_schedules(self, mock_wa_dm, mock_fb_pub):
        mock_fb_pub.return_value = {
            'success': True,
            'post_id': 'fb_pub_sched_1',
            'post_url': 'https://facebook.com/fb_pub_sched_1',
            'error': None,
            'raw_response': {'id': 'fb_pub_sched_1'}
        }
        mock_wa_dm.return_value = {
            'success': True,
            'message_id': 'wamid.sched.999',
            'conversation_id': None,
            'error': None,
            'raw_response': {'id': 'wamid.sched.999'}
        }

        SocialPlatformConfig.objects.create(
            platform='facebook', is_enabled=True, access_token='fb_token_sched'
        )
        SocialPlatformConfig.objects.create(
            platform='whatsapp', is_enabled=True, page_or_account_id='12345', access_token='wa_token_sched'
        )

        # Due broadcast (in the past)
        due_broadcast = SocialBroadcast.objects.create(
            title="Due Broadcast",
            message="Publish me now",
            target_platforms=['facebook'],
            status='scheduled',
            scheduled_at=timezone.now() - timedelta(minutes=5)
        )
        # Future broadcast (should remain scheduled)
        future_broadcast = SocialBroadcast.objects.create(
            title="Future Broadcast",
            message="Do not publish yet",
            target_platforms=['facebook'],
            status='scheduled',
            scheduled_at=timezone.now() + timedelta(days=1)
        )

        # Due message
        due_dm = SocialDirectMessage.objects.create(
            platform='whatsapp',
            recipient_id='15551234567',
            message='Due reminder',
            status='scheduled',
            scheduled_at=timezone.now() - timedelta(minutes=10)
        )
        # Future message
        future_dm = SocialDirectMessage.objects.create(
            platform='whatsapp',
            recipient_id='15551234567',
            message='Future reminder',
            status='scheduled',
            scheduled_at=timezone.now() + timedelta(days=2)
        )

        # Run scheduler
        stats = SocialSchedulerService.process_due_schedules()
        self.assertEqual(stats['broadcasts_due'], 1)
        self.assertEqual(stats['broadcasts_processed'], 1)
        self.assertEqual(stats['messages_due'], 1)
        self.assertEqual(stats['messages_processed'], 1)

        due_broadcast.refresh_from_db()
        self.assertEqual(due_broadcast.status, 'completed')
        self.assertIsNotNone(due_broadcast.published_at)

        future_broadcast.refresh_from_db()
        self.assertEqual(future_broadcast.status, 'scheduled')

        due_dm.refresh_from_db()
        self.assertEqual(due_dm.status, 'delivered')
        self.assertIsNotNone(due_dm.sent_at)

        future_dm.refresh_from_db()
        self.assertEqual(future_dm.status, 'scheduled')

    def test_management_command(self):
        # Test dry-run and live run via call_command
        call_command('process_scheduled_social_posts', dry_run=True)
        call_command('process_scheduled_social_posts')


class SocialSchedulingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='schedulingapi@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_schedule_and_control_broadcast_api(self):
        future_str = (timezone.now() + timedelta(days=3)).isoformat()
        res = self.client.post('/social/broadcast/', {
            'title': 'API Scheduled Post',
            'message': 'Scheduled via API',
            'platforms': ['facebook'],
            'scheduled_at': future_str
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'scheduled')
        broadcast_id = res.data['id']

        # Reschedule API
        new_time_str = (timezone.now() + timedelta(days=4)).isoformat()
        res_reschedule = self.client.post(f'/social/broadcast/{broadcast_id}/reschedule/', {
            'scheduled_at': new_time_str
        }, format='json')
        self.assertEqual(res_reschedule.status_code, status.HTTP_200_OK)
        self.assertEqual(res_reschedule.data['status'], 'scheduled')

        # Cancel API
        res_cancel = self.client.post(f'/social/broadcast/{broadcast_id}/cancel/')
        self.assertEqual(res_cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(res_cancel.data['status'], 'cancelled')

    def test_schedule_and_control_message_api(self):
        future_str = (timezone.now() + timedelta(days=2)).isoformat()
        res = self.client.post('/social/messages/send/', {
            'platform': 'whatsapp',
            'recipient_id': '+15551234567',
            'message': 'Scheduled WA message',
            'scheduled_at': future_str
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'scheduled')
        dm_id = res.data['id']

        # Cancel message API
        res_cancel = self.client.post(f'/social/messages/{dm_id}/cancel/')
        self.assertEqual(res_cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(res_cancel.data['status'], 'cancelled')

    def test_scheduled_overview_api(self):
        # Create scheduled broadcast and message
        SocialBroadcast.objects.create(
            title="Overview Broadcast",
            message="Check me out",
            status='scheduled',
            scheduled_at=timezone.now() + timedelta(days=1)
        )
        SocialDirectMessage.objects.create(
            platform='whatsapp',
            recipient_id='15551234567',
            message='Overview DM',
            status='scheduled',
            scheduled_at=timezone.now() + timedelta(days=1)
        )

        res = self.client.get('/social/scheduled/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['scheduled_broadcasts']), 1)
        self.assertEqual(len(res.data['scheduled_messages']), 1)
