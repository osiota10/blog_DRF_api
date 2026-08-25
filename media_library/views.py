from rest_framework import viewsets, generics, permissions, filters
from .models import MediaAsset
from .serializers import MediaAssetSerializer


class MediaAssetViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing MediaAssets.
    Provides GET (list & retrieve), POST (create), PUT/PATCH (update), and DELETE (destroy).
    """
    queryset = MediaAsset.objects.all().order_by('-uploaded_at')
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'alt_text', 'caption']
    ordering_fields = ['uploaded_at', 'updated_at', 'title']

    def get_queryset(self):
        queryset = super().get_queryset()
        media_type = self.request.query_params.get('media_type')
        if media_type:
            queryset = queryset.filter(media_type=media_type)
        return queryset

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(uploaded_by=self.request.user)
        else:
            serializer.save()


class MediaAssetListCreateView(generics.ListCreateAPIView):
    """
    List (GET) all media assets or create (POST) a new media asset.
    """
    queryset = MediaAsset.objects.all().order_by('-uploaded_at')
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'alt_text', 'caption']

    def get_queryset(self):
        queryset = super().get_queryset()
        media_type = self.request.query_params.get('media_type')
        if media_type:
            queryset = queryset.filter(media_type=media_type)
        return queryset

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(uploaded_by=self.request.user)
        else:
            serializer.save()


class MediaAssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve (GET), update (PUT/PATCH), or delete (DELETE) a single media asset by ID.
    """
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
