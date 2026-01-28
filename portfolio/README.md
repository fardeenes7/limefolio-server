# Portfolio App

Multi-tenant SaaS backend for portfolio websites built with Django and Django REST Framework.

## Features

-   **Multi-tenant Architecture**: Each user can create multiple portfolio sites
-   **Subdomain Support**: Free subdomain (username.mysaas.com)
-   **Custom Domains**: Support for custom domain mapping with DNS verification
-   **Rich Content Management**: Projects, experiences, skills, sections
-   **Contact Forms**: Built-in contact form with spam protection
-   **Analytics**: Basic site analytics tracking
-   **RESTful API**: Complete REST API for frontend integration

## Models

### Core Models

-   **Site**: Main portfolio site model
-   **CustomDomain**: Custom domain management
-   **Section**: Flexible content sections (Hero, About, Projects, etc.)
-   **Project**: Portfolio projects with media and metadata
-   **Experience**: Work experience entries
-   **Skill**: Skills/technologies with proficiency levels
-   **SocialLink**: Social media links
-   **ContactSubmission**: Contact form submissions
-   **SiteAnalytics**: Daily analytics data

## API Structure

### Authenticated Endpoints (Owner Only)

```
/api/portfolio/sites/                           # CRUD sites
/api/portfolio/sites/{id}/domains/              # Manage custom domains
/api/portfolio/sites/{id}/sections/             # Manage sections
/api/portfolio/sites/{id}/projects/             # Manage projects
/api/portfolio/sites/{id}/experiences/          # Manage experiences
/api/portfolio/sites/{id}/skills/               # Manage skills
/api/portfolio/sites/{id}/social-links/         # Manage social links
/api/portfolio/sites/{id}/contact-submissions/  # View submissions
```

### Public Endpoints (No Auth)

```
/api/portfolio/public/sites/{subdomain}/        # Get published site
/api/portfolio/public/contact/                  # Submit contact form
```

## Permissions

-   **IsSiteOwner**: Only site owner can modify
-   **IsAuthenticatedOwner**: Authenticated users only
-   **CanManageSite**: Site management permissions (extensible for collaborators)

## Installation

1. Add to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_nested',
    'portfolio',
]
```

2. Include URLs:

```python
urlpatterns = [
    ...
    path('api/portfolio/', include('portfolio.urls')),
]
```

3. Run migrations:

```bash
python manage.py makemigrations portfolio
python manage.py migrate portfolio
```

## Usage Examples

### Create a Site

```python
POST /api/portfolio/sites/
{
  "subdomain": "johndoe",
  "title": "John Doe Portfolio",
  "tagline": "Full Stack Developer"
}
```

### Add a Project

```python
POST /api/portfolio/sites/1/projects/
{
  "title": "E-commerce Platform",
  "description": "Built with React and Django",
  "technologies": ["React", "Django", "PostgreSQL"],
  "live_url": "https://example.com",
  "featured": true
}
```

### Public Access

```python
GET /api/portfolio/public/sites/johndoe/
# Returns full site data for rendering
```

## Future Enhancements

-   [ ] Collaborator support (multiple users per site)
-   [ ] Template system
-   [ ] Advanced analytics
-   [ ] SEO optimization tools
-   [ ] Custom CSS/JS injection
-   [ ] Blog functionality
-   [ ] Multi-language support
-   [ ] Export/Import functionality
