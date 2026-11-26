========================
django-social-autoposter
========================

A standalone, modular Django REST Framework package for broadcasting social media posts, sending direct private messages, and scheduling publications across **Facebook Pages & Messenger**, **Instagram Business & Direct**, **WhatsApp Business Cloud API**, **Threads**, **TikTok**, **X (Twitter)**, and **LinkedIn** with unified logging, generic model linking, and environment-based configuration.

Current Version: **0.6.0**

Quick Start
-----------

1. Installation
~~~~~~~~~~~~~~~
.. code-block:: bash

    pip install django-social-autoposter

2. Configure ``INSTALLED_APPS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In your Django ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        'rest_framework',
        'django_social_autoposter',
    ]

3. Add URL Patterns
~~~~~~~~~~~~~~~~~~~
In your Django ``urls.py``:

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        path('social/', include('django_social_autoposter.urls')),
    ]

4. Run Migrations
~~~~~~~~~~~~~~~~~
.. code-block:: bash

    python manage.py migrate

Supported Social Media Platforms
--------------------------------
- **Facebook Pages & Messenger**: Graph API v19.0 feed, Page video, and multi-photo/video carousel posts, plus direct customer messaging.
- **Instagram Business & Direct**: Single-image, Reels video, and native multi-slide image/video Carousel publishing (up to 10 slides) and Instagram Direct messaging.
- **WhatsApp Business Cloud API**: Meta Graph API direct messaging with support for text, documents, images, audio, video, and templates.
- **Threads (Meta)**: Two-step media container & publish API (supports text-only, images, videos, and mixed Carousels up to 20 slides).
- **TikTok**: Content Posting API direct post (video via ``PULL_FROM_URL`` or multi-photo Carousel up to 35 slides).
- **X / Twitter**: API v2 ``POST /2/tweets`` with chunked image/video media upload and Direct Messaging via OAuth 1.0a / OAuth 2.0 User Context.
- **LinkedIn**: UGC Post API v2 (3-step Assets API single/multi-image and video upload) and Member Messaging API v2.

Python Service Usage
--------------------

.. code-block:: python

    from datetime import timedelta
    from django.utils import timezone
    from django_social_autoposter.services import SocialBroadcastService, SocialMessagingService

    # 1. Immediate or Scheduled Broadcast (Single Image or Multi-Image Carousel)
    broadcast = SocialBroadcastService.broadcast(
        title="Product Launch",
        message="Check out our new release!",
        link_url="https://example.com/product",
        image_url="https://example.com/image.jpg",
        media_urls=[  # Optional: pass multiple public URLs for native carousels
            "https://example.com/slide1.jpg",
            "https://example.com/slide2.jpg",
        ],
        platforms=['facebook', 'instagram', 'threads', 'tiktok', 'twitter', 'linkedin'],
        scheduled_at=timezone.now() + timedelta(days=1),  # Optional future scheduling
        source_instance=my_instance
    )

    # 2. Social Direct Messaging (Immediate or Scheduled)
    dm = SocialMessagingService.send_message(
        platform='whatsapp',
        recipient_id='+1234567890',
        message='Your order has been verified and processed.',
        media_url='https://example.com/receipt.pdf',
        extra_params={'media_type': 'document'},
        scheduled_at=timezone.now() + timedelta(hours=4)
    )

Scheduler Management Command
----------------------------

Run periodically via cron or task runner:

.. code-block:: bash

    python manage.py process_scheduled_social_posts
