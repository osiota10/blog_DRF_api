========================
django-social-autoposter
========================

A standalone, modular Django REST Framework package for broadcasting social media posts simultaneously across **Facebook Pages**, **Instagram Business**, **X (Twitter)**, and **LinkedIn** with unified logging, generic model linking, and environment-based configuration.

Current Version: **0.1.1**

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

Twitter / X (API v2) User Context Requirement
----------------------------------------------
Twitter's ``POST /2/tweets`` endpoint rejects OAuth 2.0 Application-Only Bearer Tokens with ``403 Forbidden``. To post tweets on behalf of an account, provide **OAuth 1.0a User Context** tokens in ``.env`` or via ``SocialPlatformConfig``:

- ``TWITTER_API_KEY`` (Consumer Key)
- ``TWITTER_API_SECRET`` (Consumer Secret)
- ``TWITTER_ACCESS_TOKEN`` (User Access Token)
- ``TWITTER_ACCESS_TOKEN_SECRET`` (User Access Token Secret)

**Critical Developer Portal Setting:**
In `Twitter Developer Portal <https://developer.x.com/>`_ under Project & App settings -> **User authentication settings**, set app permissions to **"Read and write"** *before* generating or regenerating the Access Token and Access Token Secret.

Python Service Usage
--------------------

.. code-block:: python

    from django_social_autoposter.services import SocialBroadcastService

    broadcast = SocialBroadcastService.broadcast(
        title="Product Launch",
        message="Check out our new release!",
        link_url="https://example.com/product",
        image_url="https://example.com/image.jpg",
        platforms=['facebook', 'twitter', 'linkedin', 'instagram'],
        source_instance=my_instance
    )
