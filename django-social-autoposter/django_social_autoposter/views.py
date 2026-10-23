from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog
from .serializer import (
    SocialPlatformConfigSerializer,
    SocialPostLogSerializer,
    SocialBroadcastSerializer,
    SocialBroadcastCreateSerializer,
)
from .services import SocialBroadcastService


class SocialBroadcastView(APIView):
    """
    GET: List past broadcasts with nested social post logs.
    POST: Compose and broadcast a post to Facebook, Instagram, X (Twitter), LinkedIn, etc. at once.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        broadcasts = SocialBroadcast.objects.all().order_by('-created_at')
        serializer = SocialBroadcastSerializer(broadcasts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SocialBroadcastCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        broadcast = SocialBroadcastService.broadcast(
            message=data.get('message'),
            title=data.get('title'),
            link_url=data.get('link_url'),
            image_url=data.get('image_url'),
            platforms=data.get('platforms'),
            async_dispatch=True,
        )

        return Response(SocialBroadcastSerializer(broadcast).data, status=status.HTTP_201_CREATED)


class SocialBroadcastDetailView(APIView):
    """
    GET: Retrieve details of a specific broadcast including per-platform logs.
    DELETE: Delete a broadcast record.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, *args, **kwargs):
        try:
            broadcast = SocialBroadcast.objects.get(pk=pk)
        except SocialBroadcast.DoesNotExist:
            return Response({'error': 'Social broadcast not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(SocialBroadcastSerializer(broadcast).data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            broadcast = SocialBroadcast.objects.get(pk=pk)
        except SocialBroadcast.DoesNotExist:
            return Response({'error': 'Social broadcast not found.'}, status=status.HTTP_404_NOT_FOUND)

        broadcast.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SocialPlatformConfigView(generics.ListCreateAPIView):
    """
    List or create database overrides for social platform credentials.
    """
    permission_classes = [IsAuthenticated]
    queryset = SocialPlatformConfig.objects.all()
    serializer_class = SocialPlatformConfigSerializer


class SocialPlatformConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a social platform configuration.
    """
    permission_classes = [IsAuthenticated]
    queryset = SocialPlatformConfig.objects.all()
    serializer_class = SocialPlatformConfigSerializer


class SocialPostLogListView(generics.ListAPIView):
    """
    List execution audit logs with optional filters:
    ?platform=facebook
    ?status=published
    ?broadcast_id=1
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SocialPostLogSerializer

    def get_queryset(self):
        qs = SocialPostLog.objects.all().order_by('-created_at')
        platform = self.request.query_params.get('platform')
        post_status = self.request.query_params.get('status')
        broadcast_id = self.request.query_params.get('broadcast_id')

        if platform:
            qs = qs.filter(platform=platform.lower())
        if post_status:
            qs = qs.filter(status=post_status.lower())
        if broadcast_id:
            qs = qs.filter(broadcast_id=broadcast_id)

        return qs
