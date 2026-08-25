from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaAssetViewSet, MediaAssetListCreateView, MediaAssetDetailView, CKEditor5MediaUploadView

app_name = 'media_library'

router = DefaultRouter()
router.register(r'assets', MediaAssetViewSet, basename='media-asset')

urlpatterns = [
    # Router endpoints: /assets/ (GET list, POST create) & /assets/<id>/ (GET detail, PUT/PATCH update, DELETE destroy)
    path('', include(router.urls)),

    # Direct CBV endpoints alternative:
    path('list/', MediaAssetListCreateView.as_view(), name='media-asset-list-create'),
    path('detail/<int:pk>/', MediaAssetDetailView.as_view(), name='media-asset-detail'),
    path('ckeditor-upload/', CKEditor5MediaUploadView.as_view(), name='ckeditor5_upload'),
]
