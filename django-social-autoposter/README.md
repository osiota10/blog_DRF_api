# django-social-autoposter

A standalone, modular Django REST Framework package for broadcasting social media posts and sending direct private messages across **Facebook Pages & Messenger**, **Instagram Business & Direct**, **WhatsApp Business Cloud API**, **Threads**, **TikTok**, **X (Twitter)**, and **LinkedIn** with unified logging, generic model linking, and environment-based configuration.

Current Version: **`0.3.0`**

---

## 🚀 Key Features

* **Multi-Platform Broadcasting**: Publish content (title, message, link, image) to Facebook, Instagram, Threads, TikTok, Twitter, and LinkedIn simultaneously.
* **Direct Messaging (DMs)**: Send direct messages to customers/users across:
  * **WhatsApp Business Cloud API** (text, images, documents, audio, video, templates)
  * **Facebook Messenger** (text, media attachments, Meta message tags)
  * **Instagram Direct Messages** (text, media attachments)
  * **Twitter / X Direct Messages** (API v2 DMs with OAuth 1.0a or OAuth 2.0 User Context)
  * **LinkedIn Messaging** (API v2 messages with recipient member URNs)
* **Decoupled Architecture**: Can be used by any domain package (`django-drf-blog-api`, `django-drf-coy-apis`, `django-mkt-place-api`, or custom apps).
* **Generic Model Attachment (`GenericForeignKey`)**: Attach social broadcast campaigns and logs to *any* model instance (e.g. `Post`, `Product`, `Event`, or standalone manual broadcasts).
* **Direct REST API Endpoints**: Full API for both broadcasting (`POST /social/broadcast/`) and direct messaging (`POST /social/messages/send/`).
* **Non-Blocking Asynchronous Execution**: Dispatches broadcast HTTP network calls in background worker thread pools without slowing down web request-response times.
* **Hybrid Credential Resolution**:
  * Prioritizes database overrides (`SocialPlatformConfig`).
  * Falls back to `.env` configuration via `django-environ` / `settings.py`.
* **Execution Auditing & Delivery Tracking**:
  * `SocialPostLog`: Detailed broadcast logs recording live post URLs, platform post IDs, and error traces.
  * `SocialDirectMessage`: Audit log tracking message status (`pending`, `delivered`, `failed`), external message IDs, and conversation IDs.

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
    'THREADS': {
        'ENABLED': env.bool('THREADS_AUTO_POST_ENABLED', default=False),
        'USER_ID': env.str('THREADS_USER_ID', default=''),
        'ACCESS_TOKEN': env.str('THREADS_ACCESS_TOKEN', default=''),
    },
    'TIKTOK': {
        'ENABLED': env.bool('TIKTOK_AUTO_POST_ENABLED', default=False),
        'ACCOUNT_ID': env.str('TIKTOK_ACCOUNT_ID', default=''),
        'ACCESS_TOKEN': env.str('TIKTOK_ACCESS_TOKEN', default=''),
    },
    'WHATSAPP': {
        'ENABLED': env.bool('WHATSAPP_AUTO_POST_ENABLED', default=False),
        'PHONE_NUMBER_ID': env.str('WHATSAPP_PHONE_NUMBER_ID', default=''),
        'ACCESS_TOKEN': env.str('WHATSAPP_ACCESS_TOKEN', default=''),
    },
}
```

### 4. Setup `.env` File
Create or update `.env` in your project root:

```env
# Frontend Base URL
FRONTEND_SITE_URL=https://yourdomain.com

# Facebook Page API & Messenger
FACEBOOK_AUTO_POST_ENABLED=True
FACEBOOK_PAGE_ID=109876543210
FACEBOOK_PAGE_ACCESS_TOKEN=EAAG...

# Instagram Business API & Direct
INSTAGRAM_AUTO_POST_ENABLED=True
INSTAGRAM_ACCOUNT_ID=17841400000000000
INSTAGRAM_ACCESS_TOKEN=EAAG...

# WhatsApp Business Cloud API
WHATSAPP_AUTO_POST_ENABLED=True
WHATSAPP_PHONE_NUMBER_ID=109876543210987
WHATSAPP_ACCESS_TOKEN=EAAG...

# Threads API (Meta)
THREADS_AUTO_POST_ENABLED=True
THREADS_USER_ID=17841400000000000
THREADS_ACCESS_TOKEN=THQ...

# TikTok Content Posting API (Requires image/video attachment)
TIKTOK_AUTO_POST_ENABLED=True
TIKTOK_ACCOUNT_ID=your_tiktok_username
TIKTOK_ACCESS_TOKEN=act.example...

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

### 1. Multi-Platform Broadcast
```python
from django_social_autoposter.services import SocialBroadcastService

# Broadcast to all enabled platforms
broadcast = SocialBroadcastService.broadcast(
    title="Product Launch: Next-Gen Smartphone",
    message="We are thrilled to launch our new smartphone with cutting edge AI capabilities.",
    link_url="https://example.com/products/next-gen",
    image_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
    platforms=['facebook', 'instagram', 'threads', 'tiktok', 'twitter', 'linkedin'], # or None for all enabled
    source_instance=my_product_instance # Optional: attaches audit log to any model instance
)

print("Broadcast ID:", broadcast.id)
```

### 2. Social Direct Messaging
```python
from django_social_autoposter.services import SocialMessagingService

# Send a WhatsApp message (E.164 phone number)
dm_wa = SocialMessagingService.send_message(
    platform='whatsapp',
    recipient_id='+1234567890',
    message='Your order #4892 has been shipped and is on its way!',
    media_url='https://example.com/tracking_label.pdf',
    extra_params={'media_type': 'document', 'filename': 'tracking.pdf'}
)
print("WhatsApp Status:", dm_wa.status, "External ID:", dm_wa.external_message_id)

# Send an Instagram Direct Message
dm_ig = SocialMessagingService.send_message(
    platform='instagram',
    recipient_id='178414000123456',  # Instagram Scoped User ID
    message='Thanks for reaching out! How can our support team assist you today?'
)

# Send an X / Twitter Direct Message
dm_tw = SocialMessagingService.send_message(
    platform='twitter',
    recipient_id='1850000000000000000',  # X User ID
    message='Here is your requested support ticket update.'
)

# Send a Facebook Messenger Message (with optional Message Tag)
dm_fb = SocialMessagingService.send_message(
    platform='facebook',
    recipient_id='1029384756',  # Page-scoped User ID
    message='Your account details were successfully updated.',
    extra_params={'tag': 'ACCOUNT_UPDATE'}
)
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
| `/social/messages/send/` | `POST` | Send a direct message to a user on WhatsApp, Instagram, FB Messenger, X, or LinkedIn. |
| `/social/messages/` | `GET` | List logged direct messages (`?platform=whatsapp&status=delivered`). |
| `/social/messages/<id>/` | `GET`, `DELETE` | Retrieve delivery details or delete a direct message log. |

---

## 💻 Direct Messaging API Example (Axios / JavaScript)

```javascript
import axios from 'axios';

// 1. Send Direct Message via WhatsApp
async function sendWhatsAppAlert(userToken, recipientPhone, alertMessage) {
  const payload = {
    platform: "whatsapp",
    recipient_id: recipientPhone, // e.g. "+15552345678"
    message: alertMessage,
    media_url: "https://example.com/receipt.pdf", // Optional
    extra_params: { media_type: "document" }
  };

  const response = await axios.post('/social/messages/send/', payload, {
    headers: { Authorization: `Token ${userToken}` }
  });

  console.log("DM Status:", response.data.status); // "delivered" | "failed"
  console.log("External Message ID:", response.data.external_message_id);
}
```

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
