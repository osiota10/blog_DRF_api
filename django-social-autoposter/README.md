# django-social-autoposter

A standalone, modular Django REST Framework package for broadcasting social media posts simultaneously across **Facebook Pages**, **Instagram Business**, **X (Twitter)**, and **LinkedIn** with unified logging, generic model linking, and environment-based configuration.

Current Version: **`0.1.1`**

---

## 🚀 Key Features

* **One-Call Multi-Platform Broadcast**: Publish content (title, message, link, image) to Facebook, Instagram, Twitter, and LinkedIn at once.
* **Decoupled Architecture**: Can be used by any domain package (`django-drf-blog-api`, `django-drf-coy-apis`, `django-mkt-place-api`, or custom apps).
* **Generic Model Attachment (`GenericForeignKey`)**: Attach social broadcast campaigns and logs to *any* model instance (e.g. `Post`, `Product`, `Event`, or standalone manual broadcasts).
* **Direct REST API Endpoint**: Allows admin dashboards and frontend applications to compose and broadcast directly (`POST /social/broadcast/`).
* **Non-Blocking Asynchronous Execution**: Dispatches HTTP network calls in background worker thread pools without slowing down web request-response times.
* **Hybrid Credential Resolution**:
  * Prioritizes database overrides (`SocialPlatformConfig`).
  * Falls back to `.env` configuration via `django-environ` / `settings.py`.
* **Execution Auditing**: Detailed per-platform logs (`SocialPostLog`) recording live post URLs, platform post IDs, and error traces.

---

## ⚡ Quick Start

### 1. Installation
```bash
pip install django-social-autoposter
```

### 2. Configure `INSTALLED_APPS`
In your Django `settings.py`:

```python
INSTALLED_APPS = [
    # Core Django apps...
    'rest_framework',
    'django_social_autoposter',
]
```

### 3. Configure `settings.py` (via `django-environ`)
```python
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

# Instagram Business API (Requires image on broadcast)
INSTAGRAM_AUTO_POST_ENABLED=True
INSTAGRAM_ACCOUNT_ID=17841400000000000
INSTAGRAM_ACCESS_TOKEN=EAAG...

# Twitter / X API v2 (OAuth 1.0a User Context)
TWITTER_AUTO_POST_ENABLED=True
TWITTER_API_KEY=your_consumer_key
TWITTER_API_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# LinkedIn API v2
LINKEDIN_AUTO_POST_ENABLED=True
LINKEDIN_ORGANIZATION_ID=987654321
LINKEDIN_ACCESS_TOKEN=AQX...
```

> **Important Twitter / X API v2 Authentication Note**:
> Twitter's `POST /2/tweets` endpoint **rejects OAuth 2.0 Application-Only Bearer Tokens** with `403 Forbidden` (`"Authenticating with OAuth 2.0 Application-Only is forbidden for this endpoint"`).
> To post tweets on behalf of an account, you must provide **OAuth 1.0a User Context** tokens (all 4: `API_KEY`, `API_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`) or an OAuth 2.0 User Context Access Token.
>
> ⚠️ **Developer Portal Setting**: In your [X Developer Portal](https://developer.x.com/) under Project & App settings -> **User authentication settings**, ensure the app permissions are set to **"Read and write"** *before* generating or regenerating the Access Token and Access Token Secret. Tokens created under "Read-only" permissions cannot publish tweets!

### 5. Include URL Patterns
In your Django `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('social/', include('django_social_autoposter.urls')),
]
```

### 6. Run Migrations
```bash
python manage.py migrate
```

---

## 🐍 Python Service Usage (From Any Package / App)

```python
from django_social_autoposter.services import SocialBroadcastService

# Broadcast to all enabled platforms
broadcast = SocialBroadcastService.broadcast(
    title="Product Launch: Next-Gen Smartphone",
    message="We are thrilled to launch our new smartphone with cutting edge AI capabilities.",
    link_url="https://example.com/products/next-gen",
    image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
    platforms=['facebook', 'twitter', 'linkedin', 'instagram'], # or None for all enabled
    source_instance=my_product_instance # Optional: attaches audit log to any model instance
)

print("Broadcast ID:", broadcast.id)
```

---

## 📡 REST API Sitemap

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/social/broadcast/` | `GET` | List past broadcast campaigns and per-platform results. |
| `/social/broadcast/` | `POST` | Compose and dispatch a post to all or selected platforms at once. |
| `/social/broadcast/<id>/` | `GET` | Retrieve details and status logs for a specific broadcast. |
| `/social/configs/` | `GET`, `POST` | List or create database-backed platform credential overrides. |
| `/social/configs/<id>/` | `GET`, `PUT`, `DELETE` | Edit or delete platform credentials. |
| `/social/logs/` | `GET` | Search and filter post execution logs (`?platform=facebook&status=published`). |

---

## 💻 Direct API Broadcast Example (Axios / JavaScript)

```javascript
import axios from 'axios';

async function publishToAllSocialMedia(userToken) {
  const payload = {
    title: "Major Announcement!",
    message: "We just launched our new mobile application. Download today!",
    link_url: "https://yourwebsite.com/download",
    image_url: "https://res.cloudinary.com/your-cloud/banner.jpg",
    platforms: ["facebook", "twitter", "linkedin", "instagram"] // or omit to use all enabled
  };

  const response = await axios.post('/social/broadcast/', payload, {
    headers: { Authorization: `Token ${userToken}` }
  });

  console.log("Broadcast Result:", response.data);
}
```

---

## 📄 License
BSD 3-Clause License. Maintained by Osiota Samuel Obrozie.
