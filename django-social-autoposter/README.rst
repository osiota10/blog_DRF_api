========================
django-social-autoposter
========================

A standalone, modular Django REST Framework package for broadcasting social media posts simultaneously across **Facebook Pages**, **Instagram Business**, **Threads**, **TikTok**, **X (Twitter)**, and **LinkedIn** with unified logging, generic model linking, and environment-based configuration.

Current Version: **0.2.0**

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
- **Facebook Pages**: Graph API v19.0 page feed sharing.
- **Instagram Business**: Two-step container creation & publishing (requires image attachment).
- **Threads (Meta)**: Two-step media container & publish API (supports text-only and images up to 500 characters).
- **TikTok**: Content Posting API direct post (photo/video via public URL).
- **X / Twitter**: API v2 ``POST /2/tweets`` via OAuth 1.0a User Context.
- **LinkedIn**: UGC Post API v2 for company organization or personal profiles.

Python Service Usage
--------------------

.. code-block:: python

    from django_social_autoposter.services import SocialBroadcastService

    broadcast = SocialBroadcastService.broadcast(
        title="Product Launch",
        message="Check out our new release!",
        link_url="https://example.com/product",
        image_url="https://example.com/image.jpg",
        platforms=['facebook', 'instagram', 'threads', 'tiktok', 'twitter', 'linkedin'],
        source_instance=my_instance
    )
