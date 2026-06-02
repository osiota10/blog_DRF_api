=====================
django-mkt-place-api
=====================

django-mkt-place-api is a reusable Django app package containing model registry and domain definitions for California Marketplace.

Quick start
-----------

1. Add "django_mkt_place_api.accounts", "django_mkt_place_api.notifications", "django_mkt_place_api.orders", "django_mkt_place_api.products", "django_mkt_place_api.search", "django_mkt_place_api.support_requests", and "django_mkt_place_api.vendors" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_mkt_place_api.accounts',
        'django_mkt_place_api.notifications',
        'django_mkt_place_api.orders',
        'django_mkt_place_api.products',
        'django_mkt_place_api.search',
        'django_mkt_place_api.support_requests',
        'django_mkt_place_api.vendors',
    ]

2. Set `AUTH_USER_MODEL` to your user model in settings.py.

3. Run ``python manage.py migrate`` to create the marketplace models.
