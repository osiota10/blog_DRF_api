import logging
import concurrent.futures
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog, SocialDirectMessage
from .adapters import ADAPTERS_MAP

logger = logging.getLogger(__name__)


def get_platform_credentials(platform_name: str) -> dict:
    """
    Resolves credentials for a social media platform.
    Checks Database override (SocialPlatformConfig) first, then falls back
    to settings.SOCIAL_AUTO_POST (configured via .env / django-environ).
    """
    key = platform_name.upper()
    env_config = getattr(settings, 'SOCIAL_AUTO_POST', {}).get(key, {})

    # 1. Check Database Configuration
    try:
        db_config = SocialPlatformConfig.objects.filter(platform=platform_name.lower()).first()
        if db_config:
            if not db_config.is_enabled:
                return {'enabled': False}

            return {
                'enabled': True,
                'access_token': db_config.access_token or env_config.get('ACCESS_TOKEN', ''),
                'page_or_account_id': (
                    db_config.page_or_account_id or
                    env_config.get('PAGE_ID') or
                    env_config.get('ACCOUNT_ID') or
                    env_config.get('USER_ID') or
                    env_config.get('PHONE_NUMBER_ID') or
                    env_config.get('ORGANIZATION_ID', '')
                ),
                'api_key': db_config.api_key or env_config.get('API_KEY', ''),
                'api_secret': db_config.api_secret or env_config.get('API_SECRET', ''),
                'bearer_token': db_config.bearer_token or env_config.get('BEARER_TOKEN', ''),
                'access_token_secret': getattr(db_config, 'access_token_secret', None) or env_config.get('ACCESS_TOKEN_SECRET', ''),
                'extra_data': db_config.extra_data,
            }
    except Exception as e:
        logger.warning(f"Error reading SocialPlatformConfig for {platform_name}: {e}")

    # 2. Fallback to settings.SOCIAL_AUTO_POST
    return {
        'enabled': env_config.get('ENABLED', False),
        'access_token': env_config.get('ACCESS_TOKEN', ''),
        'page_or_account_id': (
            env_config.get('PAGE_ID') or
            env_config.get('ACCOUNT_ID') or
            env_config.get('USER_ID') or
            env_config.get('PHONE_NUMBER_ID') or
            env_config.get('ORGANIZATION_ID', '')
        ),
        'api_key': env_config.get('API_KEY', ''),
        'api_secret': env_config.get('API_SECRET', ''),
        'bearer_token': env_config.get('BEARER_TOKEN', ''),
        'access_token_secret': env_config.get('ACCESS_TOKEN_SECRET', ''),
        'extra_data': {},
    }


def _execute_publish(broadcast_id: int, platform_name: str, log_id: int):
    """
    Worker function executed in background thread pool.
    """
    try:
        broadcast = SocialBroadcast.objects.get(id=broadcast_id)
        log = SocialPostLog.objects.get(id=log_id)
    except Exception as e:
        logger.error(f"Failed to load broadcast #{broadcast_id} or log #{log_id}: {e}")
        return

    adapter_cls = ADAPTERS_MAP.get(platform_name.lower())
    if not adapter_cls:
        log.status = 'failed'
        log.error_message = f"Unsupported platform: {platform_name}"
        log.save()
        return

    creds = get_platform_credentials(platform_name)
    if not creds.get('enabled'):
        log.status = 'skipped'
        log.error_message = f"Platform {platform_name} is disabled in configuration."
        log.save()
        return

    adapter = adapter_cls(creds)
    result = adapter.publish(broadcast)

    if result.get('success'):
        log.status = 'published'
        log.external_post_id = result.get('post_id')
        log.external_post_url = result.get('post_url')
        log.response_data = result.get('raw_response') or {}
        log.error_message = None
    else:
        log.status = 'failed'
        log.error_message = result.get('error')
        log.response_data = result.get('raw_response') or {}

    log.save()

    # If all logs for this broadcast have completed, finalize broadcast status
    pending_count = SocialPostLog.objects.filter(broadcast_id=broadcast_id, status='pending').count()
    if pending_count == 0:
        b = SocialBroadcast.objects.filter(id=broadcast_id).first()
        if b and b.status in ['publishing', 'scheduled']:
            has_pub = b.logs.filter(status='published').exists()
            b.status = 'completed' if has_pub else 'failed'
            b.save(update_fields=['status', 'updated_at'])


def _dispatch_broadcast_tasks(broadcast: SocialBroadcast, tasks: list, async_dispatch: bool = True):
    broadcast.status = 'publishing'
    broadcast.published_at = timezone.now()
    broadcast.save(update_fields=['status', 'published_at', 'updated_at'])

    if not tasks:
        logger.info("No active social platforms targeted for broadcast #%s", broadcast.id)
        broadcast.status = 'completed'
        broadcast.save(update_fields=['status', 'updated_at'])
        return

    if async_dispatch:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 4))
        for b_id, plat, l_id in tasks:
            executor.submit(_execute_publish, b_id, plat, l_id)
    else:
        for b_id, plat, l_id in tasks:
            _execute_publish(b_id, plat, l_id)

        has_pub = broadcast.logs.filter(status='published').exists()
        broadcast.status = 'completed' if has_pub else 'failed'
        broadcast.save(update_fields=['status', 'updated_at'])


class SocialBroadcastService:
    """
    Unified entry point for publishing content across Facebook, Instagram, X (Twitter), LinkedIn, etc.
    Supports immediate broadcasting and future scheduled publications.
    """

    @classmethod
    def broadcast(
        cls,
        message: str,
        title: str = None,
        link_url: str = None,
        image_url: str = None,
        platforms: list = None,
        source_instance=None,
        async_dispatch: bool = True,
        scheduled_at=None,
    ) -> SocialBroadcast:
        """
        Creates a SocialBroadcast record and dispatches publication immediately or schedules it.
        
        :param message: The text message or caption.
        :param title: Optional headline / title.
        :param link_url: Optional link / article URL.
        :param image_url: Optional image attachment URL.
        :param platforms: List of platform keys (e.g. ['facebook', 'twitter']). Defaults to all enabled platforms.
        :param source_instance: Optional model instance (Post, Product, Event, etc.) to link via GenericForeignKey.
        :param async_dispatch: Whether to execute HTTP calls in background thread pool (default True).
        :param scheduled_at: Optional future datetime to schedule publishing.
        :return: SocialBroadcast model instance.
        """
        if not message:
            raise ValueError("Social broadcast message cannot be empty.")

        # Determine target platforms
        if platforms is None:
            target_platforms = []
            for p in ADAPTERS_MAP.keys():
                creds = get_platform_credentials(p)
                if creds.get('enabled'):
                    target_platforms.append(p)
        else:
            target_platforms = [p.lower() for p in platforms if p.lower() in ADAPTERS_MAP]

        # Resolve GenericForeignKey if source_instance is provided
        content_type = None
        object_id = None
        if source_instance and hasattr(source_instance, 'pk'):
            content_type = ContentType.objects.get_for_model(source_instance)
            object_id = source_instance.pk

        # Check if scheduled for the future
        is_scheduled = False
        if scheduled_at:
            if isinstance(scheduled_at, str):
                from django.utils.dateparse import parse_datetime
                parsed = parse_datetime(scheduled_at)
                if parsed:
                    scheduled_at = parsed
            if scheduled_at and scheduled_at > timezone.now():
                is_scheduled = True

        broadcast = SocialBroadcast.objects.create(
            title=title,
            message=message,
            link_url=link_url,
            image_url=image_url,
            target_platforms=target_platforms,
            content_type=content_type,
            object_id=object_id,
            status='scheduled' if is_scheduled else 'completed',
            scheduled_at=scheduled_at if is_scheduled else None,
        )

        if is_scheduled:
            logger.info("Broadcast #%s scheduled for future publication at %s", broadcast.id, scheduled_at)
            return broadcast

        # Create pending log entries and dispatch immediately
        tasks = []
        for p in target_platforms:
            log = SocialPostLog.objects.create(
                broadcast=broadcast,
                platform=p,
                status='pending'
            )
            tasks.append((broadcast.id, p, log.id))

        _dispatch_broadcast_tasks(broadcast, tasks, async_dispatch=async_dispatch)
        return broadcast

    @classmethod
    def publish_scheduled_broadcast(cls, broadcast_id: int, async_dispatch: bool = False) -> SocialBroadcast:
        """
        Publishes a previously scheduled broadcast now.
        """
        try:
            broadcast = SocialBroadcast.objects.get(pk=broadcast_id)
        except SocialBroadcast.DoesNotExist:
            raise ValueError(f"SocialBroadcast #{broadcast_id} does not exist.")

        if broadcast.status == 'cancelled':
            logger.warning("Attempted to publish cancelled broadcast #%s", broadcast.id)
            return broadcast

        tasks = []
        for p in broadcast.target_platforms:
            log = SocialPostLog.objects.filter(broadcast=broadcast, platform=p).first()
            if not log:
                log = SocialPostLog.objects.create(
                    broadcast=broadcast,
                    platform=p,
                    status='pending'
                )
            elif log.status not in ['published', 'pending']:
                log.status = 'pending'
                log.error_message = None
                log.save()
            tasks.append((broadcast.id, p, log.id))

        _dispatch_broadcast_tasks(broadcast, tasks, async_dispatch=async_dispatch)
        return broadcast

    @classmethod
    def cancel_broadcast(cls, broadcast_id: int) -> SocialBroadcast:
        """
        Cancels a scheduled or draft broadcast.
        """
        try:
            broadcast = SocialBroadcast.objects.get(pk=broadcast_id)
        except SocialBroadcast.DoesNotExist:
            raise ValueError(f"SocialBroadcast #{broadcast_id} does not exist.")

        if broadcast.status in ['completed', 'publishing']:
            raise ValueError(f"Cannot cancel a broadcast with status '{broadcast.status}'.")

        broadcast.status = 'cancelled'
        broadcast.save(update_fields=['status', 'updated_at'])
        return broadcast

    @classmethod
    def reschedule_broadcast(cls, broadcast_id: int, new_scheduled_at) -> SocialBroadcast:
        """
        Updates scheduled publication timestamp for a broadcast.
        """
        try:
            broadcast = SocialBroadcast.objects.get(pk=broadcast_id)
        except SocialBroadcast.DoesNotExist:
            raise ValueError(f"SocialBroadcast #{broadcast_id} does not exist.")

        if broadcast.status in ['completed', 'publishing', 'cancelled']:
            raise ValueError(f"Cannot reschedule a broadcast with status '{broadcast.status}'.")

        if isinstance(new_scheduled_at, str):
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(new_scheduled_at)
            if parsed:
                new_scheduled_at = parsed

        if not new_scheduled_at or new_scheduled_at <= timezone.now():
            raise ValueError("Scheduled timestamp must be in the future.")

        broadcast.scheduled_at = new_scheduled_at
        broadcast.status = 'scheduled'
        broadcast.save(update_fields=['scheduled_at', 'status', 'updated_at'])
        return broadcast


class SocialMessagingService:
    """
    Unified entry point for sending direct/private messages across Facebook Messenger,
    Instagram Direct, Twitter / X DMs, WhatsApp Business Cloud API, and LinkedIn Messaging.
    Supports immediate delivery and future scheduled messaging.
    """

    @classmethod
    def send_message(
        cls,
        platform: str,
        recipient_id: str,
        message: str,
        media_url: str = None,
        extra_params: dict = None,
        sender_id: str = None,
        scheduled_at=None,
    ) -> SocialDirectMessage:
        """
        Sends a direct message immediately or schedules it for future delivery.
        """
        plat = platform.lower()
        if not recipient_id:
            raise ValueError("Recipient ID is required to send a social direct message.")
        if not message and not media_url:
            raise ValueError("Message body or media URL is required to send a social direct message.")

        is_scheduled = False
        if scheduled_at:
            if isinstance(scheduled_at, str):
                from django.utils.dateparse import parse_datetime
                parsed = parse_datetime(scheduled_at)
                if parsed:
                    scheduled_at = parsed
            if scheduled_at and scheduled_at > timezone.now():
                is_scheduled = True

        dm = SocialDirectMessage.objects.create(
            platform=plat,
            recipient_id=str(recipient_id),
            sender_id=str(sender_id) if sender_id else None,
            message=message or '',
            media_url=media_url,
            direction='outbound',
            status='scheduled' if is_scheduled else 'pending',
            scheduled_at=scheduled_at if is_scheduled else None,
            extra_data=extra_params or {}
        )

        if is_scheduled:
            logger.info("Direct message #%s to %s scheduled for %s", dm.id, dm.recipient_id, scheduled_at)
            return dm

        return cls._dispatch_message(dm)

    @classmethod
    def _dispatch_message(cls, dm: SocialDirectMessage) -> SocialDirectMessage:
        adapter_cls = ADAPTERS_MAP.get(dm.platform)
        if not adapter_cls:
            dm.status = 'failed'
            dm.error_message = f"Unsupported platform for direct messaging: {dm.platform}"
            dm.sent_at = timezone.now()
            dm.save()
            return dm

        creds = get_platform_credentials(dm.platform)
        if not creds.get('enabled'):
            dm.status = 'failed'
            dm.error_message = f"Platform '{dm.platform}' is disabled in configuration / .env."
            dm.sent_at = timezone.now()
            dm.save()
            return dm

        adapter = adapter_cls(creds)
        res = adapter.send_direct_message(
            recipient_id=dm.recipient_id,
            text=dm.message or '',
            media_url=dm.media_url,
            extra_params=dm.extra_data or {}
        )

        dm.sent_at = timezone.now()
        if res.get('success'):
            dm.status = 'delivered'
            dm.external_message_id = res.get('message_id')
            dm.conversation_id = res.get('conversation_id')
            dm.response_data = res.get('raw_response') or {}
            dm.error_message = None
        else:
            dm.status = 'failed'
            dm.error_message = res.get('error')
            dm.response_data = res.get('raw_response') or {}

        dm.save()
        return dm

    @classmethod
    def dispatch_scheduled_message(cls, message_id: int) -> SocialDirectMessage:
        """
        Dispatches a previously scheduled message now.
        """
        try:
            dm = SocialDirectMessage.objects.get(pk=message_id)
        except SocialDirectMessage.DoesNotExist:
            raise ValueError(f"SocialDirectMessage #{message_id} does not exist.")

        if dm.status == 'cancelled':
            logger.warning("Attempted to send cancelled direct message #%s", dm.id)
            return dm

        return cls._dispatch_message(dm)

    @classmethod
    def cancel_message(cls, message_id: int) -> SocialDirectMessage:
        """
        Cancels a scheduled direct message.
        """
        try:
            dm = SocialDirectMessage.objects.get(pk=message_id)
        except SocialDirectMessage.DoesNotExist:
            raise ValueError(f"SocialDirectMessage #{message_id} does not exist.")

        if dm.status == 'delivered':
            raise ValueError("Cannot cancel a message that has already been delivered.")

        dm.status = 'cancelled'
        dm.save(update_fields=['status', 'updated_at'])
        return dm

    @classmethod
    def reschedule_message(cls, message_id: int, new_scheduled_at) -> SocialDirectMessage:
        """
        Updates scheduled delivery timestamp for a direct message.
        """
        try:
            dm = SocialDirectMessage.objects.get(pk=message_id)
        except SocialDirectMessage.DoesNotExist:
            raise ValueError(f"SocialDirectMessage #{message_id} does not exist.")

        if dm.status in ['delivered', 'cancelled']:
            raise ValueError(f"Cannot reschedule a message with status '{dm.status}'.")

        if isinstance(new_scheduled_at, str):
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(new_scheduled_at)
            if parsed:
                new_scheduled_at = parsed

        if not new_scheduled_at or new_scheduled_at <= timezone.now():
            raise ValueError("Scheduled timestamp must be in the future.")

        dm.scheduled_at = new_scheduled_at
        dm.status = 'scheduled'
        dm.save(update_fields=['scheduled_at', 'status', 'updated_at'])
        return dm


class SocialSchedulerService:
    """
    Orchestrates batch execution of due scheduled broadcasts and direct messages.
    """

    @classmethod
    def process_due_schedules(
        cls,
        limit: int = 100,
        dry_run: bool = False,
        broadcasts_only: bool = False,
        messages_only: bool = False,
    ) -> dict:
        """
        Finds all broadcasts and direct messages where scheduled_at <= now and status='scheduled'
        and executes them.
        """
        now = timezone.now()
        results = {
            'processed_at': now.isoformat(),
            'dry_run': dry_run,
            'broadcasts_due': 0,
            'broadcasts_processed': 0,
            'broadcasts_failed': 0,
            'messages_due': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'errors': [],
        }

        # 1. Process Due Broadcasts
        if not messages_only:
            due_broadcasts = list(SocialBroadcast.objects.filter(
                status='scheduled',
                scheduled_at__lte=now
            ).order_by('scheduled_at')[:limit])
            results['broadcasts_due'] = len(due_broadcasts)

            if not dry_run:
                for b in due_broadcasts:
                    try:
                        b_res = SocialBroadcastService.publish_scheduled_broadcast(b.id, async_dispatch=False)
                        if b_res and b_res.status == 'completed':
                            results['broadcasts_processed'] += 1
                        else:
                            results['broadcasts_failed'] += 1
                    except Exception as e:
                        logger.exception("Error processing scheduled broadcast #%s", b.id)
                        results['broadcasts_failed'] += 1
                        results['errors'].append(f"Broadcast #{b.id}: {str(e)}")

        # 2. Process Due Messages
        if not broadcasts_only:
            due_messages = list(SocialDirectMessage.objects.filter(
                status='scheduled',
                scheduled_at__lte=now
            ).order_by('scheduled_at')[:limit])
            results['messages_due'] = len(due_messages)

            if not dry_run:
                for msg in due_messages:
                    try:
                        msg_res = SocialMessagingService.dispatch_scheduled_message(msg.id)
                        if msg_res and msg_res.status == 'delivered':
                            results['messages_processed'] += 1
                        else:
                            results['messages_failed'] += 1
                    except Exception as e:
                        logger.exception("Error processing scheduled message #%s", msg.id)
                        results['messages_failed'] += 1
                        results['errors'].append(f"Message #{msg.id}: {str(e)}")

        return results

