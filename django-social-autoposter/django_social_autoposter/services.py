import logging
import concurrent.futures
from django.conf import settings
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


class SocialBroadcastService:
    """
    Unified entry point for publishing content across Facebook, Instagram, X (Twitter), LinkedIn, etc.
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
    ) -> SocialBroadcast:
        """
        Creates a SocialBroadcast record and dispatches publication to all target platforms.
        
        :param message: The text message or caption.
        :param title: Optional headline / title.
        :param link_url: Optional link / article URL.
        :param image_url: Optional image attachment URL.
        :param platforms: List of platform keys (e.g. ['facebook', 'twitter']). Defaults to all enabled platforms.
        :param source_instance: Optional model instance (Post, Product, Event, etc.) to link via GenericForeignKey.
        :param async_dispatch: Whether to execute HTTP calls in background thread pool (default True).
        :return: SocialBroadcast model instance.
        """
        if not message:
            raise ValueError("Social broadcast message cannot be empty.")

        # Determine target platforms
        if platforms is None:
            # Query all registered platforms and check credentials
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

        broadcast = SocialBroadcast.objects.create(
            title=title,
            message=message,
            link_url=link_url,
            image_url=image_url,
            target_platforms=target_platforms,
            content_type=content_type,
            object_id=object_id
        )

        # Create pending log entries
        tasks = []
        for p in target_platforms:
            log = SocialPostLog.objects.create(
                broadcast=broadcast,
                platform=p,
                status='pending'
            )
            tasks.append((broadcast.id, p, log.id))

        if not tasks:
            logger.info("No active social platforms targeted for broadcast #%s", broadcast.id)
            return broadcast

        if async_dispatch:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 4))
            for b_id, plat, l_id in tasks:
                executor.submit(_execute_publish, b_id, plat, l_id)
        else:
            for b_id, plat, l_id in tasks:
                _execute_publish(b_id, plat, l_id)

        return broadcast


class SocialMessagingService:
    """
    Unified entry point for sending direct/private messages across Facebook Messenger,
    Instagram Direct, Twitter / X DMs, WhatsApp Business Cloud API, and LinkedIn Messaging.
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
    ) -> SocialDirectMessage:
        """
        Sends a direct message and persists audit record in SocialDirectMessage.

        :param platform: Target platform slug ('facebook', 'instagram', 'twitter', 'whatsapp', 'linkedin').
        :param recipient_id: Platform user ID, phone number, or chat handle.
        :param message: Message text body.
        :param media_url: Optional media attachment URL.
        :param extra_params: Optional dict with tags, template names, or attachment types.
        :param sender_id: Optional sender ID or account ID.
        :return: SocialDirectMessage instance with delivery status and external message ID.
        """
        plat = platform.lower()
        if not recipient_id:
            raise ValueError("Recipient ID is required to send a social direct message.")
        if not message and not media_url:
            raise ValueError("Message body or media URL is required to send a social direct message.")

        # Create pending record
        dm = SocialDirectMessage.objects.create(
            platform=plat,
            recipient_id=str(recipient_id),
            sender_id=str(sender_id) if sender_id else None,
            message=message or '',
            media_url=media_url,
            direction='outbound',
            status='pending',
            extra_data=extra_params or {}
        )

        adapter_cls = ADAPTERS_MAP.get(plat)
        if not adapter_cls:
            dm.status = 'failed'
            dm.error_message = f"Unsupported platform for direct messaging: {platform}"
            dm.save()
            return dm

        creds = get_platform_credentials(plat)
        if not creds.get('enabled'):
            dm.status = 'failed'
            dm.error_message = f"Platform '{platform}' is disabled in configuration / .env."
            dm.save()
            return dm

        adapter = adapter_cls(creds)
        res = adapter.send_direct_message(
            recipient_id=str(recipient_id),
            text=message or '',
            media_url=media_url,
            extra_params=extra_params or {}
        )

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

