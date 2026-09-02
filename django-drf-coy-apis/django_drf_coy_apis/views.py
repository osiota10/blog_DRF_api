from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.utils.text import slugify
from .models import *
from .serializer import *


def resolve_id_or_instance(val):
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get('id') or val.get('pk')
    if val is None or val == "" or str(val).lower() == 'null':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def resolve_id_list(val):
    if not val:
        return []
    if not isinstance(val, (list, tuple, set)):
        val = [val]
    res = []
    for item in val:
        resolved = resolve_id_or_instance(item)
        if resolved is not None:
            res.append(resolved)
    return res


def prepare_payload_data(request_data, model):
    if request_data is None:
        data = {}
    elif hasattr(request_data, 'copy'):
        data = request_data.copy()
    elif isinstance(request_data, dict):
        data = dict(request_data)
    else:
        data = {}

    if not model:
        return data

    # 1. Foreign Key / Media Resolution
    for field in model._meta.get_fields():
        if field.is_relation and field.many_to_one:
            field_name = field.name
            id_field_name = f"{field_name}_id"

            raw_val = None
            if id_field_name in data:
                raw_val = data[id_field_name]
            elif field_name in data:
                raw_val = data[field_name]

            if id_field_name in data or field_name in data:
                if raw_val is None or str(raw_val).lower() == 'null' or raw_val == "":
                    data[id_field_name] = None
                    if field_name in data and field_name != id_field_name:
                        data.pop(field_name, None)
                else:
                    resolved_id = resolve_id_or_instance(raw_val)
                    if resolved_id is not None:
                        data[id_field_name] = resolved_id
                        if field_name in data and field_name != id_field_name:
                            data.pop(field_name, None)

    # 2. ManyToMany Resolution
    for field in model._meta.get_fields():
        if field.is_relation and field.many_to_many:
            field_name = field.name
            ids_field_name = f"{field_name}_ids"

            raw_val = None
            if ids_field_name in data:
                raw_val = data[ids_field_name]
            elif field_name in data:
                raw_val = data[field_name]

            if ids_field_name in data or field_name in data:
                resolved_ids = resolve_id_list(raw_val)
                data[ids_field_name] = resolved_ids
                if field_name in data and field_name != ids_field_name:
                    data.pop(field_name, None)

    # 3. Auto-slug generation
    if hasattr(model, 'slug'):
        title_val = data.get('title') or data.get('name')
        if title_val and not data.get('slug'):
            data['slug'] = slugify(title_val)

    return data


class BaseUnifiedAPIView(APIView):
    model = None
    serializer_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.model:
            return self.model.objects.all()
        return None

    def get_serializer(self, *args, **kwargs):
        if self.serializer_class:
            return self.serializer_class(*args, **kwargs)
        raise NotImplementedError("serializer_class must be defined.")

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk if pk is not None else self.kwargs.get('id') or self.kwargs.get('pk')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')
        if identifier is None and self.request.query_params:
            identifier = self.request.query_params.get('id') or self.request.query_params.get('pk')

        query_slug = slug if slug is not None else self.kwargs.get('slug')
        if query_slug is None and request_data and isinstance(request_data, dict):
            query_slug = request_data.get('slug')
        if query_slug is None and self.request.query_params:
            query_slug = self.request.query_params.get('slug')

        queryset = self.get_queryset()
        if queryset is None:
            return None

        if identifier is not None:
            if str(identifier).isdigit():
                obj = queryset.filter(pk=int(identifier)).first()
                if obj:
                    self.check_object_permissions(self.request, obj)
                    return obj
            if hasattr(self.model, 'slug'):
                obj = queryset.filter(slug=str(identifier)).first()
                if obj:
                    self.check_object_permissions(self.request, obj)
                    return obj

        if query_slug is not None and hasattr(self.model, 'slug'):
            obj = queryset.filter(slug=query_slug).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        if (
            pk is not None
            or slug is not None
            or self.kwargs.get('pk') is not None
            or self.kwargs.get('id') is not None
            or self.kwargs.get('slug') is not None
            or request.query_params.get('id')
            or request.query_params.get('pk')
            or request.query_params.get('slug')
        ):
            obj = self.get_object(pk=pk, slug=slug)
            if not obj:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = prepare_payload_data(request.data, self.model)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=False, *args, **kwargs)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=True, *args, **kwargs)

    def update(self, request, pk=None, slug=None, partial=True, *args, **kwargs):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = prepare_payload_data(request.data, self.model)
        serializer = self.get_serializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContactFormView(BaseUnifiedAPIView):
    model = ContactForm
    serializer_class = ContactFormSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]


class EmailSubcriptionView(BaseUnifiedAPIView):
    model = EmailSubcription
    serializer_class = EmailSubcriptionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]


class OurClientView(BaseUnifiedAPIView):
    model = OurClient
    serializer_class = OurClientSerializer


class OurSponsorView(BaseUnifiedAPIView):
    model = OurSponsor
    serializer_class = OurSponsorSerializer


class ServiceCategoryView(BaseUnifiedAPIView):
    model = ServiceCategory
    serializer_class = ServiceCategorySerializer


class ProductCategoryView(BaseUnifiedAPIView):
    model = ProductCategory
    serializer_class = ProductCategorySerializer


class ServiceView(BaseUnifiedAPIView):
    model = Service
    serializer_class = ServiceSerializer


class ProductView(BaseUnifiedAPIView):
    model = Product
    serializer_class = ProductSerializer


class TestimonialView(BaseUnifiedAPIView):
    model = Testimonial
    serializer_class = TestimonialSerializer


class OurTeamView(BaseUnifiedAPIView):
    model = OurTeam
    serializer_class = OurTeamSerializer


class CompanyInfoView(BaseUnifiedAPIView):
    model = CompanyInfo
    serializer_class = CompanyInfoSerializer

    def get_object(self, pk=None, slug=None, request_data=None):
        obj = CompanyInfo.load()
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        instance = CompanyInfo.load()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        instance = CompanyInfo.load()
        data = prepare_payload_data(request.data, self.model)
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return Response({'detail': 'CompanyInfo deletion is prevented.'}, status=status.HTTP_400_BAD_REQUEST)


class SocialUrlView(BaseUnifiedAPIView):
    model = SocialUrl
    serializer_class = SocialUrlSerializer


class FaqView(BaseUnifiedAPIView):
    model = FAQ
    serializer_class = FaqSerializer


class CoreValueView(BaseUnifiedAPIView):
    model = CoreValue
    serializer_class = CoreValueSerializer


class EventView(BaseUnifiedAPIView):
    model = Event
    serializer_class = EventSerializer


class HeroSectionView(BaseUnifiedAPIView):
    model = HeroSection
    serializer_class = HeroSectionSerializer


class StatView(BaseUnifiedAPIView):
    model = Stat
    serializer_class = StatSerializer


class PhotoGalleryView(BaseUnifiedAPIView):
    model = PhotoGallery
    serializer_class = PhotoGallerySerializer


# Backward Compatibility Aliases
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
PhotoGalleryDetailView = PhotoGalleryView
