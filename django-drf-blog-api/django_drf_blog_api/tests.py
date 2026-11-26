from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import MagazineSeries, Post, Category, SocialPlatformConfig, SocialPostLog
from .signals import dispatch_social_posts
from .social_posters import ThreadsPoster, TikTokPoster, LinkedInPoster, InstagramPoster

User = get_user_model()


class MagazineSeriesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='admin@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_magazine_series_crud(self):
        # 1. Create Magazine (POST)
        res = self.client.post('/django_drf_blog_api/magazines/', {
            'series_number': 'Series 42',
            'edition_code': 'VOL. 42 • NO. 01',
            'date': 'January 2026',
            'title': 'Tech Innovation Magazine',
            'subtitle': 'The future of AI and software',
            'editorial_summary': 'Full summary here'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mag_id = res.data['id']
        mag_slug = res.data['slug']

        # 2. List Magazines (GET)
        res = self.client.get('/django_drf_blog_api/magazines/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 3. Retrieve Detail by Slug & PK (GET)
        res_slug = self.client.get(f'/django_drf_blog_api/magazines/{mag_slug}/')
        self.assertEqual(res_slug.status_code, status.HTTP_200_OK)
        res_pk = self.client.get(f'/django_drf_blog_api/magazines/{mag_id}/')
        self.assertEqual(res_pk.status_code, status.HTTP_200_OK)

        # 4. Update Magazine (PATCH)
        res_update = self.client.patch(f'/django_drf_blog_api/magazines/{mag_id}/', {
            'title': 'Updated Tech Magazine'
        })
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        self.assertEqual(res_update.data['title'], 'Updated Tech Magazine')

        # 5. Delete Magazine (DELETE)
        res_delete = self.client.delete(f'/django_drf_blog_api/magazines/{mag_id}/')
        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)


class SocialAutoPosterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='social_admin@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Tech')

    def test_social_platform_config_crud(self):
        res = self.client.post('/django_drf_blog_api/social-configs/', {
            'platform': 'facebook',
            'is_enabled': True,
            'page_or_account_id': '123456789',
            'access_token': 'test_token_123'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res_list = self.client.get('/django_drf_blog_api/social-configs/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)

    @patch('django_drf_blog_api.social_posters.FacebookPoster.publish')
    def test_dispatch_social_posts_trigger(self, mock_publish):
        mock_publish.return_value = {
            'success': True,
            'post_id': 'fb_12345',
            'post_url': 'https://facebook.com/fb_12345'
        }
        SocialPlatformConfig.objects.create(
            platform='facebook',
            is_enabled=True,
            page_or_account_id='987654321',
            access_token='token'
        )
        post = Post.objects.create(
            title='Breaking AI News',
            content='AI is evolving rapidly.',
            category=self.category
        )
        dispatch_social_posts(post.id)

        log = SocialPostLog.objects.filter(post=post, platform='facebook').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'published')
        self.assertEqual(log.external_post_id, 'fb_12345')

    @patch('requests.post')
    def test_threads_and_tiktok_posters(self, mock_post):
        post = Post.objects.create(
            title='Threads and TikTok Update',
            content='Publishing across more channels.',
            featured_image_url='https://example.com/cover.jpg',
            category=self.category
        )

        # Threads poster test
        threads_poster = ThreadsPoster({
            'page_or_account_id': 'th_user_1',
            'access_token': 'th_token_1'
        })
        mock_container = patch('requests.post').start()
        mock_res1 = type('Response', (), {'status_code': 200, 'content': b'{"id": "c1"}', 'json': lambda s: {"id": "c1"}})()
        mock_res2 = type('Response', (), {'status_code': 200, 'content': b'{"id": "p1"}', 'json': lambda s: {"id": "p1"}})()
        mock_container.side_effect = [mock_res1, mock_res2]

        res_th = threads_poster.publish(post, 'https://example.com/blog/1')
        self.assertTrue(res_th['success'])
        self.assertEqual(res_th['post_id'], 'p1')

        # TikTok poster test
        tiktok_poster = TikTokPoster({
            'page_or_account_id': 'tt_user_1',
            'access_token': 'tt_token_1'
        })
        mock_tt_res = type('Response', (), {
            'status_code': 200,
            'content': b'{"data": {"publish_id": "tt_pub_1"}, "error": {"code": "ok"}}',
            'json': lambda s: {"data": {"publish_id": "tt_pub_1"}, "error": {"code": "ok"}}
        })()
        mock_container.side_effect = None
        mock_container.return_value = mock_tt_res

        res_tt = tiktok_poster.publish(post, 'https://example.com/blog/1')
        self.assertTrue(res_tt['success'])
        self.assertEqual(res_tt['post_id'], 'tt_pub_1')
        patch.stopall()

    @patch('requests.post')
    def test_instagram_poster_carousel(self, mock_post):
        post = Post.objects.create(
            title='Instagram Carousel News',
            content='Multiple slides in blog post.',
            featured_image_url='https://example.com/slide1.jpg',
            category=self.category
        )
        post.gallery_images = ['https://example.com/slide2.jpg']

        ig_poster = InstagramPoster({
            'page_or_account_id': 'ig_act_99',
            'access_token': 'ig_tok_99'
        })

        mock_c1 = type('Response', (), {'status_code': 200, 'content': b'{"id": "ig_c1"}', 'json': lambda s: {"id": "ig_c1"}})()
        mock_c2 = type('Response', (), {'status_code': 200, 'content': b'{"id": "ig_c2"}', 'json': lambda s: {"id": "ig_c2"}})()
        mock_parent = type('Response', (), {'status_code': 200, 'content': b'{"id": "ig_parent"}', 'json': lambda s: {"id": "ig_parent"}})()
        mock_pub = type('Response', (), {'status_code': 200, 'content': b'{"id": "ig_pub_done"}', 'json': lambda s: {"id": "ig_pub_done"}})()
        mock_post.side_effect = [mock_c1, mock_c2, mock_parent, mock_pub]

        res = ig_poster.publish(post, 'https://example.com/blog/carousel')
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'ig_pub_done')

    @patch('requests.put')
    @patch('requests.get')
    @patch('requests.post')
    def test_linkedin_poster_with_image_and_article(self, mock_post, mock_get, mock_put):
        post_with_image = Post.objects.create(
            title='AI Advances in 2026',
            excerpt='A breakthrough year for AI agents.',
            featured_image_url='https://example.com/ai_image.png',
            category=self.category
        )

        linkedin_poster = LinkedInPoster({
            'page_or_account_id': '12345678',
            'access_token': 'li_test_tok'
        })

        # Mock image download & asset status check
        mock_get_res = type('Response', (), {
            'status_code': 200,
            'content': b'image_data',
            'json': lambda s=None: {'recipes': [{'status': 'AVAILABLE'}]}
        })()
        mock_get.return_value = mock_get_res

        # Mock registerUpload and ugcPosts
        mock_reg_res = type('Response', (), {
            'status_code': 200,
            'content': b'{"value": {"asset": "urn:li:digitalmediaAsset:li_img_123", "uploadMechanism": {"com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {"uploadUrl": "https://upload.linkedin.com/image"}}}}',
            'json': lambda s: {
                "value": {
                    "asset": "urn:li:digitalmediaAsset:li_img_123",
                    "uploadMechanism": {
                        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                            "uploadUrl": "https://upload.linkedin.com/image"
                        }
                    }
                }
            }
        })()
        mock_ugc_res = type('Response', (), {
            'status_code': 201,
            'content': b'{"id": "urn:li:share:li_post_789"}',
            'json': lambda s: {"id": "urn:li:share:li_post_789"}
        })()
        mock_post.side_effect = [mock_reg_res, mock_ugc_res]

        mock_put_res = type('Response', (), {'status_code': 201, 'content': b''})()
        mock_put.return_value = mock_put_res

        res = linkedin_poster.publish(post_with_image, 'https://example.com/blog/ai-advances')
        self.assertTrue(res['success'])
        self.assertEqual(res['post_id'], 'urn:li:share:li_post_789')
        self.assertIn("https://www.linkedin.com/feed/update/urn:li:share:li_post_789", res['post_url'])

        # Verify UGC payload had IMAGE media category
        ugc_call = mock_post.call_args_list[1]
        payload = ugc_call[1]['json']
        share_content = payload['specificContent']['com.linkedin.ugc.ShareContent']
        self.assertEqual(share_content['shareMediaCategory'], 'IMAGE')
        self.assertEqual(share_content['media'][0]['media'], 'urn:li:digitalmediaAsset:li_img_123')
