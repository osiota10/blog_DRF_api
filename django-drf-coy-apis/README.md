# django-drf-coy-apis

A reusable Django REST Framework corporate CMS package providing complete CRUD endpoints for Company Information, Services, Products, Team Members, Testimonials, Core Values, Events, Photo Gallery, YouTube Videos, Key Performance Stats, Sponsors, Clients, FAQs, Contact Forms, and Email Subscriptions.

Current Version: **`0.3.0`**

---

## ⚡ Quick Start

### 1. Installation
```bash
pip install django-drf-coy-apis
```

### 2. Configure `INSTALLED_APPS`
In your Django `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'media_library',
    'django_drf_coy_apis',
    'django_ckeditor_5',
]
```

### 3. Add URL Patterns
In your Django `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('django_drf_coy_apis/', include('django_drf_coy_apis.urls')),
    path('media-library/', include('media_library.urls')),
]
```

### 4. Run Migrations
```bash
python manage.py migrate
```

---

## 📡 Key API Endpoints (All support full CRUD)

* **`Company Info`**: `/django_drf_coy_apis/company-info` and `/company-info/<id>`
* **`Services`**: `/django_drf_coy_apis/our-services` and `/our-services/<slug>`
* **`Products`**: `/django_drf_coy_apis/products` and `/products/<slug>`
* **`Our Clients`**: `/django_drf_coy_apis/clients` and `/clients/<pk>`
* **`Our Sponsors`**: `/django_drf_coy_apis/sponsors` and `/sponsors/<pk>`
* **`Testimonials`**: `/django_drf_coy_apis/testimonials` and `/testimonials/<pk>`
* **`Our Team`**: `/django_drf_coy_apis/our-teams` and `/our-teams/<pk>`
* **`Core Values`**: `/django_drf_coy_apis/core-values` and `/core-values/<pk>`
* **`Events`**: `/django_drf_coy_apis/events` and `/events/<slug>`
* **`Hero Section`**: `/django_drf_coy_apis/hero-section` and `/hero-section/<pk>`
* **`Stats`**: `/django_drf_coy_apis/stat` and `/stat/<pk>`
* **`YouTube Videos`**: `/django_drf_coy_apis/youtube-videos` and `/youtube-videos/<pk>`
* **`Photo Gallery`**: `/django_drf_coy_apis/photo-gallery` and `/photo-gallery/<pk>`
* **`Contact Forms`**: `/django_drf_coy_apis/contact-us`
* **`Email Subscriptions`**: `/django_drf_coy_apis/email-subscription`
