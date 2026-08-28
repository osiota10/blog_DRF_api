from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import OperationalError
from .models import *
from .serializer import *


class ContactFormView(generics.ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]


class ContactFormDetailView(generics.RetrieveDestroyAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EmailSubcriptionView(generics.ListCreateAPIView):
    queryset = EmailSubcription.objects.all()
    serializer_class = EmailSubcriptionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]


class EmailSubcriptionDetailView(generics.RetrieveDestroyAPIView):
    queryset = EmailSubcription.objects.all()
    serializer_class = EmailSubcriptionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OurClientView(generics.ListCreateAPIView):
    queryset = OurClient.objects.all()
    serializer_class = OurClientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OurClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OurClient.objects.all()
    serializer_class = OurClientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OurSponsorView(generics.ListCreateAPIView):
    queryset = OurSponsor.objects.all()
    serializer_class = OurSponsorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OurSponsorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OurSponsor.objects.all()
    serializer_class = OurSponsorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServiceCategoryView(generics.ListCreateAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServiceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductCategoryView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServiceView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class TestimonialView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TestimonialDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OurTeamView(generics.ListCreateAPIView):
    queryset = OurTeam.objects.all()
    serializer_class = OurTeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OurTeamDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OurTeam.objects.all()
    serializer_class = OurTeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CompanyInfoView(generics.ListCreateAPIView):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CompanyInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SocialUrlView(generics.ListCreateAPIView):
    queryset = SocialUrl.objects.all()
    serializer_class = SocialUrlSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SocialUrlDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SocialUrl.objects.all()
    serializer_class = SocialUrlSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FaqView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FaqSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FaqDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FaqSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CoeValueView(generics.ListCreateAPIView):
    queryset = CoreValue.objects.all()
    serializer_class = CoreValueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CoreValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoreValue.objects.all()
    serializer_class = CoreValueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EventView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class HeroSectionView(generics.ListCreateAPIView):
    queryset = HeroSection.objects.all()
    serializer_class = HeroSectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class HeroSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HeroSection.objects.all()
    serializer_class = HeroSectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class StatView(generics.ListCreateAPIView):
    queryset = Stat.objects.all()
    serializer_class = StatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class StatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stat.objects.all()
    serializer_class = StatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class YouTubeVideoView(generics.ListCreateAPIView):
    queryset = YouTubeVideo.objects.all()
    serializer_class = YouTubeVideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class YouTubeVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = YouTubeVideo.objects.all()
    serializer_class = YouTubeVideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PhotoGalleryView(generics.ListCreateAPIView):
    queryset = PhotoGallery.objects.all()
    serializer_class = PhotoGallerySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PhotoGalleryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PhotoGallery.objects.all()
    serializer_class = PhotoGallerySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
