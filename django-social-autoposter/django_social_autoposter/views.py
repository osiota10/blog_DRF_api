from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog, SocialDirectMessage
from .serializer import (
    SocialPlatformConfigSerializer,
    SocialPostLogSerializer,
    SocialBroadcastSerializer,
    SocialBroadcastCreateSerializer,
    SocialDirectMessageSerializer,
    SendMessageRequestSerializer,
    RescheduleRequestSerializer,
)
from .services import SocialBroadcastService, SocialMessagingService, SocialSchedulerService


class SocialBroadcastView(APIView):
    """
    GET: List past and scheduled broadcasts with nested social post logs.
         Optional query filter: ?status=scheduled
    POST: Compose and broadcast a post immediately or schedule it for a future timestamp.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = SocialBroadcast.objects.all().order_by('-created_at')
        broadcast_status = request.query_params.get('status')
        if broadcast_status:
            qs = qs.filter(status=broadcast_status.lower())

        serializer = SocialBroadcastSerializer(qs, many=True)
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
            media_urls=data.get('media_urls'),
            platforms=data.get('platforms'),
            async_dispatch=True,
            scheduled_at=data.get('scheduled_at'),
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


class SocialMessageSendAPIView(APIView):
    """
    POST: Send a private direct message immediately or schedule it for future delivery.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SendMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        dm = SocialMessagingService.send_message(
            platform=data['platform'],
            recipient_id=data['recipient_id'],
            message=data.get('message', ''),
            media_url=data.get('media_url'),
            extra_params=data.get('extra_params') or {},
            sender_id=data.get('sender_id'),
            scheduled_at=data.get('scheduled_at'),
        )

        status_code = status.HTTP_201_CREATED if dm.status in ['delivered', 'scheduled'] else status.HTTP_200_OK
        return Response(SocialDirectMessageSerializer(dm).data, status=status_code)


class SocialMessageListView(generics.ListAPIView):
    """
    GET: List logged direct messages with optional filters:
    ?platform=whatsapp
    ?recipient_id=+1234567890
    ?status=scheduled
    ?direction=outbound
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SocialDirectMessageSerializer

    def get_queryset(self):
        qs = SocialDirectMessage.objects.all().order_by('-created_at')
        platform = self.request.query_params.get('platform')
        recipient_id = self.request.query_params.get('recipient_id')
        msg_status = self.request.query_params.get('status')
        direction = self.request.query_params.get('direction')

        if platform:
            qs = qs.filter(platform=platform.lower())
        if recipient_id:
            qs = qs.filter(recipient_id=recipient_id)
        if msg_status:
            qs = qs.filter(status=msg_status.lower())
        if direction:
            qs = qs.filter(direction=direction.lower())

        return qs


class SocialMessageDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: Retrieve direct message delivery details.
    DELETE: Delete direct message log record.
    """
    permission_classes = [IsAuthenticated]
    queryset = SocialDirectMessage.objects.all()
    serializer_class = SocialDirectMessageSerializer


class SocialBroadcastCancelAPIView(APIView):
    """
    POST: Cancel a scheduled social broadcast.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, *args, **kwargs):
        try:
            broadcast = SocialBroadcastService.cancel_broadcast(pk)
            return Response(SocialBroadcastSerializer(broadcast).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialBroadcastPublishNowAPIView(APIView):
    """
    POST: Force immediate publication of a scheduled broadcast.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, *args, **kwargs):
        try:
            broadcast = SocialBroadcastService.publish_scheduled_broadcast(pk, async_dispatch=True)
            return Response(SocialBroadcastSerializer(broadcast).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialBroadcastRescheduleAPIView(APIView):
    """
    POST: Reschedule an existing scheduled broadcast to a new timestamp.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, *args, **kwargs):
        serializer = RescheduleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            broadcast = SocialBroadcastService.reschedule_broadcast(
                broadcast_id=pk,
                new_scheduled_at=serializer.validated_data['scheduled_at']
            )
            return Response(SocialBroadcastSerializer(broadcast).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialMessageCancelAPIView(APIView):
    """
    POST: Cancel a scheduled direct message.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, *args, **kwargs):
        try:
            dm = SocialMessagingService.cancel_message(pk)
            return Response(SocialDirectMessageSerializer(dm).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialMessageSendNowAPIView(APIView):
    """
    POST: Force immediate delivery of a scheduled direct message.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, *args, **kwargs):
        try:
            dm = SocialMessagingService.dispatch_scheduled_message(pk)
            return Response(SocialDirectMessageSerializer(dm).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialMessageRescheduleAPIView(APIView):
    """
    POST: Reschedule an existing scheduled direct message to a new timestamp.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, *args, **kwargs):
        serializer = RescheduleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            dm = SocialMessagingService.reschedule_message(
                message_id=pk,
                new_scheduled_at=serializer.validated_data['scheduled_at']
            )
            return Response(SocialDirectMessageSerializer(dm).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialScheduledOverviewAPIView(APIView):
    """
    GET: Unified overview of all upcoming scheduled broadcasts and direct messages.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        scheduled_broadcasts = SocialBroadcast.objects.filter(status='scheduled').order_by('scheduled_at')
        scheduled_messages = SocialDirectMessage.objects.filter(status='scheduled').order_by('scheduled_at')

        return Response({
            'scheduled_broadcasts': SocialBroadcastSerializer(scheduled_broadcasts, many=True).data,
            'scheduled_messages': SocialDirectMessageSerializer(scheduled_messages, many=True).data,
        }, status=status.HTTP_200_OK)
