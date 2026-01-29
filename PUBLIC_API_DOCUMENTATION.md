# Public Blog and Media API Documentation

## Overview

Public API endpoints for accessing published blog posts and media via domain-based authentication. These endpoints are accessible without authentication and automatically detect the site from the request domain.

## Base URL

```
/api/public/
```

## Authentication

- **Type**: Domain-based (automatic site detection)
- **Required**: None (public access)
- **How it works**: The site is detected from the request's `Host` header (subdomain or custom domain)

---

## Blog Endpoints

### 1. List Blog Posts

Get all published blog posts for the site.

**Endpoint**: `GET /api/public/blog/`

**Query Parameters**:

- `tag` (optional): Filter by tag
- `category` (optional): Filter by category
- `featured` (optional): Filter by featured posts (true/false)

**Response**:

```json
[
    {
        "id": 1,
        "title": "My First Blog Post",
        "slug": "my-first-blog-post",
        "excerpt": "A short description of the post...",
        "content": "Full blog post content in markdown...",
        "media": [
            {
                "id": 1,
                "image": "/media/blog/image.jpg",
                "thumbnail": "/media/blog/thumb.jpg",
                "alt": "Blog post image",
                "caption": "Image caption",
                "media_type": "image",
                "url": "/media/blog/image.jpg"
            }
        ],
        "thumbnail": "/media/blog/thumb.jpg",
        "author": "John Doe",
        "author_name": "John Doe",
        "tags": ["tech", "tutorial"],
        "categories": ["Development"],
        "meta_description": "SEO description",
        "meta_keywords": "blog, tech, tutorial",
        "status": "published",
        "is_featured": true,
        "published_at": "2026-01-30T00:00:00Z",
        "reading_time": 5,
        "view_count": 42,
        "comments_count": 3,
        "created_at": "2026-01-29T00:00:00Z",
        "updated_at": "2026-01-30T00:00:00Z"
    }
]
```

**Example Requests**:

```bash
# Get all blog posts
curl https://yoursite.limefolio.com/api/public/blog/

# Get featured posts only
curl https://yoursite.limefolio.com/api/public/blog/?featured=true

# Filter by tag
curl https://yoursite.limefolio.com/api/public/blog/?tag=tutorial

# Filter by category
curl https://yoursite.limefolio.com/api/public/blog/?category=Development
```

---

### 2. Get Blog Post Detail

Get a single published blog post by slug. Automatically increments view count.

**Endpoint**: `GET /api/public/blog/{slug}/`

**Path Parameters**:

- `slug`: Blog post slug

**Response**: Same as list endpoint, but single object

**Example**:

```bash
curl https://yoursite.limefolio.com/api/public/blog/my-first-blog-post/
```

---

### 3. Get Blog Post Comments

Get all approved comments for a blog post.

**Endpoint**: `GET /api/public/blog/{slug}/comments/`

**Path Parameters**:

- `slug`: Blog post slug

**Response**:

```json
[
    {
        "id": 1,
        "author_name": "Jane Smith",
        "author_email": "jane@example.com",
        "author_website": "https://janesmith.com",
        "content": "Great post! Very helpful.",
        "is_approved": true,
        "created_at": "2026-01-30T01:00:00Z",
        "updated_at": "2026-01-30T01:00:00Z"
    }
]
```

**Example**:

```bash
curl https://yoursite.limefolio.com/api/public/blog/my-first-blog-post/comments/
```

---

### 4. Create Comment

Submit a new comment on a blog post (requires moderation).

**Endpoint**: `POST /api/public/blog/{slug}/comments/`

**Path Parameters**:

- `slug`: Blog post slug

**Request Body**:

```json
{
    "author_name": "Jane Smith",
    "author_email": "jane@example.com",
    "author_website": "https://janesmith.com",
    "content": "Great post! Very helpful."
}
```

**Response**:

```json
{
    "message": "Comment submitted successfully. It will appear after moderation.",
    "comment": {
        "id": 1,
        "author_name": "Jane Smith",
        "author_email": "jane@example.com",
        "author_website": "https://janesmith.com",
        "content": "Great post! Very helpful.",
        "is_approved": false,
        "created_at": "2026-01-30T01:00:00Z",
        "updated_at": "2026-01-30T01:00:00Z"
    }
}
```

**Example**:

```bash
curl -X POST https://yoursite.limefolio.com/api/public/blog/my-first-blog-post/comments/ \
  -H "Content-Type: application/json" \
  -d '{
    "author_name": "Jane Smith",
    "author_email": "jane@example.com",
    "content": "Great post!"
  }'
```

---

### 5. Get All Tags

Get all unique tags from published blog posts.

**Endpoint**: `GET /api/public/blog/tags/`

**Response**:

```json
["development", "tech", "tutorial", "web"]
```

**Example**:

```bash
curl https://yoursite.limefolio.com/api/public/blog/tags/
```

---

### 6. Get All Categories

Get all unique categories from published blog posts.

**Endpoint**: `GET /api/public/blog/categories/`

**Response**:

```json
["Development", "Design", "Marketing"]
```

**Example**:

```bash
curl https://yoursite.limefolio.com/api/public/blog/categories/
```

---

## Media Endpoints

### 1. List Media

Get all media for the site (from published projects and blog posts).

**Endpoint**: `GET /api/public/media/`

**Query Parameters**:

- `content_type` (optional): Filter by content type (`project` or `blogpost`)
- `media_type` (optional): Filter by media type (`image` or `video`)
- `featured` (optional): Filter by featured media (true/false)

**Response**:

```json
[
    {
        "id": 1,
        "image": "/media/2026/01/image.jpg",
        "video": null,
        "thumbnail": "/media/thumbnails/2026/01/thumb.jpg",
        "alt": "Project screenshot",
        "caption": "Main project interface",
        "order": 0,
        "is_featured": true,
        "media_type": "image",
        "url": "/media/2026/01/image.jpg",
        "created_at": "2026-01-30T00:00:00Z",
        "updated_at": "2026-01-30T00:00:00Z"
    }
]
```

**Example Requests**:

```bash
# Get all media
curl https://yoursite.limefolio.com/api/public/media/

# Get only images
curl https://yoursite.limefolio.com/api/public/media/?media_type=image

# Get only project media
curl https://yoursite.limefolio.com/api/public/media/?content_type=project

# Get featured media only
curl https://yoursite.limefolio.com/api/public/media/?featured=true
```

---

### 2. Get Media Detail

Get a single media item by ID.

**Endpoint**: `GET /api/public/media/{id}/`

**Path Parameters**:

- `id`: Media ID

**Response**: Same as list endpoint, but single object

**Example**:

```bash
curl https://yoursite.limefolio.com/api/public/media/1/
```

---

## Error Responses

All endpoints may return the following error responses:

### Site Not Found

```json
{
    "error": "Site not found"
}
```

**Status Code**: 404

### Resource Not Found

```json
{
    "error": "Blog post not found"
}
```

**Status Code**: 404

### Validation Error

```json
{
    "field_name": ["Error message"]
}
```

**Status Code**: 400

---

## Integration Examples

### React/Next.js Example

```typescript
// Fetch blog posts
async function getBlogPosts() {
    const response = await fetch("/api/public/blog/");
    const posts = await response.json();
    return posts;
}

// Fetch single blog post
async function getBlogPost(slug: string) {
    const response = await fetch(`/api/public/blog/${slug}/`);
    const post = await response.json();
    return post;
}

// Submit comment
async function submitComment(slug: string, data: CommentData) {
    const response = await fetch(`/api/public/blog/${slug}/comments/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
    const result = await response.json();
    return result;
}

// Fetch media
async function getMedia(filters?: MediaFilters) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`/api/public/media/?${params}`);
    const media = await response.json();
    return media;
}
```

### Vue.js Example

```javascript
// composables/useBlog.js
export function useBlog() {
    const getBlogPosts = async (filters = {}) => {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/api/public/blog/?${params}`);
        return await response.json();
    };

    const getBlogPost = async (slug) => {
        const response = await fetch(`/api/public/blog/${slug}/`);
        return await response.json();
    };

    const getComments = async (slug) => {
        const response = await fetch(`/api/public/blog/${slug}/comments/`);
        return await response.json();
    };

    const submitComment = async (slug, commentData) => {
        const response = await fetch(`/api/public/blog/${slug}/comments/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(commentData),
        });
        return await response.json();
    };

    return {
        getBlogPosts,
        getBlogPost,
        getComments,
        submitComment,
    };
}
```

---

## Notes

1. **View Count**: The blog post detail endpoint automatically increments the view count each time it's accessed.

2. **Comment Moderation**: All comments submitted via the public API are set to `is_approved: false` by default and require admin approval before appearing in the public comments list.

3. **Media Access**: Only media attached to published content (published projects and blog posts) is accessible via the public API.

4. **Domain Detection**: The site is automatically detected from the request's `Host` header. Make sure your frontend is configured to send requests to the correct domain.

5. **Ordering**:
    - Blog posts are ordered by: `-published_at` (newest first)
    - Media is ordered by: `-is_featured`, `order`, `-created_at`

6. **Filtering**: All filter parameters are optional and can be combined.

---

## API Documentation

For interactive API documentation, visit:

- **Swagger UI**: `https://yoursite.limefolio.com/api/docs/`
- **ReDoc**: `https://yoursite.limefolio.com/api/redoc/`
