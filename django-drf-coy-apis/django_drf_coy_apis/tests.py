from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    CompanyInfo, ServiceCategory, Service, ProductCategory, Product,
    ContactForm, EmailSubcription, OurClient, OurSponsor, Stat,
    Testimonial, OurTeam, SocialUrl, FAQ, CoreValue, HeroSection,
    Event
)

User = get_user_model()


class CorporateAPICRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='admin@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_company_info_crud(self):
        # Create
        res = self.client.post('/django_drf_coy_apis/company-info/', {
            'company_name': 'Test Tech Studio',
            'company_address': '123 Tech Street',
            'email': 'contact@testtech.com'
        })
        self.assertIn(res.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        coy_id = res.data['id']

        # Read List
        res = self.client.get('/django_drf_coy_apis/company-info/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Read Detail
        res = self.client.get(f'/django_drf_coy_apis/company-info/{coy_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Update
        res = self.client.patch(f'/django_drf_coy_apis/company-info/{coy_id}/', {
            'company_name': 'Updated Tech Studio'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['company_name'], 'Updated Tech Studio')

        # Delete (prevented)
        res = self.client.delete(f'/django_drf_coy_apis/company-info/{coy_id}/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_service_crud(self):
        # Create
        res = self.client.post('/django_drf_coy_apis/our-services/', {
            'title': 'Web Development',
            'description': '<p>Custom website development</p>',
            'slug': 'web-development'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        service_id = res.data['id']

        # Read List
        res = self.client.get('/django_drf_coy_apis/our-services/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Read Detail by Slug
        res = self.client.get('/django_drf_coy_apis/our-services/web-development/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Read Detail by ID
        res = self.client.get(f'/django_drf_coy_apis/our-services/{service_id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Update
        res = self.client.patch(f'/django_drf_coy_apis/our-services/{service_id}/', {
            'title': 'Advanced Web Development'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete
        res = self.client.delete(f'/django_drf_coy_apis/our-services/{service_id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_crud(self):
        # Create
        res = self.client.post('/django_drf_coy_apis/products/', {
            'title': 'SaaS Platform',
            'description': '<p>Enterprise SaaS Product</p>',
            'slug': 'saas-platform'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        prod_id = res.data['id']

        # Read Detail by Slug & ID
        res_slug = self.client.get('/django_drf_coy_apis/products/saas-platform/')
        self.assertEqual(res_slug.status_code, status.HTTP_200_OK)
        res_id = self.client.get(f'/django_drf_coy_apis/products/{prod_id}/')
        self.assertEqual(res_id.status_code, status.HTTP_200_OK)

        # Delete
        res = self.client.delete(f'/django_drf_coy_apis/products/{prod_id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_our_team_crud(self):
        # Create without user (fallback to name & phone_number)
        res = self.client.post('/django_drf_coy_apis/our-teams/', {
            'name': 'John Doe',
            'phone_number': '+123456789',
            'position': 'Lead Architect',
            'bio': '<p>Experienced developer</p>',
            'facebook_url': 'https://facebook.com/johndoe',
            'github_url': 'https://github.com/johndoe'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        team_id = res.data['id']
        self.assertEqual(res.data['display_name'], 'John Doe')
        self.assertEqual(res.data['display_phone_number'], '+123456789')

        # Link to authenticated user
        res = self.client.patch(f'/django_drf_coy_apis/our-teams/{team_id}/', {
            'user_id': self.user.id,
            'position': 'CTO'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['position'], 'CTO')

        # Delete
        res = self.client.delete(f'/django_drf_coy_apis/our-teams/{team_id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_auto_slug_signal(self):
        s1 = Service.objects.create(title='Cloud Migration', description='Migrate to cloud')
        self.assertEqual(s1.slug, 'cloud-migration')

        s2 = Service.objects.create(title='Cloud Migration', description='Another cloud service')
        self.assertTrue(s2.slug.startswith('cloud-migration-'))

