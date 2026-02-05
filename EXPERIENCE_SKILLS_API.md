# Experience and Skills API Documentation

This document provides comprehensive documentation for the Experience, Skills, and Social Links APIs.

## Table of Contents

- [Overview](#overview)
- [API Layers](#api-layers)
- [Models](#models)
- [Endpoints](#endpoints)
- [Examples](#examples)

---

## Overview

The Experience and Skills API provides three layers of access:

1. **Dashboard API** - Full CRUD operations for authenticated users
2. **Public API** - Read-only access based on site domain
3. **External API** - Read-only access with API key authentication

---

## API Layers

### 1. Dashboard API (Authenticated)

**Base URL:** `/api/dashboard/`  
**Authentication:** Bearer token (OAuth2)  
**Permissions:** User can only manage their own data

### 2. Public API (Domain-based)

**Base URL:** `/api/public/`  
**Authentication:** None  
**Permissions:** Read-only, filtered by site domain  
**Note:** Requires site detection via domain or subdomain

### 3. External API (API Key)

**Base URL:** `/v1/`  
**Authentication:** API Key + Secret  
**Permissions:** Read-only, filtered by API key's associated site

---

## Models

### Experience Model

Work experience entries for a portfolio site.

**Fields:**

- `id` (integer, read-only) - Unique identifier
- `company` (string, required) - Company name
- `position` (string, required) - Job position/title
- `description` (text, optional) - Job description
- `type` (string, optional) - Employment type
    - Choices: `Full Time`, `Part Time`, `Internship`, `Freelance`
- `type_display` (string, read-only) - Human-readable type
- `company_logo` (image, optional) - Company logo URL
- `url` (url, optional) - Company website
- `location` (string, optional) - Job location
- `start_date` (date, required) - Start date
- `end_date` (date, optional) - End date (null if current)
- `is_current` (boolean) - Currently working here
- `order` (integer) - Display order
- `is_published` (boolean) - Visibility status

**Ordering:** Current jobs first, then by start date (descending), then by order

---

### Skill Model

User skills with categories and proficiency levels.

**Fields:**

- `id` (integer, read-only) - Unique identifier
- `name` (string, required) - Skill name (unique per site)
- `category` (string, required) - Skill category
    - Choices: `programming`, `framework`, `database`, `devops`, `design`, `soft_skill`, `language`, `tool`, `other`
- `category_display` (string, read-only) - Human-readable category
- `proficiency` (string, required) - Proficiency level
    - Choices: `beginner`, `intermediate`, `advanced`, `expert`
- `proficiency_display` (string, read-only) - Human-readable proficiency
- `description` (text, optional) - Experience description
- `years_of_experience` (integer, optional) - Years of experience
- `icon_url` (url, optional) - Skill icon/logo URL
- `order` (integer) - Display order
- `is_featured` (boolean) - Show prominently
- `is_published` (boolean) - Visibility status

**Ordering:** Featured first, then by category, order, and name

**Constraints:** Unique combination of site and name

---

### SocialLink Model

Social media links for a portfolio site.

**Fields:**

- `id` (integer, read-only) - Unique identifier
- `platform` (string, required) - Social platform
    - Choices: `github`, `linkedin`, `twitter`, `instagram`, `facebook`, `youtube`, `dribbble`, `behance`, `medium`, `dev`, `stackoverflow`, `other`
- `url` (url, required) - Profile URL
- `username` (string, optional) - Username/handle
- `order` (integer) - Display order

**Ordering:** By order, then platform

---

## Endpoints

### Dashboard API

#### Experiences

```
GET    /api/dashboard/experiences/          - List all experiences
POST   /api/dashboard/experiences/          - Create new experience
GET    /api/dashboard/experiences/{id}/     - Get experience details
PUT    /api/dashboard/experiences/{id}/     - Update experience
PATCH  /api/dashboard/experiences/{id}/     - Partial update
DELETE /api/dashboard/experiences/{id}/     - Delete experience
```

#### Skills

```
GET    /api/dashboard/skills/               - List all skills
POST   /api/dashboard/skills/               - Create new skill
GET    /api/dashboard/skills/{id}/          - Get skill details
PUT    /api/dashboard/skills/{id}/          - Update skill
PATCH  /api/dashboard/skills/{id}/          - Partial update
DELETE /api/dashboard/skills/{id}/          - Delete skill
```

#### Social Links

```
GET    /api/dashboard/social-links/         - List all social links
POST   /api/dashboard/social-links/         - Create new social link
GET    /api/dashboard/social-links/{id}/    - Get social link details
PUT    /api/dashboard/social-links/{id}/    - Update social link
PATCH  /api/dashboard/social-links/{id}/    - Partial update
DELETE /api/dashboard/social-links/{id}/    - Delete social link
```

---

### Public API

#### Experiences

```
GET    /api/public/experiences/             - List published experiences
GET    /api/public/experiences/{id}/        - Get experience details
```

#### Skills

```
GET    /api/public/skills/                  - List published skills
GET    /api/public/skills/{id}/             - Get skill details
```

#### Social Links

```
GET    /api/public/social-links/            - List all social links
GET    /api/public/social-links/{id}/       - Get social link details
```

**Note:** Public API requires domain-based site detection via middleware.

---

### External API

#### Experiences

```
GET    /v1/experiences/                     - List published experiences
GET    /v1/experiences/{id}/                - Get experience details
```

#### Skills

```
GET    /v1/skills/                          - List published skills
GET    /v1/skills/{id}/                     - Get skill details
```

#### Social Links

```
GET    /v1/social-links/                    - List all social links
GET    /v1/social-links/{id}/               - Get social link details
```

**Authentication:** Requires API Key and Secret in headers:

```
X-API-Key: your_api_key
X-API-Secret: your_api_secret
```

---

## Examples

### Dashboard API Examples

#### Create Experience

```bash
curl -X POST https://api.limefolio.com/api/dashboard/experiences/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tech Corp",
    "position": "Senior Software Engineer",
    "description": "Led development of microservices architecture",
    "type": "Full Time",
    "location": "San Francisco, CA",
    "start_date": "2022-01-15",
    "is_current": true,
    "is_published": true,
    "order": 0
  }'
```

**Response:**

```json
{
    "id": 1,
    "company": "Tech Corp",
    "position": "Senior Software Engineer",
    "description": "Led development of microservices architecture",
    "type": "Full Time",
    "type_display": "Full Time",
    "company_logo": null,
    "url": null,
    "location": "San Francisco, CA",
    "start_date": "2022-01-15",
    "end_date": null,
    "is_current": true,
    "order": 0,
    "is_published": true
}
```

#### Create Skill

```bash
curl -X POST https://api.limefolio.com/api/dashboard/skills/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "category": "programming",
    "proficiency": "expert",
    "description": "10+ years of experience in Python development",
    "years_of_experience": 10,
    "is_featured": true,
    "is_published": true,
    "order": 0
  }'
```

**Response:**

```json
{
    "id": 1,
    "name": "Python",
    "category": "programming",
    "category_display": "Programming",
    "proficiency": "expert",
    "proficiency_display": "Expert",
    "description": "10+ years of experience in Python development",
    "years_of_experience": 10,
    "icon_url": null,
    "order": 0,
    "is_featured": true,
    "is_published": true
}
```

#### Create Social Link

```bash
curl -X POST https://api.limefolio.com/api/dashboard/social-links/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "url": "https://github.com/johndoe",
    "username": "johndoe",
    "order": 0
  }'
```

**Response:**

```json
{
    "id": 1,
    "platform": "github",
    "url": "https://github.com/johndoe",
    "username": "johndoe",
    "order": 0
}
```

#### Update Experience

```bash
curl -X PATCH https://api.limefolio.com/api/dashboard/experiences/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_current": false,
    "end_date": "2024-01-31"
  }'
```

#### List Experiences

```bash
curl https://api.limefolio.com/api/dashboard/experiences/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### Public API Examples

#### Get Published Experiences

```bash
curl https://johndoe.limefolio.com/api/public/experiences/
```

**Response:**

```json
[
    {
        "id": 1,
        "company": "Tech Corp",
        "position": "Senior Software Engineer",
        "description": "Led development of microservices architecture",
        "type": "Full Time",
        "type_display": "Full Time",
        "company_logo": "https://cdn.limefolio.com/media/logos/techcorp.png",
        "url": "https://techcorp.com",
        "location": "San Francisco, CA",
        "start_date": "2022-01-15",
        "end_date": null,
        "is_current": true,
        "order": 0,
        "is_published": true
    }
]
```

#### Get Published Skills

```bash
curl https://johndoe.limefolio.com/api/public/skills/
```

**Response:**

```json
[
    {
        "id": 1,
        "name": "Python",
        "category": "programming",
        "category_display": "Programming",
        "proficiency": "expert",
        "proficiency_display": "Expert",
        "description": "10+ years of experience in Python development",
        "years_of_experience": 10,
        "icon_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
        "order": 0,
        "is_featured": true,
        "is_published": true
    }
]
```

---

### External API Examples

#### Get Experiences with API Key

```bash
curl https://api.limefolio.com/v1/experiences/ \
  -H "X-API-Key: your_api_key_here" \
  -H "X-API-Secret: your_api_secret_here"
```

#### Get Skills with API Key

```bash
curl https://api.limefolio.com/v1/skills/ \
  -H "X-API-Key: your_api_key_here" \
  -H "X-API-Secret: your_api_secret_here"
```

---

## Filtering and Ordering

### Dashboard API

All list endpoints support standard DRF filtering:

```bash
# Filter by published status
GET /api/dashboard/experiences/?is_published=true

# Filter by current status
GET /api/dashboard/experiences/?is_current=true

# Filter skills by category
GET /api/dashboard/skills/?category=programming

# Filter skills by proficiency
GET /api/dashboard/skills/?proficiency=expert

# Filter featured skills
GET /api/dashboard/skills/?is_featured=true
```

---

## Error Responses

### 400 Bad Request

```json
{
    "field_name": ["Error message"]
}
```

### 401 Unauthorized

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
    "detail": "Not found."
}
```

---

## Best Practices

1. **Always set `is_published=true`** for items you want visible on your portfolio
2. **Use `order` field** to control display sequence
3. **Mark current job** with `is_current=true` and leave `end_date` null
4. **Feature important skills** with `is_featured=true`
5. **Use consistent categories** for better organization
6. **Add company logos** for better visual appeal
7. **Include descriptions** to provide context
8. **Set proficiency levels** accurately to set proper expectations

---

## Rate Limits

- **Dashboard API:** No rate limits for authenticated users
- **Public API:** 1000 requests per hour per IP
- **External API:** 10,000 requests per day per API key

---

## Support

For issues or questions:

- Documentation: https://docs.limefolio.com
- API Status: https://status.limefolio.com
- Support: support@limefolio.com
