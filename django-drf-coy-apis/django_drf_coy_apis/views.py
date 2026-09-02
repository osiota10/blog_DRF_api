from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.utils.text import slugify
from .models import *
from .serializer import *


def extract_id(val):
    """Utility helper to parse integer IDs from int, str, dict {'id': ...}, or None."""
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get('id') or val.get('pk')
    if val == "" or str(val).lower() == 'null':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def extract_id_list(val):
    """Utility helper to parse list of integer IDs."""
    if not val:
        return []
    if not isinstance(val, (list, tuple, set)):
        val = [val]
    res = []
    for item in val:
        resolved = extract_id(item)
        if resolved is not None:
            res.append(resolved)
    return res


# ============================================================================
# 1. ContactFormView
# ============================================================================
class ContactFormView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = ContactForm.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'ContactForm not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ContactFormSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = ContactForm.objects.all().order_by('-id')
        serializer = ContactFormSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = ContactFormSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'ContactForm not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = ContactFormSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'ContactForm not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
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

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = EmailSubcription.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'EmailSubcription not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmailSubcriptionSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = EmailSubcription.objects.all().order_by('-id')
        serializer = EmailSubcriptionSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = EmailSubcriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'EmailSubcription not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = EmailSubcriptionSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'EmailSubcription not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 3. OurClientView
# ============================================================================
class OurClientView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = OurClient.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'OurClient not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = OurClientSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = OurClient.objects.all().order_by('-id')
        serializer = OurClientSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'logo_media_id' in data or 'logo_media' in data:
            raw_media = data.get('logo_media_id') if 'logo_media_id' in data else data.get('logo_media')
            data['logo_media_id'] = extract_id(raw_media)
            data.pop('logo_media', None)

        serializer = OurClientSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'OurClient not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'logo_media_id' in data or 'logo_media' in data:
            raw_media = data.get('logo_media_id') if 'logo_media_id' in data else data.get('logo_media')
            data['logo_media_id'] = extract_id(raw_media)
            data.pop('logo_media', None)

        serializer = OurClientSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'OurClient not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 4. OurSponsorView
# ============================================================================
class OurSponsorView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = OurSponsor.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'OurSponsor not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = OurSponsorSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = OurSponsor.objects.all().order_by('-id')
        serializer = OurSponsorSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'logo_media_id' in data or 'logo_media' in data:
            raw_media = data.get('logo_media_id') if 'logo_media_id' in data else data.get('logo_media')
            data['logo_media_id'] = extract_id(raw_media)
            data.pop('logo_media', None)

        serializer = OurSponsorSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'OurSponsor not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'logo_media_id' in data or 'logo_media' in data:
            raw_media = data.get('logo_media_id') if 'logo_media_id' in data else data.get('logo_media')
            data['logo_media_id'] = extract_id(raw_media)
            data.pop('logo_media', None)

        serializer = OurSponsorSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'OurSponsor not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 5. ServiceCategoryView
# ============================================================================
class ServiceCategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = ServiceCategory.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'ServiceCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ServiceCategorySerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = ServiceCategory.objects.all().order_by('-id')
        serializer = ServiceCategorySerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = ServiceCategorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'ServiceCategory not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = ServiceCategorySerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'ServiceCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 6. ProductCategoryView
# ============================================================================
class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = ProductCategory.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'ProductCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProductCategorySerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = ProductCategory.objects.all().order_by('-id')
        serializer = ProductCategorySerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = ProductCategorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'ProductCategory not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = ProductCategorySerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'ProductCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 7. ServiceView
# ============================================================================
class ServiceView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        query_slug = slug or self.kwargs.get('slug')
        if query_slug is None and request_data and isinstance(request_data, dict):
            query_slug = request_data.get('slug')

        if identifier is not None:
            if str(identifier).isdigit():
                obj = Service.objects.filter(pk=int(identifier)).first()
                if obj:
                    self.check_object_permissions(self.request, obj)
                    return obj
            obj = Service.objects.filter(slug=str(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        if query_slug is not None:
            obj = Service.objects.filter(slug=query_slug).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        query_slug = request.query_params.get('slug')
        if pk is not None or slug is not None or query_id or query_slug:
            obj = self.get_object(pk=pk or query_id, slug=slug or query_slug)
            if not obj:
                return Response({'detail': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ServiceSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = Service.objects.all().order_by('-id')
        serializer = ServiceSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        if 'category_ids' in data or 'category' in data:
            raw_cats = data.get('category_ids') if 'category_ids' in data else data.get('category')
            data['category_ids'] = extract_id_list(raw_cats)
            data.pop('category', None)

        if data.get('title') and not data.get('slug'):
            data['slug'] = slugify(data['title'])

        serializer = ServiceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=True)

    def update(self, request, pk=None, slug=None, partial=True):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        if 'category_ids' in data or 'category' in data:
            raw_cats = data.get('category_ids') if 'category_ids' in data else data.get('category')
            data['category_ids'] = extract_id_list(raw_cats)
            data.pop('category', None)

        if data.get('title') and not data.get('slug'):
            data['slug'] = slugify(data['title'])

        serializer = ServiceSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 8. ProductView
# ============================================================================
class ProductView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        query_slug = slug or self.kwargs.get('slug')
        if query_slug is None and request_data and isinstance(request_data, dict):
            query_slug = request_data.get('slug')

        if identifier is not None:
            if str(identifier).isdigit():
                obj = Product.objects.filter(pk=int(identifier)).first()
                if obj:
                    self.check_object_permissions(self.request, obj)
                    return obj
            obj = Product.objects.filter(slug=str(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        if query_slug is not None:
            obj = Product.objects.filter(slug=query_slug).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        query_slug = request.query_params.get('slug')
        if pk is not None or slug is not None or query_id or query_slug:
            obj = self.get_object(pk=pk or query_id, slug=slug or query_slug)
            if not obj:
                return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        if 'hero_image_media_id' in data or 'hero_image_media' in data:
            raw_hero = data.get('hero_image_media_id') if 'hero_image_media_id' in data else data.get(
                'hero_image_media')
            data['hero_image_media_id'] = extract_id(raw_hero)
            data.pop('hero_image_media', None)

        if 'category_ids' in data or 'category' in data:
            raw_cats = data.get('category_ids') if 'category_ids' in data else data.get('category')
            data['category_ids'] = extract_id_list(raw_cats)
            data.pop('category', None)

        if data.get('title') and not data.get('slug'):
            data['slug'] = slugify(data['title'])

        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=True)

    def update(self, request, pk=None, slug=None, partial=True):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        if 'hero_image_media_id' in data or 'hero_image_media' in data:
            raw_hero = data.get('hero_image_media_id') if 'hero_image_media_id' in data else data.get(
                'hero_image_media')
            data['hero_image_media_id'] = extract_id(raw_hero)
            data.pop('hero_image_media', None)

        if 'category_ids' in data or 'category' in data:
            raw_cats = data.get('category_ids') if 'category_ids' in data else data.get('category')
            data['category_ids'] = extract_id_list(raw_cats)
            data.pop('category', None)

        if data.get('title') and not data.get('slug'):
            data['slug'] = slugify(data['title'])

        serializer = ProductSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 9. TestimonialView
# ============================================================================
class TestimonialView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = Testimonial.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TestimonialSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = Testimonial.objects.all().order_by('-id')
        serializer = TestimonialSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        serializer = TestimonialSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        serializer = TestimonialSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 10. OurTeamView
# ============================================================================
class OurTeamView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = OurTeam.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'OurTeam not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = OurTeamSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = OurTeam.objects.all().order_by('-id')
        serializer = OurTeamSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        serializer = OurTeamSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'OurTeam not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        serializer = OurTeamSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'OurTeam not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 11. CompanyInfoView (Singleton)
# ============================================================================
class CompanyInfoView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        obj = CompanyInfo.load()
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        instance = CompanyInfo.load()
        serializer = CompanyInfoSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        instance = CompanyInfo.load()
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if 'logo_media_id' in data or 'logo_media' in data:
            raw_media = data.get('logo_media_id') if 'logo_media_id' in data else data.get('logo_media')
            data['logo_media_id'] = extract_id(raw_media)
            data.pop('logo_media', None)

        if 'site_page_header_image_media_id' in data or 'site_page_header_image_media' in data:
            raw_header = data.get('site_page_header_image_media_id') if 'site_page_header_image_media_id' in data else data.get(
                'site_page_header_image_media')
            data['site_page_header_image_media_id'] = extract_id(raw_header)
            data.pop('site_page_header_image_media', None)

        serializer = CompanyInfoSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        return Response({'detail': 'CompanyInfo deletion is prevented.'}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# 12. SocialUrlView
# ============================================================================
class SocialUrlView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = SocialUrl.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'SocialUrl not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = SocialUrlSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = SocialUrl.objects.all().order_by('-id')
        serializer = SocialUrlSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'company_id' in data or 'company' in data:
            raw_coy = data.get('company_id') if 'company_id' in data else data.get('company')
            data['company'] = extract_id(raw_coy)

        serializer = SocialUrlSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'SocialUrl not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'company_id' in data or 'company' in data:
            raw_coy = data.get('company_id') if 'company_id' in data else data.get('company')
            data['company'] = extract_id(raw_coy)

        serializer = SocialUrlSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'SocialUrl not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 13. FaqView
# ============================================================================
class FaqView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = FAQ.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'FAQ not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = FaqSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = FAQ.objects.all().order_by('-id')
        serializer = FaqSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'service_id' in data or 'service' in data:
            raw_svc = data.get('service_id') if 'service_id' in data else data.get('service')
            data['service'] = extract_id(raw_svc)

        if 'company_id' in data or 'company' in data:
            raw_coy = data.get('company_id') if 'company_id' in data else data.get('company')
            data['company'] = extract_id(raw_coy)

        serializer = FaqSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'FAQ not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'service_id' in data or 'service' in data:
            raw_svc = data.get('service_id') if 'service_id' in data else data.get('service')
            data['service'] = extract_id(raw_svc)

        if 'company_id' in data or 'company' in data:
            raw_coy = data.get('company_id') if 'company_id' in data else data.get('company')
            data['company'] = extract_id(raw_coy)

        serializer = FaqSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'FAQ not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 14. CoreValueView
# ============================================================================
class CoreValueView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = CoreValue.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'CoreValue not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CoreValueSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = CoreValue.objects.all().order_by('-id')
        serializer = CoreValueSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'pic_media_id' in data or 'pic_media' in data:
            raw_media = data.get('pic_media_id') if 'pic_media_id' in data else data.get('pic_media')
            data['pic_media_id'] = extract_id(raw_media)
            data.pop('pic_media', None)

        serializer = CoreValueSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'CoreValue not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'pic_media_id' in data or 'pic_media' in data:
            raw_media = data.get('pic_media_id') if 'pic_media_id' in data else data.get('pic_media')
            data['pic_media_id'] = extract_id(raw_media)
            data.pop('pic_media', None)

        serializer = CoreValueSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'CoreValue not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 15. EventView
# ============================================================================
class EventView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        query_slug = slug or self.kwargs.get('slug')
        if query_slug is None and request_data and isinstance(request_data, dict):
            query_slug = request_data.get('slug')

        if identifier is not None:
            if str(identifier).isdigit():
                obj = Event.objects.filter(pk=int(identifier)).first()
                if obj:
                    self.check_object_permissions(self.request, obj)
                    return obj
            obj = Event.objects.filter(slug=str(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        if query_slug is not None:
            obj = Event.objects.filter(slug=query_slug).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        query_slug = request.query_params.get('slug')
        if pk is not None or slug is not None or query_id or query_slug:
            obj = self.get_object(pk=pk or query_id, slug=slug or query_slug)
            if not obj:
                return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = EventSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = Event.objects.all().order_by('-id')
        serializer = EventSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        if data.get('title') and not data.get('slug'):
            data['slug'] = slugify(data['title'])

        serializer = EventSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, slug=slug, partial=True)

    def update(self, request, pk=None, slug=None, partial=True):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        if data.get('title') and not data.get('slug'):
            data['slug'] = slugify(data['title'])

        serializer = EventSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, slug=slug, request_data=request.data)
        if not obj:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 16. HeroSectionView
# ============================================================================
class HeroSectionView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = HeroSection.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'HeroSection not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = HeroSectionSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = HeroSection.objects.all().order_by('-id')
        serializer = HeroSectionSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        serializer = HeroSectionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'HeroSection not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'image_media_id' in data or 'image_media' in data:
            raw_media = data.get('image_media_id') if 'image_media_id' in data else data.get('image_media')
            data['image_media_id'] = extract_id(raw_media)
            data.pop('image_media', None)

        serializer = HeroSectionSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'HeroSection not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 17. StatView
# ============================================================================
class StatView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = Stat.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'Stat not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = StatSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = Stat.objects.all().order_by('-id')
        serializer = StatSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = StatSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'Stat not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        serializer = StatSerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'Stat not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 18. PhotoGalleryView
# ============================================================================
class PhotoGalleryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk=None, slug=None, request_data=None):
        identifier = pk or self.kwargs.get('pk') or self.kwargs.get('id')
        if identifier is None and request_data and isinstance(request_data, dict):
            identifier = request_data.get('id') or request_data.get('pk')

        if identifier is not None and str(identifier).isdigit():
            obj = PhotoGallery.objects.filter(pk=int(identifier)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return None

    def get(self, request, pk=None, slug=None, *args, **kwargs):
        query_id = request.query_params.get('id') or request.query_params.get('pk')
        if pk is not None or query_id:
            obj = self.get_object(pk=pk or query_id)
            if not obj:
                return Response({'detail': 'PhotoGallery not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = PhotoGallerySerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        records = PhotoGallery.objects.all().order_by('-id')
        serializer = PhotoGallerySerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'photo_media_id' in data or 'photo_media' in data:
            raw_media = data.get('photo_media_id') if 'photo_media_id' in data else data.get('photo_media')
            data['photo_media_id'] = extract_id(raw_media)
            data.pop('photo_media', None)

        serializer = PhotoGallerySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=False)

    def patch(self, request, pk=None, slug=None, *args, **kwargs):
        return self.update(request, pk=pk, partial=True)

    def update(self, request, pk=None, partial=True):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'PhotoGallery not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'photo_media_id' in data or 'photo_media' in data:
            raw_media = data.get('photo_media_id') if 'photo_media_id' in data else data.get('photo_media')
            data['photo_media_id'] = extract_id(raw_media)
            data.pop('photo_media', None)

        serializer = PhotoGallerySerializer(obj, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, slug=None, *args, **kwargs):
        obj = self.get_object(pk=pk, request_data=request.data)
        if not obj:
            return Response({'detail': 'PhotoGallery not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
