# Admin Frontend Integration Guide - Blog Management (React + react-redux-django-auth)

This guide provides the complete TypeScript frontend service implementation for managing blog posts, categories, tags, and magazine series using `authClientWeb` from **`react-redux-django-auth/web`**.

`authClientWeb` manages your authentication state (JWT tokens, headers, refresh flows) automatically.

---

## ⚙️ 1. Endpoints Configuration (`@/config/endpoints.ts`)

```typescript
export const endpoints = {
  // Blog Post Management
  blogPosts: "/django_drf_blog_api/post",
  publicPostList: "/django_drf_blog_api/post-list",
  publicPostDetail: (slug: string) => `/django_drf_blog_api/post-list/${slug}`,
  
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
}

export interface Author {
  id: number;
  user: AuthorUser;
  role: string;
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
  title: string;               // e.g. "Governor Fubara: A Catalyst to a New Dawn..."
  subtitle?: string | null;
  badge?: string | null;       // e.g. "CURRENT EDITION"
  cover_media?: MediaAsset | null;
  cover_media_id?: number | null;
  cover_image_url?: string | null;
  cover_image?: string | null; // Computed property returning Cloudinary URL or external URL
  editorial_summary?: string | null;
  lead_stories?: string[];     // Array of lead story headlines
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
  magazine_series_id?: number | null;
  featured_media_id?: number | null;
  featured_image_url?: string | null;
  featured_image_url_caption?: string | null;
}

export interface UpdateBlogPostPayload extends Partial<CreateBlogPostPayload> {
  id: number;
}

export interface CreateMagazineSeriesPayload {
  series_number: string;
  edition_code: string;
  date: string;
  title: string;
  subtitle?: string;
  badge?: string;
  cover_media_id?: number | null;
  cover_image_url?: string;
  editorial_summary?: string;
  lead_stories?: string[];
}
```

---

## 🚀 3. Blog & Magazine Service (`@/services/blogService.ts`)

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

  // POST: Create a new blog post (with optional magazine_series_id)
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

  // GET: Fetch single Magazine Series by slug
  async getMagazineSeriesDetail(slug: string): Promise<MagazineSeries> {
    const client = authClientWeb();
    const endpoint = endpoints.magazineSeriesDetail(slug);

    const apiCall = client?.get(endpoint);
    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201)) {
      return response.data;
    }
    throw new Error(`Failed to fetch magazine series (HTTP ${response?.status || "Unknown"})`);
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

  // GET: Fetch post tags
  async getTags(): Promise<Tag[]> {
    const client = authClientWeb();
    const endpoint = endpoints.tags;

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

## 🖼 4. CKEditor 5 Upload Adapter via `authClientWeb`

```typescript
import { authClientWeb } from "react-redux-django-auth/web";
import { endpoints } from "@/config/endpoints";

export class AuthClientUploadAdapter {
  private loader: any;

  constructor(loader: any) {
    this.loader = loader;
  }

  async upload(): Promise<{ default: string }> {
    const file = await this.loader.file;
    const formData = new FormData();
    formData.append("upload", file);

    const client = authClientWeb();
    const endpoint = endpoints.ckeditorUpload;

    const apiCall = client?.post(endpoint, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    const response = await apiCall;

    if (response && (response.status === 200 || response.status === 201) && response.data?.url) {
      return { default: response.data.url };
    }
    throw new Error(response?.data?.error?.message || "Failed to upload inline image");
  }

  abort(): void {}
}

export function AuthClientUploadAdapterPlugin(editor: any) {
  editor.plugins.get("FileRepository").createUploadAdapter = (loader: any) => {
    return new AuthClientUploadAdapter(loader);
  };
}
```

---

## 🎨 5. Example Post Form with Magazine Series Selector

```tsx
import React, { useState, useEffect } from "react";
import { blogService } from "@/services/blogService";
import { Category, MagazineSeries } from "@/types/blog";

export const CreatePostForm: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [magazineSeriesList, setMagazineSeriesList] = useState<MagazineSeries[]>([]);
  
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [magazineSeriesId, setMagazineSeriesId] = useState<number | "">("");
  const [excerpt, setExcerpt] = useState("");
  const [readTime, setReadTime] = useState(5);
  const [featuredMediaId, setFeaturedMediaId] = useState<number | null>(null);
  const [featuredImageUrl, setFeaturedImageUrl] = useState("");
  const [imageCaption, setImageCaption] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    blogService.getCategories().then(setCategories);
    blogService.getMagazineSeries().then(setMagazineSeriesList);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !content || !categoryId) return;

    try {
      setLoading(true);
      const newPost = await blogService.createPost({
        title,
        content,
        category: Number(categoryId),
        magazine_series_id: magazineSeriesId ? Number(magazineSeriesId) : null,
        excerpt,
        read_time: readTime,
        featured_media_id: featuredMediaId,
        featured_image_url: featuredImageUrl || null,
        featured_image_url_caption: imageCaption,
      });
      alert(`Post "${newPost.title}" created successfully!`);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Category Dropdown */}
      <select value={categoryId} onChange={(e) => setCategoryId(Number(e.target.value))}>
        <option value="">Select Category</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </select>

      {/* Magazine Series Link Dropdown */}
      <select value={magazineSeriesId} onChange={(e) => setMagazineSeriesId(Number(e.target.value))}>
        <option value="">None (Independent Blog Post)</option>
        {magazineSeriesList.map((m) => (
          <option key={m.id} value={m.id}>{m.series_number} - {m.title}</option>
        ))}
      </select>
    </form>
  );
};
```
