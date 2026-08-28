# Comprehensive Technical & API Documentation

Welcome to the official developer and integration documentation for **`django-drf-blog-api`** and **`django-drf-coy-apis`**.

This document covers installation, backend Django setup, model schemas, full REST API reference matrix, media library integration, and frontend integration using React, TypeScript, and **`react-redux-django-auth`**.

---

## 📚 Table of Contents

1. [Overview & Package Architecture](#1-overview--package-architecture)
2. [Backend Django Setup & Installation](#2-backend-django-setup--installation)
3. [Media Library & CKEditor 5 Integration](#3-media-library--ckeditor-5-integration)
4. [Blog & Magazine API Reference (`django_drf_blog_api`)](#4-blog--magazine-api-reference-django_drf_blog_api)
5. [Company & Corporate API Reference (`django_drf_coy_apis`)](#5-company--corporate-api-reference-django_drf_coy_apis)
6. [Frontend Integration Guide (TypeScript + React)](#6-frontend-integration-guide-typescript--react)

---

## 1. Overview & Package Architecture

### 📦 Published Packages

| Package | Latest PyPI Version | Primary Purpose | Key Features |
|---|---|---|---|
| **`django-drf-blog-api`** | **`0.2.2`** | Comprehensive Blog & Magazine Engine | Articles, Magazine Series, Categories, Tags, Author Profiles (role/bio), Comments, Likes, Backdated Posts (`pub_date`). |
| **`django-drf-coy-apis`** | **`0.2.0`** | Corporate & Company CMS Endpoints | Company Info, Services, Products, Team Members, Testimonials, Core Values, Events, Photo Gallery, YouTube Videos, Stats, FAQs, Contact Forms, Newsletter Subscriptions. |
| **`media_library`** | Included | Asset Storage & CKEditor Upload Handler | Centralized media asset manager linked to Cloudinary & local media storage. |

---

## 2. Backend Django Setup & Installation

### Step 1: Install PyPI Packages
```bash
pip install django-drf-blog-api django-drf-coy-apis django-ckeditor-5 djoser djangorestframework-simplejwt
```

### Step 2: Configure `settings.py`

Add the packages to `INSTALLED_APPS`:

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
    'rest_framework_simplejwt',
    'djoser',
    'django_ckeditor_5',

    # Custom DRF API packages
    'media_library',
    'django_drf_blog_api',
    'django_drf_coy_apis',
]
```

Configure REST Framework & JWT Authentication in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}
```

### Step 3: Configure `urls.py`

In your root `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from media_library.views import CKEditor5MediaUploadView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Package APIs
    path('django_drf_blog_api/', include('django_drf_blog_api.urls')),
    path('django_drf_coy_apis/', include('django_drf_coy_apis.urls')),
    path('media-library/', include('media_library.urls')),

    # Auth APIs (Djoser + JWT)
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # CKEditor 5 Upload Interceptor & Static Media
    path('ckeditor5/image_upload/', CKEditor5MediaUploadView.as_view(), name='ck_editor_5_upload_file'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Step 4: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 3. Media Library & CKEditor 5 Integration

All image fields in `django_drf_blog_api` and `django_drf_coy_apis` connect directly to **`media_library.MediaAsset`**.

### How Media Asset Linking Works
When creating or updating any record (e.g. BlogPost, Service, Product, Team Member, Company Info):
* **Read Response**: Exposes full `MediaAsset` object details under `*_media` and returns a computed URL string (`logo`, `image`, `hero_image`, `featured_image`).
* **Write Payload**: Accept `*_media_id` (the Primary Key integer of the uploaded `MediaAsset`), or fallback raw `*_url` strings.

---

## 4. Blog & Magazine API Reference (`django_drf_blog_api`)

### 📝 Blog Posts (`/django_drf_blog_api/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/django_drf_blog_api/post-list` | Public | List all public posts (ordered by `-pub_date`) |
| `GET` | `/django_drf_blog_api/post-list/<slug>` | Public | Retrieve single post by slug |
| `GET` | `/django_drf_blog_api/post` | Authenticated | List posts created by logged-in author |
| `POST` | `/django_drf_blog_api/post` | Authenticated | Create a new blog post |
| `PUT` | `/django_drf_blog_api/post` | Authenticated | Update an existing blog post |
| `DELETE` | `/django_drf_blog_api/post` | Authenticated | Delete a blog post |

#### Post Request Payload (`POST` / `PUT`)
```json
{
  "id": 12, // Required for PUT
  "title": "Governor Fubara: A Catalyst to a New Dawn",
  "content": "<p>Article content in HTML or rich text...</p>",
  "excerpt": "Short article summary...",
  "read_time": 5,
  "pub_date": "2024-05-15T10:00:00Z", // Allows past/backdated publication dates
  "category": 1,
  "magazine_series_id": 4,
  "featured_media_id": 8,
  "featured_image_url": "https://example.com/image.jpg",
  "featured_image_url_caption": "Governor Siminalayi Fubara"
}
```

---

### 👤 Author Profiles (`/django_drf_blog_api/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/django_drf_blog_api/author` | Public | Get profile of logged-in user (or by query param `?id=X`) |
| `POST`/`PUT` | `/django_drf_blog_api/author` | Authenticated | Update profile (`role`, `bio`). SuperAdmin can pass `id` |
| `DELETE` | `/django_drf_blog_api/author` | Authenticated | Delete profile (Owner or SuperAdmin) |
| `GET` | `/django_drf_blog_api/authors` | Public | List all author profiles |
| `GET` | `/django_drf_blog_api/authors/<id>` | Public | Retrieve author profile by ID |

#### Author Profile Payload (`PUT`)
```json
{
  "role": "Senior Political Editor & Columnist",
  "bio": "Covering African politics, economic policies, and governance across West Africa."
}
```

---

### 📖 Magazine Series (`/django_drf_blog_api/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/django_drf_blog_api/magazines` | Public | List all magazine series editions |
| `GET` | `/django_drf_blog_api/magazines/<slug>` | Public | Retrieve magazine series details by slug |

#### Magazine Series Schema Response
```json
{
  "id": 4,
  "series_number": "Series 41",
  "edition_code": "VOL. 41 • NO. 01",
  "date": "January 2026",
  "title": "Governor Fubara: A Catalyst to a New Dawn",
  "subtitle": "...A Celebration of African Leaders & Economic Trailblazers.",
  "badge": "CURRENT EDITION",
  "cover_media": { "id": 15, "url": "https://..." },
  "cover_image": "https://res.cloudinary.com/...",
  "editorial_summary": "Special Cover Story on Rivers State political recalibration...",
  "lead_stories": [
    "Governor Fubara: A Catalyst to a New Dawn",
    "Tantita Security Services: Turning the Tide",
    "Matthew Tonlagha at 50: A Life of Impact"
  ],
  "slug": "series-41-vol-41-no-01"
}
```

---

## 5. Company & Corporate API Reference (`django_drf_coy_apis`)

All endpoints support full **CRUD** (Create, Read, Update, Delete):

| Resource | Base Endpoint | Detail Endpoint | Public Access | Authenticated Access |
|---|---|---|---|---|
| **Company Info** | `/django_drf_coy_apis/company-info` | `/company-info/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Our Services** | `/django_drf_coy_apis/our-services` | `/our-services/<slug>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Products** | `/django_drf_coy_apis/products` | `/products/<slug>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Our Clients** | `/django_drf_coy_apis/clients` | `/clients/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Our Sponsors** | `/django_drf_coy_apis/sponsors` | `/sponsors/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Testimonials** | `/django_drf_coy_apis/testimonials` | `/testimonials/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Our Team** | `/django_drf_coy_apis/our-teams` | `/our-teams/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Core Values** | `/django_drf_coy_apis/core-values` | `/core-values/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Events** | `/django_drf_coy_apis/events` | `/events/<slug>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Hero Section** | `/django_drf_coy_apis/hero-section` | `/hero-section/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Stats** | `/django_drf_coy_apis/stat` | `/stat/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **YouTube Videos** | `/django_drf_coy_apis/youtube-videos` | `/youtube-videos/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Photo Gallery** | `/django_drf_coy_apis/photo-gallery` | `/photo-gallery/<id>` | `GET` | `POST`, `PUT`, `DELETE` |
| **Contact Us** | `/django_drf_coy_apis/contact-us` | `/contact-us/<id>` | `POST` | `GET`, `DELETE` |
| **Newsletter** | `/django_drf_coy_apis/email-subscription` | `/email-subscription/<id>` | `POST` | `GET`, `DELETE` |

---

## 6. Frontend Integration Guide (TypeScript + React)

All API calls use `authClientWeb` from **`react-redux-django-auth/web`** to manage state, tokens, and requests automatically.

### ⚙️ 1. Endpoints Config (`src/config/endpoints.ts`)

```typescript
export const endpoints = {
  // Blog & Magazine
  blogPosts: "/django_drf_blog_api/post",
  publicPostList: "/django_drf_blog_api/post-list",
  publicPostDetail: (slug: string) => `/django_drf_blog_api/post-list/${slug}`,
  authorProfile: "/django_drf_blog_api/author",
  authorsList: "/django_drf_blog_api/authors",
  magazineSeries: "/django_drf_blog_api/magazines",
  categories: "/django_drf_blog_api/category",

  // Corporate & Company
  companyInfo: "/django_drf_coy_apis/company-info",
  services: "/django_drf_coy_apis/our-services",
  products: "/django_drf_coy_apis/products",
  clients: "/django_drf_coy_apis/clients",
  team: "/django_drf_coy_apis/our-teams",
  testimonials: "/django_drf_coy_apis/testimonials",
  events: "/django_drf_coy_apis/events",

  // Media Library
  mediaAssets: "/media-library/assets/",
  ckeditorUpload: "/ckeditor5/image_upload/",
};
```

---

### 📦 2. Corporate Service (`src/services/coyService.ts`)

```typescript
import { authClientWeb } from "react-redux-django-auth/web";
import { endpoints } from "@/config/endpoints";

export interface CompanyInfoPayload {
  company_name: string;
  company_address?: string;
  telephone?: string;
  email?: string;
  about_company?: string;
  logo_media_id?: number | null;
  about_company_media_id?: number | null;
  ceo_media_id?: number | null;
}

export interface ServicePayload {
  title: string;
  description: string;
  image_media_id?: number | null;
  category_ids?: number[];
  slug?: string;
}

export const coyService = {
  // GET: Fetch Company Information
  async getCompanyInfo() {
    const client = authClientWeb();
    const response = await client?.get(endpoints.companyInfo);
    if (response && response.status === 200) {
      return Array.isArray(response.data) ? response.data[0] : response.data;
    }
    throw new Error("Failed to fetch company info");
  },

  // POST: Create or Update Company Info
  async saveCompanyInfo(data: CompanyInfoPayload, id?: number) {
    const client = authClientWeb();
    const endpoint = id ? `${endpoints.companyInfo}/${id}` : endpoints.companyInfo;
    const response = id ? await client?.put(endpoint, data) : await client?.post(endpoint, data);

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error("Failed to save company info");
  },

  // GET: Fetch All Services
  async getServices() {
    const client = authClientWeb();
    const response = await client?.get(endpoints.services);
    if (response && response.status === 200) {
      return Array.isArray(response.data) ? response.data : response.data.results || [];
    }
    return [];
  },

  // POST: Create Service
  async createService(data: ServicePayload) {
    const client = authClientWeb();
    const response = await client?.post(endpoints.services, data);
    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error("Failed to create service");
  },
};
```

---

### 🎨 3. Example React Component: Services Management Dashboard

```tsx
import React, { useState, useEffect } from "react";
import { coyService, ServicePayload } from "@/services/coyService";

export const ServicesDashboard: React.FC = () => {
  const [services, setServices] = useState<any[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    coyService.getServices().then(setServices).catch(console.error);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newService = await coyService.createService({ title, description });
      setServices([newService, ...services]);
      setTitle("");
      setDescription("");
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto bg-white rounded shadow">
      <h1 className="text-2xl font-bold mb-6">Company Services Dashboard</h1>

      <form onSubmit={handleCreate} className="mb-8 p-4 border rounded bg-gray-50">
        <h2 className="text-lg font-semibold mb-4">Add New Service</h2>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Service Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full border rounded p-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            rows={3}
            className="w-full border rounded p-2"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create Service"}
        </button>
      </form>

      <h2 className="text-lg font-semibold mb-4">Existing Services</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((service) => (
          <div key={service.id} className="border p-4 rounded shadow-sm">
            <h3 className="font-bold text-lg">{service.title}</h3>
            <p className="text-gray-600 text-sm mt-1">{service.safe_description_html || service.description}</p>
            {service.image && (
              <img src={service.image} alt={service.title} className="mt-3 h-32 w-full object-cover rounded" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```
