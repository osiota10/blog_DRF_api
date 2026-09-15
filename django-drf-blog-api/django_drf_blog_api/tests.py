from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import MagazineSeries

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
