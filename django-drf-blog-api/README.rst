
# django-drf-blog-api


django-drf-blog-api is a Django blog API app



## Quick start


1. Add "Blog" to your INSTALLED_APPS setting like this::

    ```
    INSTALLED_APPS = [
        ...,
        "django_drf_blog_api",
    ]
    ```
2. Include the polls URLconf in your project urls.py like this::

    path("blog/", include("django-drf-blog-api.urls")),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the admin to create a poll.

5. Visit the ``/blog/`` URL to participate in the poll.
