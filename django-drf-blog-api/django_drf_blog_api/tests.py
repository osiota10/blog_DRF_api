from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import MagazineSeries, Post, Category, SocialPlatformConfig, SocialPostLog
from .signals import dispatch_social_posts

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
