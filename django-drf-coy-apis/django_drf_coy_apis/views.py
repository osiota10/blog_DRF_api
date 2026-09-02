from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from .models import (
    CompanyInfo, ServiceCategory, Service, ProductCategory, Product,
    ContactForm, EmailSubcription, OurClient, OurSponsor, Stat,
    Testimonial, OurTeam, SocialUrl, FAQ, CoreValue, HeroSection,
    Event
)
from media_library.models import MediaAsset
from .serializer import (
    CompanyInfoSerializer, ServiceCategorySerializer, ServiceSerializer,
    ProductCategorySerializer, ProductSerializer, ContactFormSerializer,
    EmailSubcriptionSerializer, OurClientSerializer, OurSponsorSerializer,
    StatSerializer, TestimonialSerializer, OurTeamSerializer,
    SocialUrlSerializer, FaqSerializer, CoreValueSerializer,
    HeroSectionSerializer, EventSerializer
)


def get_media_asset(media_input):
    """Safely extracts and resolves a MediaAsset instance from int, str, dict, or None."""
    if isinstance(media_input, dict):
        media_input = media_input.get('id') or media_input.get('pk')
    if media_input is None or str(media_input).lower() in ('null', '', 'none'):
        return None
    try:
        return MediaAsset.objects.get(id=int(media_input))
    except (MediaAsset.DoesNotExist, ValueError, TypeError):
        return None


# ============================================================================
# 1. ContactFormView
# ============================================================================
class ContactFormView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return ContactForm.objects.get(pk=target_id)
            except (ContactForm.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'ContactForm not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ContactFormSerializer(obj).data, status=status.HTTP_200_OK)

        records = ContactForm.objects.all().order_by('-id')
        return Response(ContactFormSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')

        if not full_name or not email or not message:
            return Response({'error': 'Full name, email, and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = ContactForm.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number or "",
            message=message
        )
        return Response(ContactFormSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'ContactForm not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'full_name' in request.data:
            obj.full_name = request.data.get('full_name')
        if 'email' in request.data:
            obj.email = request.data.get('email')
        if 'phone_number' in request.data:
            obj.phone_number = request.data.get('phone_number')
        if 'message' in request.data:
            obj.message = request.data.get('message')

        obj.save()
        return Response(ContactFormSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'ContactForm not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 2. EmailSubcriptionView
# ============================================================================
class EmailSubcriptionView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return EmailSubcription.objects.get(pk=target_id)
            except (EmailSubcription.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'EmailSubcription not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(EmailSubcriptionSerializer(obj).data, status=status.HTTP_200_OK)

        records = EmailSubcription.objects.all().order_by('-id')
        return Response(EmailSubcriptionSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = EmailSubcription.objects.create(email=email)
        return Response(EmailSubcriptionSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'EmailSubcription not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'email' in request.data:
            obj.email = request.data.get('email')

        obj.save()
        return Response(EmailSubcriptionSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'EmailSubcription not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 3. OurClientView
# ============================================================================
class OurClientView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return OurClient.objects.get(pk=target_id)
            except (OurClient.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'OurClient not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(OurClientSerializer(obj).data, status=status.HTTP_200_OK)

        records = OurClient.objects.all().order_by('-id')
        return Response(OurClientSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        name_of_client = request.data.get('name_of_client')
        logo_url = request.data.get('logo_url')
        media_input = request.data.get('logo_media_id') or request.data.get('logo_media')
        logo_media = get_media_asset(media_input)

        if not name_of_client:
            return Response({'error': 'Client name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = OurClient.objects.create(
            name_of_client=name_of_client,
            logo_media=logo_media,
            logo_url=logo_url
        )
        return Response(OurClientSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'OurClient not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'name_of_client' in request.data:
            obj.name_of_client = request.data.get('name_of_client')
        if 'logo_url' in request.data:
            obj.logo_url = request.data.get('logo_url')

        if 'logo_media' in request.data or 'logo_media_id' in request.data:
            media_input = request.data.get('logo_media_id') or request.data.get('logo_media')
            obj.logo_media = get_media_asset(media_input)

        obj.save()
        return Response(OurClientSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'OurClient not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 4. OurSponsorView
# ============================================================================
class OurSponsorView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return OurSponsor.objects.get(pk=target_id)
            except (OurSponsor.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'OurSponsor not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(OurSponsorSerializer(obj).data, status=status.HTTP_200_OK)

        records = OurSponsor.objects.all().order_by('-id')
        return Response(OurSponsorSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        name_of_sponsor = request.data.get('name_of_sponsor')
        logo_url = request.data.get('logo_url')
        media_input = request.data.get('logo_media_id') or request.data.get('logo_media')
        logo_media = get_media_asset(media_input)

        if not name_of_sponsor:
            return Response({'error': 'Sponsor name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = OurSponsor.objects.create(
            name_of_sponsor=name_of_sponsor,
            logo_media=logo_media,
            logo_url=logo_url
        )
        return Response(OurSponsorSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'OurSponsor not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'name_of_sponsor' in request.data:
            obj.name_of_sponsor = request.data.get('name_of_sponsor')
        if 'logo_url' in request.data:
            obj.logo_url = request.data.get('logo_url')

        if 'logo_media' in request.data or 'logo_media_id' in request.data:
            media_input = request.data.get('logo_media_id') or request.data.get('logo_media')
            obj.logo_media = get_media_asset(media_input)

        obj.save()
        return Response(OurSponsorSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'OurSponsor not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 5. ServiceCategoryView
# ============================================================================
class ServiceCategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return ServiceCategory.objects.get(pk=target_id)
            except (ServiceCategory.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'ServiceCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ServiceCategorySerializer(obj).data, status=status.HTTP_200_OK)

        records = ServiceCategory.objects.all().order_by('-id')
        return Response(ServiceCategorySerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = ServiceCategory.objects.create(name=name)
        return Response(ServiceCategorySerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'ServiceCategory not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'name' in request.data:
            obj.name = request.data.get('name')

        obj.save()
        return Response(ServiceCategorySerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'ServiceCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 6. ProductCategoryView
# ============================================================================
class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return ProductCategory.objects.get(pk=target_id)
            except (ProductCategory.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'ProductCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ProductCategorySerializer(obj).data, status=status.HTTP_200_OK)

        records = ProductCategory.objects.all().order_by('-id')
        return Response(ProductCategorySerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = ProductCategory.objects.create(name=name)
        return Response(ProductCategorySerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'ProductCategory not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'name' in request.data:
            obj.name = request.data.get('name')

        obj.save()
        return Response(ProductCategorySerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'ProductCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 7. ServiceView (Reference Implementation Blueprint)
# ============================================================================
class ServiceView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        """Resolves target instance from URL parameter, query string, or payload ID."""
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        target_slug = slug or (request.query_params.get('slug') if request else None)

        if target_id:
            try:
                return Service.objects.get(pk=target_id)
            except (Service.DoesNotExist, ValueError):
                return None

        if target_slug:
            try:
                return Service.objects.get(slug=target_slug)
            except Service.DoesNotExist:
                return None

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or slug or request.query_params.get('id') or request.query_params.get('slug'):
            service = self.get_object(pk=pk, slug=slug, request=request)
            if not service:
                return Response({'error': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ServiceSerializer(service).data, status=status.HTTP_200_OK)

        services = Service.objects.all().order_by('-id')
        return Response(ServiceSerializer(services, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        image_url = request.data.get('image_url')
        slug = request.data.get('slug') or slugify(title or "")

        if not title or not description:
            return Response(
                {'error': 'Title and description are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        media_input = request.data.get('image_media_id') or request.data.get('image_media')
        image_media = get_media_asset(media_input)

        service = Service.objects.create(
            title=title,
            description=description,
            image_media=image_media,
            image_url=image_url,
            slug=slug
        )

        categories = request.data.get('category_ids') or request.data.get('category')
        if categories:
            if not isinstance(categories, list):
                categories = [categories]
            service.category.set(categories)

        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        service = self.get_object(pk=pk, slug=slug, request=request)
        if not service:
            return Response({'error': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'title' in request.data:
            service.title = request.data.get('title')
        if 'description' in request.data:
            service.description = request.data.get('description')
        if 'image_url' in request.data:
            service.image_url = request.data.get('image_url')
        if 'slug' in request.data:
            service.slug = slugify(request.data.get('slug'))

        if 'image_media' in request.data or 'image_media_id' in request.data:
            media_input = request.data.get('image_media_id') or request.data.get('image_media')
            service.image_media = get_media_asset(media_input)

        service.save()

        if 'category_ids' in request.data or 'category' in request.data:
            categories = request.data.get('category_ids') or request.data.get('category')
            if isinstance(categories, list):
                service.category.set(categories)

        return Response(ServiceSerializer(service).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        service = self.get_object(pk=pk, slug=slug, request=request)
        if not service:
            return Response({'error': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 8. ProductView
# ============================================================================
class ProductView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        target_slug = slug or (request.query_params.get('slug') if request else None)

        if target_id:
            try:
                return Product.objects.get(pk=target_id)
            except (Product.DoesNotExist, ValueError):
                return None

        if target_slug:
            try:
                return Product.objects.get(slug=target_slug)
            except Product.DoesNotExist:
                return None

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or slug or request.query_params.get('id') or request.query_params.get('slug'):
            product = self.get_object(pk=pk, slug=slug, request=request)
            if not product:
                return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

        products = Product.objects.all().order_by('-id')
        return Response(ProductSerializer(products, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        image_url = request.data.get('image_url')
        hero_image_url = request.data.get('hero_image_url')
        hero_snippet = request.data.get('hero_snippet')
        slug = request.data.get('slug') or slugify(title or "")

        if not title or not description:
            return Response(
                {'error': 'Title and description are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        media_input = request.data.get('image_media_id') or request.data.get('image_media')
        image_media = get_media_asset(media_input)

        hero_media_input = request.data.get('hero_image_media_id') or request.data.get('hero_image_media')
        hero_image_media = get_media_asset(hero_media_input)

        product = Product.objects.create(
            title=title,
            description=description,
            image_media=image_media,
            image_url=image_url,
            hero_image_media=hero_image_media,
            hero_image_url=hero_image_url,
            hero_snippet=hero_snippet,
            slug=slug
        )

        categories = request.data.get('category_ids') or request.data.get('category')
        if categories:
            if not isinstance(categories, list):
                categories = [categories]
            product.category.set(categories)

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        product = self.get_object(pk=pk, slug=slug, request=request)
        if not product:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'title' in request.data:
            product.title = request.data.get('title')
        if 'description' in request.data:
            product.description = request.data.get('description')
        if 'image_url' in request.data:
            product.image_url = request.data.get('image_url')
        if 'hero_image_url' in request.data:
            product.hero_image_url = request.data.get('hero_image_url')
        if 'hero_snippet' in request.data:
            product.hero_snippet = request.data.get('hero_snippet')
        if 'slug' in request.data:
            product.slug = slugify(request.data.get('slug'))

        if 'image_media' in request.data or 'image_media_id' in request.data:
            media_input = request.data.get('image_media_id') or request.data.get('image_media')
            product.image_media = get_media_asset(media_input)

        if 'hero_image_media' in request.data or 'hero_image_media_id' in request.data:
            hero_media_input = request.data.get('hero_image_media_id') or request.data.get('hero_image_media')
            product.hero_image_media = get_media_asset(hero_media_input)

        product.save()

        if 'category_ids' in request.data or 'category' in request.data:
            categories = request.data.get('category_ids') or request.data.get('category')
            if isinstance(categories, list):
                product.category.set(categories)

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        product = self.get_object(pk=pk, slug=slug, request=request)
        if not product:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 9. TestimonialView
# ============================================================================
class TestimonialView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return Testimonial.objects.get(pk=target_id)
            except (Testimonial.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(TestimonialSerializer(obj).data, status=status.HTTP_200_OK)

        records = Testimonial.objects.all().order_by('-id')
        return Response(TestimonialSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        position = request.data.get('position')
        message = request.data.get('message')
        image_url = request.data.get('image_url')
        media_input = request.data.get('image_media_id') or request.data.get('image_media')
        image_media = get_media_asset(media_input)

        if not name or not message:
            return Response({'error': 'Name and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = Testimonial.objects.create(
            name=name,
            position=position or "",
            message=message,
            image_media=image_media,
            image_url=image_url
        )
        return Response(TestimonialSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'name' in request.data:
            obj.name = request.data.get('name')
        if 'position' in request.data:
            obj.position = request.data.get('position')
        if 'message' in request.data:
            obj.message = request.data.get('message')
        if 'image_url' in request.data:
            obj.image_url = request.data.get('image_url')

        if 'image_media' in request.data or 'image_media_id' in request.data:
            media_input = request.data.get('image_media_id') or request.data.get('image_media')
            obj.image_media = get_media_asset(media_input)

        obj.save()
        return Response(TestimonialSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 10. OurTeamView
# ============================================================================
class OurTeamView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return OurTeam.objects.get(pk=target_id)
            except (OurTeam.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'OurTeam member not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(OurTeamSerializer(obj).data, status=status.HTTP_200_OK)

        records = OurTeam.objects.all().order_by('-id')
        return Response(OurTeamSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_input = request.data.get('user_id') or request.data.get('user')
        user = None
        if user_input:
            User = get_user_model()
            user_id = user_input.get('id') if isinstance(user_input, dict) else user_input
            try:
                user = User.objects.get(pk=user_id)
            except (User.DoesNotExist, ValueError):
                user = None

        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        position = request.data.get('position')
        bio = request.data.get('bio')
        facebook_url = request.data.get('facebook_url')
        instagram_url = request.data.get('instagram_url')
        twitter_url = request.data.get('twitter_url')
        linkedin_url = request.data.get('linkedin_url')
        github_url = request.data.get('github_url')

        media_input = request.data.get('image_media_id') or request.data.get('image_media')
        image_media = get_media_asset(media_input)

        if not position:
            return Response({'error': 'Position is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user and not name:
            return Response({'error': 'Either User or Name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = OurTeam.objects.create(
            user=user,
            name=name,
            phone_number=phone_number,
            position=position,
            bio=bio,
            image_media=image_media,
            facebook_url=facebook_url,
            instagram_url=instagram_url,
            twitter_url=twitter_url,
            linkedin_url=linkedin_url,
            github_url=github_url
        )
        return Response(OurTeamSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'OurTeam member not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'user_id' in request.data or 'user' in request.data:
            user_input = request.data.get('user_id') or request.data.get('user')
            if user_input is None or user_input == '' or user_input == 'null':
                obj.user = None
            else:
                User = get_user_model()
                user_id = user_input.get('id') if isinstance(user_input, dict) else user_input
                try:
                    obj.user = User.objects.get(pk=user_id)
                except (User.DoesNotExist, ValueError):
                    pass

        if 'name' in request.data:
            obj.name = request.data.get('name')
        if 'phone_number' in request.data:
            obj.phone_number = request.data.get('phone_number')
        if 'position' in request.data:
            obj.position = request.data.get('position')
        if 'bio' in request.data:
            obj.bio = request.data.get('bio')
        if 'facebook_url' in request.data:
            obj.facebook_url = request.data.get('facebook_url')
        if 'instagram_url' in request.data:
            obj.instagram_url = request.data.get('instagram_url')
        if 'twitter_url' in request.data:
            obj.twitter_url = request.data.get('twitter_url')
        if 'linkedin_url' in request.data:
            obj.linkedin_url = request.data.get('linkedin_url')
        if 'github_url' in request.data:
            obj.github_url = request.data.get('github_url')

        if 'image_media' in request.data or 'image_media_id' in request.data:
            media_input = request.data.get('image_media_id') or request.data.get('image_media')
            obj.image_media = get_media_asset(media_input)

        obj.save()
        return Response(OurTeamSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'OurTeam member not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 11. CompanyInfoView (Singleton)
# ============================================================================
class CompanyInfoView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        return CompanyInfo.load()

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        coy = CompanyInfo.load()
        return Response(CompanyInfoSerializer(coy).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        coy = CompanyInfo.load()
        
        fields = [
            'company_name', 'company_address', 'telephone', 'telephone_2', 'telephone_3',
            'email', 'email_2', 'email_3', 'about_company', 'return_policy',
            'term_and_conditions', 'privacy_policy', 'ceo_statment'
        ]
        for field in fields:
            if field in request.data:
                setattr(coy, field, request.data.get(field))

        if 'logo_media' in request.data or 'logo_media_id' in request.data:
            media_input = request.data.get('logo_media_id') or request.data.get('logo_media')
            coy.logo_media = get_media_asset(media_input)

        if 'site_page_header_image_media' in request.data or 'site_page_header_image_media_id' in request.data:
            media_input = request.data.get('site_page_header_image_media_id') or request.data.get('site_page_header_image_media')
            coy.site_page_header_image_media = get_media_asset(media_input)

        coy.save()
        return Response(CompanyInfoSerializer(coy).data, status=status.HTTP_200_OK)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        return Response({'error': 'CompanyInfo deletion is prevented.'}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# 12. SocialUrlView
# ============================================================================
class SocialUrlView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return SocialUrl.objects.get(pk=target_id)
            except (SocialUrl.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'SocialUrl not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(SocialUrlSerializer(obj).data, status=status.HTTP_200_OK)

        records = SocialUrl.objects.all().order_by('-id')
        return Response(SocialUrlSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        company_input = data.get('company_id') or data.get('company')
        company = None
        if company_input:
            try:
                company = CompanyInfo.objects.get(id=int(company_input))
            except (CompanyInfo.DoesNotExist, ValueError, TypeError):
                company = CompanyInfo.load()
        else:
            company = CompanyInfo.load()

        fields = ['facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'github_url', 'youtube_url', 'whatsapp_url']
        obj_kwargs = {'company': company}
        for f in fields:
            obj_kwargs[f] = data.get(f)

        obj = SocialUrl.objects.create(**obj_kwargs)
        return Response(SocialUrlSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'SocialUrl not found.'}, status=status.HTTP_404_NOT_FOUND)

        fields = ['facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'github_url', 'youtube_url', 'whatsapp_url']
        for f in fields:
            if f in request.data:
                setattr(obj, f, request.data.get(f))

        obj.save()
        return Response(SocialUrlSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'SocialUrl not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 13. FaqView
# ============================================================================
class FaqView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return FAQ.objects.get(pk=target_id)
            except (FAQ.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'FAQ not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(FaqSerializer(obj).data, status=status.HTTP_200_OK)

        records = FAQ.objects.all().order_by('-id')
        return Response(FaqSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        faq_question = request.data.get('faq_question')
        faq_answer = request.data.get('faq_answer')
        service_input = request.data.get('service_id') or request.data.get('service')
        company_input = request.data.get('company_id') or request.data.get('company')

        if not faq_question or not faq_answer:
            return Response({'error': 'Question and answer are required.'}, status=status.HTTP_400_BAD_REQUEST)

        service = None
        if service_input:
            try:
                service = Service.objects.get(id=int(service_input))
            except (Service.DoesNotExist, ValueError, TypeError):
                pass

        company = None
        if company_input:
            try:
                company = CompanyInfo.objects.get(id=int(company_input))
            except (CompanyInfo.DoesNotExist, ValueError, TypeError):
                pass

        obj = FAQ.objects.create(
            faq_question=faq_question,
            faq_answer=faq_answer,
            service=service,
            company=company
        )
        return Response(FaqSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'FAQ not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'faq_question' in request.data:
            obj.faq_question = request.data.get('faq_question')
        if 'faq_answer' in request.data:
            obj.faq_answer = request.data.get('faq_answer')

        if 'service' in request.data or 'service_id' in request.data:
            svc_input = request.data.get('service_id') or request.data.get('service')
            if svc_input is None or str(svc_input).lower() in ('null', '', 'none'):
                obj.service = None
            else:
                try:
                    obj.service = Service.objects.get(id=int(svc_input))
                except (Service.DoesNotExist, ValueError, TypeError):
                    pass

        if 'company' in request.data or 'company_id' in request.data:
            coy_input = request.data.get('company_id') or request.data.get('company')
            if coy_input is None or str(coy_input).lower() in ('null', '', 'none'):
                obj.company = None
            else:
                try:
                    obj.company = CompanyInfo.objects.get(id=int(coy_input))
                except (CompanyInfo.DoesNotExist, ValueError, TypeError):
                    pass

        obj.save()
        return Response(FaqSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'FAQ not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 14. CoreValueView
# ============================================================================
class CoreValueView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return CoreValue.objects.get(pk=target_id)
            except (CoreValue.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'CoreValue not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(CoreValueSerializer(obj).data, status=status.HTTP_200_OK)

        records = CoreValue.objects.all().order_by('-id')
        return Response(CoreValueSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        pic_url = request.data.get('pic_url')
        media_input = request.data.get('pic_media_id') or request.data.get('pic_media')
        pic_media = get_media_asset(media_input)

        if not title or not description:
            return Response({'error': 'Title and description are required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = CoreValue.objects.create(
            title=title,
            description=description,
            pic_media=pic_media,
            pic_url=pic_url or 'https://img.freepik.com/premium-photo/compass-with-arrow-marks-word-mission_207634-2241.jpg?size=626&ext=jpg&ga=GA1.1.1699289041.1668069491&semt=ais'
        )
        return Response(CoreValueSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'CoreValue not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'title' in request.data:
            obj.title = request.data.get('title')
        if 'description' in request.data:
            obj.description = request.data.get('description')
        if 'pic_url' in request.data:
            obj.pic_url = request.data.get('pic_url')

        if 'pic_media' in request.data or 'pic_media_id' in request.data:
            media_input = request.data.get('pic_media_id') or request.data.get('pic_media')
            obj.pic_media = get_media_asset(media_input)

        obj.save()
        return Response(CoreValueSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'CoreValue not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 15. EventView
# ============================================================================
class EventView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        target_slug = slug or (request.query_params.get('slug') if request else None)

        if target_id:
            try:
                return Event.objects.get(pk=target_id)
            except (Event.DoesNotExist, ValueError):
                return None

        if target_slug:
            try:
                return Event.objects.get(slug=target_slug)
            except Event.DoesNotExist:
                return None

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or slug or request.query_params.get('id') or request.query_params.get('slug'):
            event = self.get_object(pk=pk, slug=slug, request=request)
            if not event:
                return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(EventSerializer(event).data, status=status.HTTP_200_OK)

        events = Event.objects.all().order_by('-id')
        return Response(EventSerializer(events, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        body = request.data.get('body')
        event_date = request.data.get('event_date')
        image_url = request.data.get('image_url')
        slug = request.data.get('slug') or slugify(title or "")

        if not title or not body or not event_date:
            return Response(
                {'error': 'Title, body, and event_date are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        media_input = request.data.get('image_media_id') or request.data.get('image_media')
        image_media = get_media_asset(media_input)

        event = Event.objects.create(
            title=title,
            body=body,
            event_date=event_date,
            image_media=image_media,
            image_url=image_url,
            slug=slug
        )

        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        event = self.get_object(pk=pk, slug=slug, request=request)
        if not event:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'title' in request.data:
            event.title = request.data.get('title')
        if 'body' in request.data:
            event.body = request.data.get('body')
        if 'event_date' in request.data:
            event.event_date = request.data.get('event_date')
        if 'image_url' in request.data:
            event.image_url = request.data.get('image_url')
        if 'slug' in request.data:
            event.slug = slugify(request.data.get('slug'))

        if 'image_media' in request.data or 'image_media_id' in request.data:
            media_input = request.data.get('image_media_id') or request.data.get('image_media')
            event.image_media = get_media_asset(media_input)

        event.save()

        return Response(EventSerializer(event).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        event = self.get_object(pk=pk, slug=slug, request=request)
        if not event:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 16. HeroSectionView
# ============================================================================
class HeroSectionView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return HeroSection.objects.get(pk=target_id)
            except (HeroSection.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'HeroSection not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(HeroSectionSerializer(obj).data, status=status.HTTP_200_OK)

        records = HeroSection.objects.all().order_by('-id')
        return Response(HeroSectionSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        image_url = request.data.get('image_url')
        media_input = request.data.get('image_media_id') or request.data.get('image_media')
        image_media = get_media_asset(media_input)

        if not title or not description:
            return Response({'error': 'Title and description are required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = HeroSection.objects.create(
            title=title,
            description=description,
            image_media=image_media,
            image_url=image_url
        )
        return Response(HeroSectionSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'HeroSection not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'title' in request.data:
            obj.title = request.data.get('title')
        if 'description' in request.data:
            obj.description = request.data.get('description')
        if 'image_url' in request.data:
            obj.image_url = request.data.get('image_url')

        if 'image_media' in request.data or 'image_media_id' in request.data:
            media_input = request.data.get('image_media_id') or request.data.get('image_media')
            obj.image_media = get_media_asset(media_input)

        obj.save()
        return Response(HeroSectionSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'HeroSection not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 17. StatView
# ============================================================================
class StatView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request=None):
        target_id = pk or (request.data.get('id') if request and hasattr(request, 'data') else None)
        if target_id:
            try:
                return Stat.objects.get(pk=target_id)
            except (Stat.DoesNotExist, ValueError):
                return None
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if pk or request.query_params.get('id'):
            obj = self.get_object(pk=pk, request=request)
            if not obj:
                return Response({'error': 'Stat not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(StatSerializer(obj).data, status=status.HTTP_200_OK)

        records = Stat.objects.all().order_by('-id')
        return Response(StatSerializer(records, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        stat_figure = request.data.get('stat_figure')
        stat_title = request.data.get('stat_title')

        if stat_figure is None or not stat_title:
            return Response({'error': 'stat_figure and stat_title are required.'}, status=status.HTTP_400_BAD_REQUEST)

        obj = Stat.objects.create(
            stat_figure=int(stat_figure),
            stat_title=stat_title
        )
        return Response(StatSerializer(obj).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'Stat not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'stat_figure' in request.data:
            obj.stat_figure = int(request.data.get('stat_figure'))
        if 'stat_title' in request.data:
            obj.stat_title = request.data.get('stat_title')

        obj.save()
        return Response(StatSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.put(request, pk=pk, slug=slug, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request=request)
        if not obj:
            return Response({'error': 'Stat not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)# Backward Compatibility Aliases
ContactFormDetailView = ContactFormView
EmailSubcriptionDetailView = EmailSubcriptionView
OurClientDetailView = OurClientView
OurSponsorDetailView = OurSponsorView
ServiceCategoryDetailView = ServiceCategoryView
ProductCategoryDetailView = ProductCategoryView
ServiceDetail = ServiceView
ProductDetail = ProductView
TestimonialDetail = TestimonialView
OurTeamDetail = OurTeamView
CompanyInfoDetailView = CompanyInfoView
SocialUrlDetailView = SocialUrlView
FAQView = FaqView
FaqDetailView = FaqView
CoeValueView = CoreValueView
CoreValueDetailView = CoreValueView
EventDetail = EventView
HeroSectionDetailView = HeroSectionView
StatDetailView = StatView
