from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class CompanyInfo(models.Model):
    logo_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_company_logos'
    )
    site_page_header_image_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_page_header_images'
    )
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_address = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(
        max_length=15, validators=[RegexValidator(r'^\d{11}$', 'Enter a valid phone number.')], null=True, blank=True
    )
    telephone_2 = models.CharField(
        max_length=15, null=True, blank=True, validators=[RegexValidator(r'^\d{11}$', 'Enter a valid phone number.')]
    )
    telephone_3 = models.CharField(
        max_length=15, null=True, blank=True, validators=[RegexValidator(r'^\d{11}$', 'Enter a valid phone number.')]
    )
    email = models.EmailField(null=True, blank=True)
    email_2 = models.EmailField(null=True, blank=True)
    email_3 = models.EmailField(null=True, blank=True)
    about_company = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    return_policy = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    term_and_conditions = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    privacy_policy = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    ceo_statment = CKEditor5Field('Text', config_name='extends', null=True, blank=True)

    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

    def save(self, *args, **kwargs):
        # Always force primary key to 1 so updates overwrite rather than create new rows
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion of the single company info instance
        pass

    @classmethod
    def load(cls):
        """Helper to fetch the single instance anywhere in views/serializers"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def logo(self):
        return self.logo_media.url if self.logo_media else ""

    @property
    def site_page_header_image(self):
        return self.site_page_header_image_media.url if self.site_page_header_image_media else ""

    def get_logo(self):
        return self.logo

    def get_page_header_image(self):
        return self.site_page_header_image

    def __str__(self):
        return self.company_name or "Company Info"


class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Service(models.Model):
    title = models.CharField(max_length=50)
    description = CKEditor5Field('Text', config_name='extends')
    image_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_service_images'
    )
    image_url = models.URLField(null=True, blank=True)
    category = models.ManyToManyField(ServiceCategory, blank=True)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    @property
    def image(self):
        if self.image_media:
            return self.image_media.url
        return self.image_url or ""

    def get_image_url(self):
        return self.image

    def safe_description_html(self):
        return strip_tags(self.description)

    def __str__(self):
        return f"{self.title}"


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    title = models.CharField(max_length=50)
    description = CKEditor5Field('Text', config_name='extends')
    image_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_product_images'
    )
    image_url = models.URLField(null=True, blank=True)
    hero_image_media = models.ForeignKey(
        'media_library.MediaAsset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coy_product_hero_images')
    hero_image_url = models.URLField(null=True, blank=True)
    hero_snippet = models.TextField(blank=True, null=True)
    category = models.ManyToManyField(ProductCategory, blank=True)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    @property
    def image(self):
        if self.image_media:
            return self.image_media.url
        return self.image_url or ""

    @property
    def hero_image(self):
        if self.hero_image_media:
            return self.hero_image_media.url
        return self.hero_image_url or ""

    def get_image_url(self):
        return self.image

    def get_hero_image_url(self):
        return self.hero_image

    def safe_description_html(self):
        return strip_tags(self.description)

    def __str__(self):
        return f"{self.title}"


class ContactForm(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    message = CKEditor5Field('Text', config_name='extends')

    def __str__(self):
        return f"{self.full_name}"

    class Meta:
        verbose_name_plural = "Contact Forms"
        ordering = ['-date']


class EmailSubcription(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name_plural = "Email Subcriptions"
        ordering = ['-date']


class OurClient(models.Model):
    name_of_client = models.CharField(max_length=50)
    logo_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_client_logos'
    )
    logo_url = models.URLField(null=True, blank=True)

    @property
    def logo(self):
        if self.logo_media:
            return self.logo_media.url
        return self.logo_url or ""

    def get_logo_url(self):
        return self.logo

    def __str__(self):
        return f"{self.name_of_client}"


class OurSponsor(models.Model):
    name_of_sponsor = models.CharField(max_length=50)
    logo_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_sponsor_logos'
    )
    logo_url = models.URLField(null=True, blank=True)

    @property
    def logo(self):
        if self.logo_media:
            return self.logo_media.url
        return self.logo_url or ""

    def get_logo_url(self):
        return self.logo

    def __str__(self):
        return f"{self.name_of_sponsor}"


class Stat(models.Model):
    stat_figure = models.IntegerField()
    stat_title = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.stat_title} - {self.stat_figure}"


class Testimonial(models.Model):
    name = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    message = CKEditor5Field('Text', config_name='extends')
    image_media = models.ForeignKey(
        'media_library.MediaAsset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coy_testimonial_images')
    image_url = models.URLField(null=True, blank=True)

    @property
    def image(self):
        if self.image_media:
            return self.image_media.url
        return self.image_url or ""

    def get_image_url(self):
        return self.image

    def __str__(self):
        return f"{self.name} - {self.position}"


class OurTeam(models.Model):
    name = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    image_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_team_images'
    )
    image_url = models.URLField(null=True, blank=True)

    @property
    def image(self):
        if self.image_media:
            return self.image_media.url
        return self.image_url or ""

    def get_image_url(self):
        return self.image

    def __str__(self):
        return f"{self.name} - {self.position}"


class SocialUrl(models.Model):
    company = models.OneToOneField(
        CompanyInfo, related_name='company_social', on_delete=models.CASCADE, blank=True, null=True
    )
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    whatsapp_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.company} Social URLs"


class FAQ(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="faqs", blank=True, null=True
    )
    company = models.ForeignKey(
        CompanyInfo, related_name='company_faqs', on_delete=models.CASCADE, blank=True, null=True
    )
    faq_question = models.CharField(max_length=50)
    faq_answer = CKEditor5Field('Text', config_name='extends')

    def __str__(self):
        return f"{self.service or self.company} - {self.faq_question}"

    def clean(self):
        if self.service and self.company:
            raise ValidationError("Only one of service and company can be selected.")


class CoreValue(models.Model):
    pic_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_core_value_pics'
    )
    pic_url = models.URLField(
        default='https://img.freepik.com/premium-photo/compass-with-arrow-marks-word-mission_207634-2241.jpg?size=626&ext=jpg&ga=GA1.1.1699289041.1668069491&semt=ais',
        blank=True,
        null=True)
    title = models.CharField(max_length=50)
    description = CKEditor5Field('Text', config_name='extends')

    @property
    def pic(self):
        if self.pic_media:
            return self.pic_media.url
        return self.pic_url or ""

    def __str__(self):
        return f"{self.title}"


class HeroSection(models.Model):
    title = models.CharField(max_length=50)
    description = CKEditor5Field('Text', config_name='extends')
    image_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_hero_images'
    )
    image_url = models.URLField(null=True, blank=True)

    @property
    def image(self):
        if self.image_media:
            return self.image_media.url
        return self.image_url or ""

    def get_image_url(self):
        return self.image

    def __str__(self):
        return f"{self.title}"


class Event(models.Model):
    date_added = models.DateField(auto_now_add=True)
    image_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_event_images'
    )
    image_url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=32)
    body = CKEditor5Field('Text', config_name='extends')
    event_date = models.DateField()
    slug = models.SlugField(max_length=250, blank=True, null=True)

    @property
    def image(self):
        if self.image_media:
            return self.image_media.url
        return self.image_url or ""

    def safe_body_html(self):
        return strip_tags(self.body)

    def get_image_url(self):
        return self.image

    def __str__(self):
        return f"{self.title}"


class YouTubeVideo(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the video")
    description = models.TextField(blank=True, help_text="Optional video description")
    video_url = models.URLField(help_text="URL of the YouTube video")
    embed_code = models.TextField(blank=True, help_text="Optional HTML embed code for the video")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    def get_embed_url(self):
        import re
        pattern = re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*")
        match = pattern.search(self.video_url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'
        return self.video_url


class PhotoGallery(models.Model):
    title = models.CharField(max_length=50)
    photo_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='coy_photo_gallery'
    )
    photo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    @property
    def photo(self):
        if self.photo_media:
            return self.photo_media.url
        return self.photo_url or ""

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['-created_at']

    def get_photo_url(self):
        return self.photo
