===================
django-drf-blog-api
===================

A reusable Django REST Framework blog and magazine API package with support for articles, magazine series editions, categories, tags, author profiles, backdated publications (``pub_date``), comments, likes, **Social Media Auto-Posting** (Facebook, Instagram, X/Twitter, LinkedIn via ``django-environ``), and Cloudinary / MediaAsset integration.

Current Version: **0.3.0**

Quick Start
-----------

1. Installation
~~~~~~~~~~~~~~~
.. code-block:: bash

    pip install django-drf-blog-api

2. Configure ``INSTALLED_APPS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In your Django ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        'rest_framework',
        'media_library',
        'django_drf_blog_api',
        'django_ckeditor_5',
    ]

3. Configure Social Auto-Poster in ``settings.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    import environ
    import os

    env = environ.Env()
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

    SOCIAL_AUTO_POST = {
        'FRONTEND_SITE_URL': env.str('FRONTEND_SITE_URL', default='https://yourdomain.com'),
        'FACEBOOK': {
            'ENABLED': env.bool('FACEBOOK_AUTO_POST_ENABLED', default=False),
            'PAGE_ID': env.str('FACEBOOK_PAGE_ID', default=''),
            'ACCESS_TOKEN': env.str('FACEBOOK_PAGE_ACCESS_TOKEN', default=''),
        },
        'INSTAGRAM': {
            'ENABLED': env.bool('INSTAGRAM_AUTO_POST_ENABLED', default=False),
            'ACCOUNT_ID': env.str('INSTAGRAM_ACCOUNT_ID', default=''),
            'ACCESS_TOKEN': env.str('INSTAGRAM_ACCESS_TOKEN', default=''),
        },
        'TWITTER': {
            'ENABLED': env.bool('TWITTER_AUTO_POST_ENABLED', default=False),
            'BEARER_TOKEN': env.str('TWITTER_BEARER_TOKEN', default=''),
        },
        'LINKEDIN': {
            'ENABLED': env.bool('LINKEDIN_AUTO_POST_ENABLED', default=False),
            'ORGANIZATION_ID': env.str('LINKEDIN_ORGANIZATION_ID', default=''),
            'ACCESS_TOKEN': env.str('LINKEDIN_ACCESS_TOKEN', default=''),
        },
    }

4. Add URL Patterns
~~~~~~~~~~~~~~~~~~~
In your Django ``urls.py``:

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        path('django_drf_blog_api/', include('django_drf_blog_api.urls')),
        path('media-library/', include('media_library.urls')),
    ]

5. Run Migrations
~~~~~~~~~~~~~~~~~
.. code-block:: bash

    python manage.py migrate

Key API Endpoints
-----------------

* **GET /django_drf_blog_api/post-list**: Public blog post list.
* **GET /django_drf_blog_api/post-list/<slug>**: Retrieve blog post by slug.
* **POST /django_drf_blog_api/post**: Create blog post (triggers social auto-posting).
* **GET /django_drf_blog_api/magazines**: List magazine series.
* **POST /django_drf_blog_api/magazines/**: Create magazine series edition.
* **GET /django_drf_blog_api/social-logs**: View social media auto-poster logs.
