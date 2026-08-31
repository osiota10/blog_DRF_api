from django.urls import path
from .views import *

urlpatterns = [
    # Contact Forms
    path('contact-us', ContactFormView.as_view()),
    path('contact-us/', ContactFormView.as_view()),
    path('contact-us/<int:pk>', ContactFormDetailView.as_view()),
    path('contact-us/<int:pk>/', ContactFormDetailView.as_view()),

    # Email Subscription
    path('email-subscription', EmailSubcriptionView.as_view()),
    path('email-subscription/', EmailSubcriptionView.as_view()),
    path('email-subscription/<int:pk>', EmailSubcriptionDetailView.as_view()),
    path('email-subscription/<int:pk>/', EmailSubcriptionDetailView.as_view()),

    # Company Clients
    path('clients', OurClientView.as_view()),
    path('clients/', OurClientView.as_view()),
    path('clients/<int:pk>', OurClientDetailView.as_view()),
    path('clients/<int:pk>/', OurClientDetailView.as_view()),

    # Company Sponsors
    path('sponsors', OurSponsorView.as_view()),
    path('sponsors/', OurSponsorView.as_view()),
    path('sponsors/<int:pk>', OurSponsorDetailView.as_view()),
    path('sponsors/<int:pk>/', OurSponsorDetailView.as_view()),

    # Service Categories
    path('service-categories', ServiceCategoryView.as_view()),
    path('service-categories/', ServiceCategoryView.as_view()),
    path('service-categories/<int:pk>', ServiceCategoryDetailView.as_view()),
    path('service-categories/<int:pk>/', ServiceCategoryDetailView.as_view()),

    # Product Categories
    path('product-categories', ProductCategoryView.as_view()),
    path('product-categories/', ProductCategoryView.as_view()),
    path('product-categories/<int:pk>', ProductCategoryDetailView.as_view()),
    path('product-categories/<int:pk>/', ProductCategoryDetailView.as_view()),

    # Services (supports both ID and Slug)
    path('our-services', ServiceView.as_view()),
    path('our-services/', ServiceView.as_view()),
    path('our-services/<int:pk>', ServiceDetail.as_view()),
    path('our-services/<int:pk>/', ServiceDetail.as_view()),
    path('our-services/<slug:slug>', ServiceDetail.as_view()),
    path('our-services/<slug:slug>/', ServiceDetail.as_view()),

    # Products (supports both ID and Slug)
    path('products', ProductView.as_view()),
    path('products/', ProductView.as_view()),
    path('products/<int:pk>', ProductDetail.as_view()),
    path('products/<int:pk>/', ProductDetail.as_view()),
    path('products/<slug:slug>', ProductDetail.as_view()),
    path('products/<slug:slug>/', ProductDetail.as_view()),

    # Testimonials
    path('testimonials', TestimonialView.as_view()),
    path('testimonials/', TestimonialView.as_view()),
    path('testimonials/<int:pk>', TestimonialDetail.as_view()),
    path('testimonials/<int:pk>/', TestimonialDetail.as_view()),

    # Our Team
    path('our-teams', OurTeamView.as_view()),
    path('our-teams/', OurTeamView.as_view()),
    path('our-teams/<int:pk>', OurTeamDetail.as_view()),
    path('our-teams/<int:pk>/', OurTeamDetail.as_view()),

    # Company Info
    path('company-info', CompanyInfoView.as_view()),
    path('company-info/', CompanyInfoView.as_view()),
    path('company-info/<int:id>', CompanyInfoDetailView.as_view()),
    path('company-info/<int:id>/', CompanyInfoDetailView.as_view()),

    # Social URLs
    path('social-urls', SocialUrlView.as_view()),
    path('social-urls/', SocialUrlView.as_view()),
    path('social-urls/<int:pk>', SocialUrlDetailView.as_view()),
    path('social-urls/<int:pk>/', SocialUrlDetailView.as_view()),

    # FAQs
    path('faqs', FaqView.as_view()),
    path('faqs/', FaqView.as_view()),
    path('faqs/<int:pk>', FaqDetailView.as_view()),
    path('faqs/<int:pk>/', FaqDetailView.as_view()),

    # Core Values
    path('core-values', CoeValueView.as_view()),
    path('core-values/', CoeValueView.as_view()),
    path('core-values/<int:pk>', CoreValueDetailView.as_view()),
    path('core-values/<int:pk>/', CoreValueDetailView.as_view()),

    # Events (supports both ID and Slug)
    path('events', EventView.as_view()),
    path('events/', EventView.as_view()),
    path('events/<int:pk>', EventDetail.as_view()),
    path('events/<int:pk>/', EventDetail.as_view()),
    path('events/<slug:slug>', EventDetail.as_view()),
    path('events/<slug:slug>/', EventDetail.as_view()),

    # Hero Section
    path('hero-section', HeroSectionView.as_view()),
    path('hero-section/', HeroSectionView.as_view()),
    path('hero-section/<int:pk>', HeroSectionDetailView.as_view()),
    path('hero-section/<int:pk>/', HeroSectionDetailView.as_view()),

    # Stats
    path('stat', StatView.as_view()),
    path('stat/', StatView.as_view()),
    path('stat/<int:pk>', StatDetailView.as_view()),
    path('stat/<int:pk>/', StatDetailView.as_view()),

    # YouTube Videos
    path('youtube-videos', YouTubeVideoView.as_view()),
    path('youtube-videos/', YouTubeVideoView.as_view()),
    path('youtube-videos/<int:pk>', YouTubeVideoDetailView.as_view()),
    path('youtube-videos/<int:pk>/', YouTubeVideoDetailView.as_view()),

    # Photo Gallery
    path('photo-gallery', PhotoGalleryView.as_view()),
    path('photo-gallery/', PhotoGalleryView.as_view()),
    path('photo-gallery/<int:pk>', PhotoGalleryDetailView.as_view()),
    path('photo-gallery/<int:pk>/', PhotoGalleryDetailView.as_view()),
]
