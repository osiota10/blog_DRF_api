# django-drf-blog-api

A reusable Django REST Framework blog and magazine API package with support for articles, magazine series editions, categories, tags, author profiles, backdated publications (`pub_date`), comments, likes, and Cloudinary / MediaAsset integration.

Current Version: **`0.2.2`**

---

## ⚡ Quick Start

### 1. Installation
```bash
pip install django-drf-blog-api
```

### 2. Configure `INSTALLED_APPS`
In your Django `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'media_library',
    'django_drf_blog_api',
    'django_ckeditor_5',
]
```

### 3. Add URL Patterns
In your Django `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('django_drf_blog_api/', include('django_drf_blog_api.urls')),
    path('media-library/', include('media_library.urls')),
]
```

### 4. Run Migrations
```bash
python manage.py migrate
```

---

## 📡 Key API Endpoints

* **`GET /django_drf_blog_api/post-list`**: Public blog post list (ordered by `-pub_date`).
* **`GET /django_drf_blog_api/post-list/<slug>`**: Retrieve blog post by slug.
* **`GET/POST/PUT/DELETE /django_drf_blog_api/post`**: Author post CRUD.
* **`GET/POST/PUT/DELETE /django_drf_blog_api/author`**: Logged-in author profile settings (`role`, `bio`).
* **`GET /django_drf_blog_api/authors`**: Public list of author profiles.
* **`GET /django_drf_blog_api/magazines`**: List magazine series.
* **`GET /django_drf_blog_api/magazines/<slug>`**: Retrieve magazine series details.
