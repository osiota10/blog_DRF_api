
# django-drf-blog-api


django-drf-blog-api is a Django blog API app



## Quick start


1. Add "Blog" to your INSTALLED_APPS setting like this::

    ```
    INSTALLED_APPS = [
        ...,
        "django_drf_blog_api",
        'django_ckeditor_5',
    ]
    ```
2. Include the polls URLconf in your project urls.py like this::

    ```
    from django.conf import settings
    from django.conf.urls.static import static

    # [ ... ]

    path("blog/", include("django-drf-blog-api.urls")),

    urlpatterns += [
        path("ckeditor5/", include('django_ckeditor_5.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ```

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the admin to create a poll.

5. Visit the ``/blog/`` URL to participate in the poll.
