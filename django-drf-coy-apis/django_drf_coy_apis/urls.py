from django.urls import path
from .views import *

urlpatterns = [
    # Contact Forms
    path('contact-us', ContactFormView.as_view(), name='contact-us-list-create'),
    path('contact-us/', ContactFormView.as_view(), name='contact-us-list-create-slash'),
    path('contact-us/<int:pk>', ContactFormView.as_view(), name='contact-us-detail'),
    path('contact-us/<int:pk>/', ContactFormView.as_view(), name='contact-us-detail-slash'),

    # Email Subscription
    path('email-subscription', EmailSubcriptionView.as_view(), name='email-subscription-list-create'),
    path('email-subscription/', EmailSubcriptionView.as_view(), name='email-subscription-list-create-slash'),
    path('email-subscription/<int:pk>', EmailSubcriptionView.as_view(), name='email-subscription-detail'),
    path('email-subscription/<int:pk>/', EmailSubcriptionView.as_view(), name='email-subscription-detail-slash'),

    # Company Clients
    path('clients', OurClientView.as_view(), name='clients-list-create'),
    path('clients/', OurClientView.as_view(), name='clients-list-create-slash'),
    path('clients/<int:pk>', OurClientView.as_view(), name='clients-detail'),
    path('clients/<int:pk>/', OurClientView.as_view(), name='clients-detail-slash'),

    # Company Sponsors
    path('sponsors', OurSponsorView.as_view(), name='sponsors-list-create'),
    path('sponsors/', OurSponsorView.as_view(), name='sponsors-list-create-slash'),
    path('sponsors/<int:pk>', OurSponsorView.as_view(), name='sponsors-detail'),
    path('sponsors/<int:pk>/', OurSponsorView.as_view(), name='sponsors-detail-slash'),

    # Service Categories
    path('service-categories', ServiceCategoryView.as_view(), name='service-categories-list-create'),
    path('service-categories/', ServiceCategoryView.as_view(), name='service-categories-list-create-slash'),
    path('service-categories/<int:pk>', ServiceCategoryView.as_view(), name='service-categories-detail'),
    path('service-categories/<int:pk>/', ServiceCategoryView.as_view(), name='service-categories-detail-slash'),

    # Product Categories
    path('product-categories', ProductCategoryView.as_view(), name='product-categories-list-create'),
    path('product-categories/', ProductCategoryView.as_view(), name='product-categories-list-create-slash'),
    path('product-categories/<int:pk>', ProductCategoryView.as_view(), name='product-categories-detail'),
    path('product-categories/<int:pk>/', ProductCategoryView.as_view(), name='product-categories-detail-slash'),

    # Services (supports both ID and Slug)
    path('our-services', ServiceView.as_view(), name='services-list-create'),
    path('our-services/', ServiceView.as_view(), name='services-list-create-slash'),
    path('our-services/<int:pk>', ServiceView.as_view(), name='services-detail'),
    path('our-services/<int:pk>/', ServiceView.as_view(), name='services-detail-slash'),
    path('our-services/<slug:slug>', ServiceView.as_view(), name='services-detail-slug'),
    path('our-services/<slug:slug>/', ServiceView.as_view(), name='services-detail-slug-slash'),

    # Products (supports both ID and Slug)
    path('products', ProductView.as_view(), name='products-list-create'),
    path('products/', ProductView.as_view(), name='products-list-create-slash'),
    path('products/<int:pk>', ProductView.as_view(), name='products-detail'),
    path('products/<int:pk>/', ProductView.as_view(), name='products-detail-slash'),
    path('products/<slug:slug>', ProductView.as_view(), name='products-detail-slug'),
    path('products/<slug:slug>/', ProductView.as_view(), name='products-detail-slug-slash'),

    # Testimonials
    path('testimonials', TestimonialView.as_view(), name='testimonials-list-create'),
    path('testimonials/', TestimonialView.as_view(), name='testimonials-list-create-slash'),
    path('testimonials/<int:pk>', TestimonialView.as_view(), name='testimonials-detail'),
    path('testimonials/<int:pk>/', TestimonialView.as_view(), name='testimonials-detail-slash'),

    # Our Team
    path('our-teams', OurTeamView.as_view(), name='our-teams-list-create'),
    path('our-teams/', OurTeamView.as_view(), name='our-teams-list-create-slash'),
    path('our-teams/<int:pk>', OurTeamView.as_view(), name='our-teams-detail'),
    path('our-teams/<int:pk>/', OurTeamView.as_view(), name='our-teams-detail-slash'),

    # Company Info
    path('company-info', CompanyInfoView.as_view(), name='company-info-singleton'),
    path('company-info/', CompanyInfoView.as_view(), name='company-info-singleton-slash'),
    path('company-info/<int:id>', CompanyInfoView.as_view(), name='company-info-detail'),
    path('company-info/<int:id>/', CompanyInfoView.as_view(), name='company-info-detail-slash'),

    # Social URLs
    path('social-urls', SocialUrlView.as_view(), name='social-urls-list-create'),
    path('social-urls/', SocialUrlView.as_view(), name='social-urls-list-create-slash'),
    path('social-urls/<int:pk>', SocialUrlView.as_view(), name='social-urls-detail'),
    path('social-urls/<int:pk>/', SocialUrlView.as_view(), name='social-urls-detail-slash'),

    # FAQs
    path('faqs', FaqView.as_view(), name='faqs-list-create'),
    path('faqs/', FaqView.as_view(), name='faqs-list-create-slash'),
    path('faqs/<int:pk>', FaqView.as_view(), name='faqs-detail'),
    path('faqs/<int:pk>/', FaqView.as_view(), name='faqs-detail-slash'),

    # Core Values
    path('core-values', CoreValueView.as_view(), name='core-values-list-create'),
    path('core-values/', CoreValueView.as_view(), name='core-values-list-create-slash'),
    path('core-values/<int:pk>', CoreValueView.as_view(), name='core-values-detail'),
    path('core-values/<int:pk>/', CoreValueView.as_view(), name='core-values-detail-slash'),

    # Events (supports both ID and Slug)
    path('events', EventView.as_view(), name='events-list-create'),
    path('events/', EventView.as_view(), name='events-list-create-slash'),
    path('events/<int:pk>', EventView.as_view(), name='events-detail'),
    path('events/<int:pk>/', EventView.as_view(), name='events-detail-slash'),
    path('events/<slug:slug>', EventView.as_view(), name='events-detail-slug'),
    path('events/<slug:slug>/', EventView.as_view(), name='events-detail-slug-slash'),

    # Hero Section
    path('hero-section', HeroSectionView.as_view(), name='hero-section-list-create'),
    path('hero-section/', HeroSectionView.as_view(), name='hero-section-list-create-slash'),
    path('hero-section/<int:pk>', HeroSectionView.as_view(), name='hero-section-detail'),
    path('hero-section/<int:pk>/', HeroSectionView.as_view(), name='hero-section-detail-slash'),

    # Stats
    path('stat', StatView.as_view(), name='stat-list-create'),
    path('stat/', StatView.as_view(), name='stat-list-create-slash'),
    path('stat/<int:pk>', StatView.as_view(), name='stat-detail'),
    path('stat/<int:pk>/', StatView.as_view(), name='stat-detail-slash'),

    # Photo Gallery
    path('photo-gallery', PhotoGalleryView.as_view(), name='photo-gallery-list-create'),
    path('photo-gallery/', PhotoGalleryView.as_view(), name='photo-gallery-list-create-slash'),
    path('photo-gallery/<int:pk>', PhotoGalleryView.as_view(), name='photo-gallery-detail'),
    path('photo-gallery/<int:pk>/', PhotoGalleryView.as_view(), name='photo-gallery-detail-slash'),
]
