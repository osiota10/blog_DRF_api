from rest_framework import serializers
from .models import *
from media_library.models import MediaAsset
from media_library.serializers import MediaAssetSerializer


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = '__all__'


class EmailSubcriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSubcription
        fields = '__all__'


class OurClientSerializer(serializers.ModelSerializer):
    logo_media = MediaAssetSerializer(read_only=True)
    logo_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='logo_media'
    )

    class Meta:
        model = OurClient
        fields = ('id', 'name_of_client', 'logo_media', 'logo_media_id', 'logo_url', 'logo', 'get_logo_url')


class OurSponsorSerializer(serializers.ModelSerializer):
    logo_media = MediaAssetSerializer(read_only=True)
    logo_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='logo_media'
    )

    class Meta:
        model = OurSponsor
        fields = ('id', 'name_of_sponsor', 'logo_media', 'logo_media_id', 'logo_url', 'logo', 'get_logo_url')


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
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
    category = ServiceCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(), many=True, write_only=True, required=False, source='category'
    )
    image_media = MediaAssetSerializer(read_only=True)
    image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='image_media'
    )
    faqs = FaqSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = (
            'id', 'title', 'description', 'image_media', 'image_media_id', 'image_url', 'image',
            'slug', 'category', 'category_ids', 'get_image_url', 'faqs', 'safe_description_html'
        )


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), many=True, write_only=True, required=False, source='category'
    )
    image_media = MediaAssetSerializer(read_only=True)
    image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='image_media'
    )
    hero_image_media = MediaAssetSerializer(read_only=True)
    hero_image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='hero_image_media'
    )

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'image_media', 'image_media_id', 'image_url', 'image',
            'hero_image_media', 'hero_image_media_id', 'hero_image_url', 'hero_image', 'hero_snippet',
            'category', 'category_ids', 'slug', 'get_image_url', 'get_hero_image_url', 'safe_description_html'
        )


class TestimonialSerializer(serializers.ModelSerializer):
    image_media = MediaAssetSerializer(read_only=True)
    image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='image_media'
    )

    class Meta:
        model = Testimonial
        fields = ('id', 'name', 'position', 'message', 'image_media', 'image_media_id', 'image_url', 'image', 'get_image_url')


class SocialUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialUrl
        fields = '__all__'


class OurTeamSerializer(serializers.ModelSerializer):
    image_media = MediaAssetSerializer(read_only=True)
    image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='image_media'
    )

    class Meta:
        model = OurTeam
        fields = ('id', 'name', 'position', 'image_media', 'image_media_id', 'image_url', 'image', 'get_image_url')


class CompanyInfoSerializer(serializers.ModelSerializer):
    company_social = SocialUrlSerializer(read_only=True)
    company_faqs = FaqSerializer(many=True, read_only=True)
    logo_media = MediaAssetSerializer(read_only=True)
    logo_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='logo_media'
    )
    about_company_media = MediaAssetSerializer(read_only=True)
    about_company_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='about_company_media'
    )
    ceo_media = MediaAssetSerializer(read_only=True)
    ceo_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='ceo_media'
    )

    class Meta:
        model = CompanyInfo
        fields = (
            'id', 'company_name', 'company_address', 'telephone', 'telephone_2',
            'email', 'about_company', 'return_policy', 'term_and_conditions',
            'privacy_policy', 'company_social', 'company_faqs', 'get_page_header_image',
            'logo_media', 'logo_media_id', 'logo_url', 'logo', 'get_logo',
            'about_company_media', 'about_company_media_id', 'about_company_img_url', 'about_company_img', 'get_about_img',
            'ceo_statment', 'ceo_media', 'ceo_media_id', 'ceo_img_url', 'ceo_img', 'get_ceo_img'
        )


class CoreValueSerializer(serializers.ModelSerializer):
    pic_media = MediaAssetSerializer(read_only=True)
    pic_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='pic_media'
    )

    class Meta:
        model = CoreValue
        fields = ('id', 'title', 'description', 'pic_media', 'pic_media_id', 'pic_url', 'pic')


class EventSerializer(serializers.ModelSerializer):
    image_media = MediaAssetSerializer(read_only=True)
    image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='image_media'
    )

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'body', 'safe_body_html', 'image_media', 'image_media_id', 'image_url', 'image',
            'get_image_url', 'event_date', 'date_added', 'slug'
        )


class HeroSectionSerializer(serializers.ModelSerializer):
    image_media = MediaAssetSerializer(read_only=True)
    image_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='image_media'
    )

    class Meta:
        model = HeroSection
        fields = ('id', 'title', 'description', 'image_media', 'image_media_id', 'image_url', 'image', 'get_image_url')


class YouTubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeVideo
        fields = '__all__'


class PhotoGallerySerializer(serializers.ModelSerializer):
    photo_media = MediaAssetSerializer(read_only=True)
    photo_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), write_only=True, required=False, allow_null=True, source='photo_media'
    )

    class Meta:
        model = PhotoGallery
        fields = ('id', 'title', 'photo_media', 'photo_media_id', 'photo_url', 'photo', 'get_photo_url', 'created_at')
