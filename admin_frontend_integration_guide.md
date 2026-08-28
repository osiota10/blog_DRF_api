# Admin Frontend Integration Guide - Blog Management (React + react-redux-django-auth)

This guide provides the complete TypeScript frontend service implementation for managing blog posts, categories, tags, magazine series, and **author profiles** using `authClientWeb` from **`react-redux-django-auth/web`**.

`authClientWeb` manages your authentication state (JWT tokens, headers, refresh flows) automatically.

---

## ⚙️ 1. Endpoints Configuration (`@/config/endpoints.ts`)

```typescript
export const endpoints = {
  // Blog Post Management
  blogPosts: "/django_drf_blog_api/post",
  publicPostList: "/django_drf_blog_api/post-list",
  publicPostDetail: (slug: string) => `/django_drf_blog_api/post-list/${slug}`,
  
  // Author Profile Management
  authorProfile: "/django_drf_blog_api/author",
  authorsList: "/django_drf_blog_api/authors",
  authorDetail: (id: number) => `/django_drf_blog_api/authors/${id}`,

  // Magazine Series
  magazineSeries: "/django_drf_blog_api/magazines",
  magazineSeriesDetail: (slug: string) => `/django_drf_blog_api/magazines/${slug}`,

  // Taxonomies
  categories: "/django_drf_blog_api/category",
  tags: "/django_drf_blog_api/tags",

  // Media Library
  mediaAssets: "/media-library/assets/",
  mediaAssetDetail: (id: number) => `/media-library/assets/${id}/`,
  ckeditorUpload: "/media-library/ckeditor-upload/",
};
```

---

## 📄 2. Types & Interfaces (`@/types/blog.ts`)

```typescript
export interface Category {
  id: number;
  name: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface AuthorUser {
  id: number;
  first_name: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  get_photo_url?: string | null;
  profile_picture?: string | null;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface Author {
  id: number;
  user: AuthorUser;
  role: string;
  bio?: string | null;
}

export interface UpdateAuthorProfilePayload {
  role?: string;
  bio?: string;
  id?: number; // SuperAdmin only: specify target author ID to update
}

export interface MediaAsset {
  id: number;
  title: string;
  alt_text?: string;
  caption?: string;
  media_type: "image" | "video" | "audio" | "document" | "other";
  file?: string | null;
  external_url?: string | null;
  url: string;
  thumbnail_url?: string;
  uploaded_at: string;
  updated_at: string;
}

export interface MagazineSeries {
  id: number;
  series_number: string;       // e.g. "Series 41"
  edition_code: string;        // e.g. "VOL. 41 • NO. 01"
  date: string;                // e.g. "January 2026"
  title: string;               // e.g. "Governor Fubara: A Catalyst..."
  subtitle?: string | null;
  badge?: string | null;       // e.g. "CURRENT EDITION"
  cover_media?: MediaAsset | null;
  cover_media_id?: number | null;
  cover_image_url?: string | null;
  cover_image?: string | null;
  editorial_summary?: string | null;
  lead_stories?: string[];
  slug?: string;
  created_at: string;
  updated_at: string;
}

export interface BlogPost {
  id: number;
  title: string;
  content: string;
  excerpt?: string | null;
  read_time?: number;
  readTime?: number;
  pub_date: string;
  updated_at: string;
  slug: string;
  category?: Category | null;
  tags?: Tag[];
  author: Author;
  magazine_series?: MagazineSeries | null;
  magazine_series_id?: number | null;
  featured_media?: MediaAsset | null;
  featured_media_id?: number | null;
  featured_image_url?: string | null;
  featured_image_url_caption?: string | null;
  featured_image?: string | null;
  total_comments?: number;
  total_likes?: number;
}

export interface CreateBlogPostPayload {
  title: string;
  content: string;
  category: number;
  excerpt?: string;
  read_time?: number;
  pub_date?: string; // Optional custom past/future publication date
  magazine_series_id?: number | null;
  featured_media_id?: number | null;
  featured_image_url?: string | null;
  featured_image_url_caption?: string | null;
}

export interface UpdateBlogPostPayload extends Partial<CreateBlogPostPayload> {
  id: number;
}
```

---

## 👤 3. Author Service (`@/services/authorService.ts`)

```typescript
import { authClientWeb } from "react-redux-django-auth/web";
import { endpoints } from "@/config/endpoints";
import { Author, UpdateAuthorProfilePayload } from "@/types/blog";

export const authorService = {
  // GET: Fetch current user's Author profile
  async getMyProfile(): Promise<Author> {
    const client = authClientWeb();
    const endpoint = endpoints.authorProfile;

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error("Failed to fetch author profile");
  },

  // PUT: Update current user's Author profile (role, bio), or SuperAdmin updating any author by ID
  async updateProfile(payload: UpdateAuthorProfilePayload): Promise<Author> {
    const client = authClientWeb();
    const endpoint = endpoints.authorProfile;

    const apiCall = client?.put(endpoint, payload);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error(`Failed to update author profile (HTTP ${response?.status || "Unknown"})`);
  },

  // GET: Public list of all authors
  async getAllAuthors(): Promise<Author[]> {
    const client = authClientWeb();
    const endpoint = endpoints.authorsList;

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return Array.isArray(response.data) ? response.data : response.data.results || [];
    }
    return [];
  },

  // GET: Public detail of single author by ID
  async getAuthorById(id: number): Promise<Author> {
    const client = authClientWeb();
    const endpoint = endpoints.authorDetail(id);

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error(`Failed to fetch author #${id}`);
  },

  // DELETE: Delete author profile (Owner or SuperAdmin)
  async deleteProfile(id?: number): Promise<void> {
    const client = authClientWeb();
    const endpoint = endpoints.authorProfile;

    const apiCall = client?.delete(endpoint, id ? { data: { id } } : undefined);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 204)) {
      return;
    }
    throw new Error("Failed to delete author profile");
  },
};
```

---

## 🚀 4. Blog & Magazine Service (`@/services/blogService.ts`)

```typescript
import { authClientWeb } from "react-redux-django-auth/web";
import { endpoints } from "@/config/endpoints";
import {
  BlogPost,
  CreateBlogPostPayload,
  UpdateBlogPostPayload,
  MagazineSeries,
  Category,
  Tag
} from "@/types/blog";

export const blogService = {
  // GET: Fetch list of blog posts for the logged-in author
  async getAuthorPosts(): Promise<BlogPost[]> {
    const client = authClientWeb();
    const endpoint = endpoints.blogPosts;

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      const data = response.data;
      if (Array.isArray(data)) {
        return data;
      }
      if (data && Array.isArray(data.results)) {
        return data.results;
      }
    }
    return [];
  },

  // POST: Create a new blog post
  async createPost(data: CreateBlogPostPayload): Promise<BlogPost> {
    const client = authClientWeb();
    const endpoint = endpoints.blogPosts;

    const apiCall = client?.post(endpoint, data);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error(`Failed to create post (HTTP ${response?.status || "Unknown"})`);
  },

  // PUT: Update an existing blog post
  async updatePost(data: UpdateBlogPostPayload): Promise<BlogPost> {
    const client = authClientWeb();
    const endpoint = endpoints.blogPosts;

    const apiCall = client?.put(endpoint, data);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error(`Failed to update post #${data.id} (HTTP ${response?.status || "Unknown"})`);
  },

  // DELETE: Delete a blog post
  async deletePost(id: number): Promise<void> {
    const client = authClientWeb();
    const endpoint = endpoints.blogPosts;

    const apiCall = client?.delete(endpoint, { data: { id } });
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 204)) {
      return;
    }
    throw new Error(`Failed to delete post #${id} (HTTP ${response?.status || "Unknown"})`);
  },

  // GET: Fetch all Magazine Series
  async getMagazineSeries(): Promise<MagazineSeries[]> {
    const client = authClientWeb();
    const endpoint = endpoints.magazineSeries;

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return Array.isArray(response.data) ? response.data : response.data.results || [];
    }
    return [];
  },

  // GET: Fetch post categories
  async getCategories(): Promise<Category[]> {
    const client = authClientWeb();
    const endpoint = endpoints.categories;

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return Array.isArray(response.data) ? response.data : response.data.results || [];
    }
    return [];
  },
};
```

---

## 🎨 5. Example React Component: Author Profile Settings Form

```tsx
import React, { useState, useEffect } from "react";
import { authorService } from "@/services/authorService";
import { Author } from "@/types/blog";

export const AuthorProfileSettings: React.FC = () => {
  const [profile, setProfile] = useState<Author | null>(null);
  const [role, setRole] = useState("");
  const [bio, setBio] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    authorService.getMyProfile()
      .then((data) => {
        setProfile(data);
        setRole(data.role || "Author");
        setBio(data.bio || "");
      })
      .catch((err) => setMessage(err.message));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const updated = await authorService.updateProfile({ role, bio });
      setProfile(updated);
      setMessage("Profile updated successfully!");
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!profile) return <div>Loading profile...</div>;

  return (
    <div className="p-6 max-w-lg mx-auto bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Author Profile Settings</h2>
      {message && <div className="mb-4 text-sm text-blue-600">{message}</div>}
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Name</label>
        <input
          type="text"
          disabled
          value={`${profile.user.first_name} ${profile.user.last_name || ""}`}
          className="w-full bg-gray-100 border rounded p-2 text-gray-700"
        />
      </div>

      <form onSubmit={handleSave}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Author Role / Designation</label>
          <input
            type="text"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. Senior Editor, Staff Writer"
            className="w-full border rounded p-2"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Biography (Bio)</label>
          <textarea
            rows={4}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Write a brief bio about yourself..."
            className="w-full border rounded p-2"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Saving..." : "Save Profile"}
        </button>
      </form>
    </div>
  );
};
```
