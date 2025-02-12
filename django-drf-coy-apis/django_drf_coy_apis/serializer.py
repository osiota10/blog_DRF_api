from rest_framework import serializers
from .models import *


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = '__all__'


class EmailSubcriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSubcription
        fields = '__all__'


class OurClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurClient
        fields = ('id', 'name_of_client', 'get_logo_url')


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = '__all__'


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(many=True)
    faqs = FaqSerializer(many=True)

    class Meta:
        model = Service
        fields = ('id', 'title', 'description', 'image', 'slug', 'category',
                  'get_image_url', 'faqs', 'safe_description_html', 'hero_snippet', 'get_hero_image_url')


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ('id', 'name', 'position', 'message', 'get_image_url')


class SocialUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialUrl
        fields = '__all__'


class OurTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurTeam
        fields = ('id', 'name', 'position', 'get_image_url')


class CompanyInfoSerializer(serializers.ModelSerializer):
    company_social = SocialUrlSerializer()
    company_faqs = FaqSerializer(many=True)

    class Meta:
        model = CompanyInfo
        fields = ('id', 'company_name', 'company_address', 'telephone', 'telephone_2',
                  'email', 'about_company', 'return_policy', 'term_and_conditions',
                  'privacy_policy', 'company_social', 'company_faqs', 'get_page_header_image',
                  'get_logo', 'get_testimonial_frame', 'career_benefits')


class CoreValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoreValue
        fields = ('id', 'title', 'description', 'pic_url')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'safe_body_html',
                  'get_image_url', 'event_date', 'slug')
