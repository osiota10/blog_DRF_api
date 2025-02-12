from django.urls import path
from .views import *

urlpatterns = [
    path('contact-us', ContactFormView.as_view(),),
    path('email-subscription', EmailSubcriptionView.as_view()),
    path('clients', OurClientView.as_view()),
    path('our-services', ServiceView.as_view()),
    path('our-services/<slug:slug>', ServiceDetail.as_view()),
    path('testimonials', TestimonialView.as_view()),
    path('our-teams', OurTeamView.as_view()),
    path('company-info/<int:id>', CompanyInfoView.as_view()),
    path('core-values', CoeValueView.as_view()),
    path('events', EventView.as_view()),
    path('events/<slug:slug>', EventDetail.as_view()),
    path('hero-section', HeroSectionView.as_view()),
]
