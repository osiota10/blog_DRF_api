# django-drf-blog-api

A production-ready, reusable Django REST Framework blog and magazine API package supporting articles, magazine series editions, categories, tags, author profiles, backdated publications (`pub_date`), nested comments, generic content likes, **Social Media Auto-Posting** (Facebook, Instagram, X/Twitter, LinkedIn via `django-environ`), and Cloudinary / MediaAsset integration.

Current Version: **`0.3.0`**

---

## 🚀 Key Features

* **Blog Article Management**: Rich text content (Django CKEditor 5), backdated publication scheduling (`pub_date`), excerpt, read time calculation, auto-generated unique slug, category, tags, and keywords.
* **Magazine Series Editions**: Volume/Issue management, cover image (`MediaAsset`), editorial summaries, and lead stories headlines.
* **Author Profiles**: One-to-one user account linking (`AUTH_USER_MODEL`), custom roles, and author biographies.
* **🤖 Social Media Auto-Poster**: Automatically formats and posts newly published articles to **Facebook Pages**, **Instagram Business**, **X (Twitter)**, and **LinkedIn** asynchronously without slowing down HTTP request cycles.
* **Environment-Based Security (`django-environ`)**: Store social tokens securely in `.env` with optional Django Admin overrides (`SocialPlatformConfig`).
* **Audit Logging**: Every social media post attempt is logged with status (`pending`, `published`, `failed`), external post URL, and error message in `SocialPostLog`.

---

## ⚡ Quick Start & Installation

### 1. Install Package
```bash
pip install django-drf-blog-api
```

### 2. Configure `INSTALLED_APPS`
In your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    # Django core apps...
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party required apps
    'rest_framework',
    'media_library',
    'django_ckeditor_5',

    # Blog API package
    'django_drf_blog_api',
]
```

### 3. Configure `django-environ` for Social Auto-Poster
In your `settings.py`:

```python
import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Social Media Auto-Poster Configuration
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
        'API_KEY': env.str('TWITTER_API_KEY', default=''),
        'API_SECRET': env.str('TWITTER_API_SECRET', default=''),
        'ACCESS_TOKEN': env.str('TWITTER_ACCESS_TOKEN', default=''),
        'ACCESS_TOKEN_SECRET': env.str('TWITTER_ACCESS_TOKEN_SECRET', default=''),
    },
    'LINKEDIN': {
        'ENABLED': env.bool('LINKEDIN_AUTO_POST_ENABLED', default=False),
        'ORGANIZATION_ID': env.str('LINKEDIN_ORGANIZATION_ID', default=''),
        'ACCESS_TOKEN': env.str('LINKEDIN_ACCESS_TOKEN', default=''),
    },
}
```

### 4. Setup `.env` File
Create or update `.env` in your project root:

```env
# Frontend Base URL
FRONTEND_SITE_URL=https://yourdomain.com

# Facebook Page API
FACEBOOK_AUTO_POST_ENABLED=True
FACEBOOK_PAGE_ID=109876543210
FACEBOOK_PAGE_ACCESS_TOKEN=EAAG...

# Instagram Business API (Requires featured image on Post)
INSTAGRAM_AUTO_POST_ENABLED=True
INSTAGRAM_ACCOUNT_ID=17841400000000000
INSTAGRAM_ACCESS_TOKEN=EAAG...

# X / Twitter v2 API
TWITTER_AUTO_POST_ENABLED=True
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAA...

# LinkedIn API v2
LINKEDIN_AUTO_POST_ENABLED=True
LINKEDIN_ORGANIZATION_ID=987654321
LINKEDIN_ACCESS_TOKEN=AQX...
```

### 5. Include URL Routing
In your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('django_drf_blog_api/', include('django_drf_blog_api.urls')),
    path('media-library/', include('media_library.urls')),
]
```

### 6. Run Migrations
```bash
python manage.py migrate
```

---

## 📡 Complete REST API Sitemap

### 🌐 Public Endpoints (`AllowAny`)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/django_drf_blog_api/post-list` | `GET` | List all published blog articles ordered by `-pub_date`. |
| `/django_drf_blog_api/post-list/<slug>` | `GET` | Retrieve single blog post by slug. |
| `/django_drf_blog_api/magazines` | `GET` | List all magazine series editions. |
| `/django_drf_blog_api/magazines/<slug_or_pk>` | `GET` | Retrieve single magazine series by slug or ID. |
| `/django_drf_blog_api/authors` | `GET` | List author profiles. |
| `/django_drf_blog_api/authors/<id>` | `GET` | Retrieve author profile details by ID. |
| `/django_drf_blog_api/category` | `GET` | List article categories. |
| `/django_drf_blog_api/tags` | `GET` | List article tags. |
| `/django_drf_blog_api/comment-list` | `GET` | List comments for a post (`?post_id=X`). |
| `/django_drf_blog_api/total-likes` | `GET` | Get total like count (`?content_type=post&object_id=X`). |

### 🔐 Authenticated Author & Admin Endpoints (`IsAuthenticated`)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/django_drf_blog_api/post` | `GET`, `POST`, `PUT` | Create or update blog post (triggers auto social posting). |
| `/django_drf_blog_api/author` | `GET`, `POST`, `PUT`, `DELETE` | View and edit authenticated user's author profile (`role`, `bio`). |
| `/django_drf_blog_api/magazines/` | `POST` | Create new magazine series edition. |
| `/django_drf_blog_api/magazines/<slug_or_pk>` | `PUT`, `PATCH`, `DELETE` | Edit or delete magazine series. |
| `/django_drf_blog_api/comment` | `POST` | Post new comment or reply. |
| `/django_drf_blog_api/like` | `GET`, `POST` | Toggle like status on articles or comments. |
| `/django_drf_blog_api/social-configs` | `GET`, `POST` | Inspect or override DB social platform configs. |
| `/django_drf_blog_api/social-logs` | `GET` | View social auto-poster execution log history. |

---

## 💻 Frontend Code Example (Axios / JavaScript)

```javascript
import axios from 'axios';

// Create a new Blog Post & Auto-Publish to Social Media
async function createBlogPost(token) {
  const payload = {
    title: "The Future of AI in Web Development",
    content: "<p>Artificial intelligence is transforming software engineering...</p>",
    excerpt: "Discover how AI tools are enhancing developer productivity in 2026.",
    category: 1, // Category ID
    read_time: 5,
    pub_date: "2026-10-04T10:00:00Z", // Backdated or current publication timestamp
    featured_media_id: 12 // MediaAsset ID from media_library
  };

  const response = await axios.post('/django_drf_blog_api/post', payload, {
    headers: { Authorization: `Token ${token}` }
  });

  console.log("Post Created:", response.data);
  console.log("Social Auto-Post Logs:", response.data.social_logs);
}
```

---

## 📄 License
BSD 3-Clause License. Maintained by Osiota Samuel Obrozie.
