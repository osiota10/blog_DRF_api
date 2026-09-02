from django.urls import path
from .views import (
    ContactFormView, EmailSubcriptionView, OurClientView, OurSponsorView,
    ServiceCategoryView, ProductCategoryView, ServiceView, ProductView,
    TestimonialView, OurTeamView, CompanyInfoView, SocialUrlView, FaqView,
    CoreValueView, EventView, HeroSectionView, StatView
)

urlpatterns = [
    # Contact Us
    path('contact-us/', ContactFormView.as_view(), name='contact-us-list-create'),
    path('contact-us/<int:pk>/', ContactFormView.as_view(), name='contact-us-detail-pk'),

    # Email Subscription
    path('email-subscription/', EmailSubcriptionView.as_view(), name='email-subscription-list-create'),
    path('email-subscription/<int:pk>/', EmailSubcriptionView.as_view(), name='email-subscription-detail-pk'),

    # Our Clients
    path('clients/', OurClientView.as_view(), name='clients-list-create'),
    path('clients/<int:pk>/', OurClientView.as_view(), name='clients-detail-pk'),

    # Our Sponsors
    path('sponsors/', OurSponsorView.as_view(), name='sponsors-list-create'),
    path('sponsors/<int:pk>/', OurSponsorView.as_view(), name='sponsors-detail-pk'),

    # Service Categories
    path('service-categories/', ServiceCategoryView.as_view(), name='service-categories-list-create'),
    path('service-categories/<int:pk>/', ServiceCategoryView.as_view(), name='service-categories-detail-pk'),

    # Product Categories
    path('product-categories/', ProductCategoryView.as_view(), name='product-categories-list-create'),
    path('product-categories/<int:pk>/', ProductCategoryView.as_view(), name='product-categories-detail-pk'),

    # Services
    path('our-services/', ServiceView.as_view(), name='service-list-create'),
    path('our-services/<int:pk>/', ServiceView.as_view(), name='service-detail-pk'),
    path('our-services/<slug:slug>/', ServiceView.as_view(), name='service-detail-slug'),

    # Products
    path('products/', ProductView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductView.as_view(), name='product-detail-pk'),
    path('products/<slug:slug>/', ProductView.as_view(), name='product-detail-slug'),

    # Testimonials
    path('testimonials/', TestimonialView.as_view(), name='testimonials-list-create'),
    path('testimonials/<int:pk>/', TestimonialView.as_view(), name='testimonials-detail-pk'),

    # Our Team
    path('our-teams/', OurTeamView.as_view(), name='our-teams-list-create'),
    path('our-teams/<int:pk>/', OurTeamView.as_view(), name='our-teams-detail-pk'),

    # Company Info (Singleton)
    path('company-info/', CompanyInfoView.as_view(), name='company-info-singleton'),
    path('company-info/<int:id>/', CompanyInfoView.as_view(), name='company-info-detail-id'),

    # Social URLs
    path('social-urls/', SocialUrlView.as_view(), name='social-urls-list-create'),
    path('social-urls/<int:pk>/', SocialUrlView.as_view(), name='social-urls-detail-pk'),

    # FAQs
    path('faqs/', FaqView.as_view(), name='faqs-list-create'),
    path('faqs/<int:pk>/', FaqView.as_view(), name='faqs-detail-pk'),

    # Core Values
    path('core-values/', CoreValueView.as_view(), name='core-values-list-create'),
    path('core-values/<int:pk>/', CoreValueView.as_view(), name='core-values-detail-pk'),

    # Events
    path('events/', EventView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventView.as_view(), name='event-detail-pk'),
    path('events/<slug:slug>/', EventView.as_view(), name='event-detail-slug'),

    # Hero Section
    path('hero-section/', HeroSectionView.as_view(), name='hero-section-list-create'),
    path('hero-section/<int:pk>/', HeroSectionView.as_view(), name='hero-section-detail-pk'),

    # Stats
    path('stat/', StatView.as_view(), name='stat-list-create'),
    path('stat/<int:pk>/', StatView.as_view(), name='stat-detail-pk'),
]
