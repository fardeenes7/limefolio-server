#!/usr/bin/env python
"""
Seed dummy data for limefolio portfolio
Usage: python seed_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from portfolios.models import Site
from blog.models import BlogPost
from projects.models import Project
from experiences.models import Experience, Skill, SocialLink
from media.models import Media
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


def generate_placeholder_image(width=800, height=600, text="Placeholder", bg_color=None):
    """Generate a placeholder image with text"""
    if bg_color is None:
        bg_color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text in center
    try:
        # Try to use a default font, fall back to default if not available
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((width - text_width) / 2, (height - text_height) / 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # Convert to file
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return InMemoryUploadedFile(
        buffer,
        'ImageField',
        f'{text.lower().replace(" ", "_")}.png',
        'image/png',
        buffer.getbuffer().nbytes,
        None
    )


def seed_user(username='fardeen.es7'):
    """Create or get user"""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'first_name': 'Fardeen',
            'last_name': 'Ehsan',
            'is_active': True,
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✓ Created user: {username}")
    else:
        print(f"✓ User already exists: {username}")
    return user


def seed_site(user):
    """Create or update portfolio site"""
    site, created = Site.objects.get_or_create(
        user=user,
        defaults={
            'subdomain': user.username.replace('.', '-'),
            'title': 'Fardeen Ehsan - Full Stack Developer',
            'tagline': 'Building scalable web applications with modern technologies',
            'description': 'Senior Full Stack Developer specializing in Django, React, and cloud infrastructure. Passionate about creating elegant solutions to complex problems.',
            'theme': 'dark',
            'template': 'modern',
            'font': 'inter',
            'is_published': True,
            'meta_title': 'Fardeen Ehsan | Full Stack Developer Portfolio',
            'meta_description': 'Portfolio of Fardeen Ehsan - Full Stack Developer with expertise in Django, React, AWS, and modern web technologies.',
        }
    )
    
    if created:
        print(f"✓ Created site: {site.subdomain}.limefolio.com")
    else:
        print(f"✓ Site already exists: {site.subdomain}.limefolio.com")
    
    return site


def seed_social_links(site):
    """Create social media links"""
    social_links_data = [
        {'platform': 'github', 'url': 'https://github.com/fardeenes7', 'username': 'fardeenes7', 'order': 1},
        {'platform': 'linkedin', 'url': 'https://linkedin.com/in/fardeen-ehsan', 'username': 'fardeen-ehsan', 'order': 2},
        {'platform': 'twitter', 'url': 'https://twitter.com/fardeenes7', 'username': 'fardeenes7', 'order': 3},
        {'platform': 'medium', 'url': 'https://medium.com/@fardeenes7', 'username': 'fardeenes7', 'order': 4},
        {'platform': 'stackoverflow', 'url': 'https://stackoverflow.com/users/fardeenes7', 'username': 'fardeenes7', 'order': 5},
    ]
    
    for link_data in social_links_data:
        link, created = SocialLink.objects.get_or_create(
            site=site,
            platform=link_data['platform'],
            defaults=link_data
        )
        if created:
            print(f"  ✓ Added {link_data['platform']} link")


def seed_skills(site):
    """Create skills"""
    skills_data = [
        # Programming Languages
        {'name': 'Python', 'category': 'programming', 'proficiency': 'expert', 'years_of_experience': 6, 'is_featured': True, 'order': 1},
        {'name': 'JavaScript', 'category': 'programming', 'proficiency': 'expert', 'years_of_experience': 5, 'is_featured': True, 'order': 2},
        {'name': 'TypeScript', 'category': 'programming', 'proficiency': 'advanced', 'years_of_experience': 4, 'is_featured': True, 'order': 3},
        {'name': 'Go', 'category': 'programming', 'proficiency': 'intermediate', 'years_of_experience': 2, 'order': 4},
        
        # Frameworks
        {'name': 'Django', 'category': 'framework', 'proficiency': 'expert', 'years_of_experience': 5, 'is_featured': True, 'order': 5},
        {'name': 'React', 'category': 'framework', 'proficiency': 'expert', 'years_of_experience': 5, 'is_featured': True, 'order': 6},
        {'name': 'Next.js', 'category': 'framework', 'proficiency': 'advanced', 'years_of_experience': 3, 'is_featured': True, 'order': 7},
        {'name': 'FastAPI', 'category': 'framework', 'proficiency': 'advanced', 'years_of_experience': 3, 'order': 8},
        {'name': 'Vue.js', 'category': 'framework', 'proficiency': 'intermediate', 'years_of_experience': 2, 'order': 9},
        
        # Databases
        {'name': 'PostgreSQL', 'category': 'database', 'proficiency': 'advanced', 'years_of_experience': 5, 'order': 10},
        {'name': 'MongoDB', 'category': 'database', 'proficiency': 'advanced', 'years_of_experience': 4, 'order': 11},
        {'name': 'Redis', 'category': 'database', 'proficiency': 'intermediate', 'years_of_experience': 3, 'order': 12},
        
        # DevOps/Cloud
        {'name': 'AWS', 'category': 'devops', 'proficiency': 'advanced', 'years_of_experience': 4, 'is_featured': True, 'order': 13},
        {'name': 'Docker', 'category': 'devops', 'proficiency': 'advanced', 'years_of_experience': 4, 'order': 14},
        {'name': 'Kubernetes', 'category': 'devops', 'proficiency': 'intermediate', 'years_of_experience': 2, 'order': 15},
        {'name': 'CI/CD', 'category': 'devops', 'proficiency': 'advanced', 'years_of_experience': 4, 'order': 16},
        
        # Tools
        {'name': 'Git', 'category': 'tool', 'proficiency': 'expert', 'years_of_experience': 6, 'order': 17},
        {'name': 'VS Code', 'category': 'tool', 'proficiency': 'expert', 'years_of_experience': 5, 'order': 18},
    ]
    
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            site=site,
            name=skill_data['name'],
            defaults=skill_data
        )
        if created:
            print(f"  ✓ Added skill: {skill_data['name']}")


def seed_experiences(site):
    """Create work experiences"""
    experiences_data = [
        {
            'company': 'TechCorp Solutions',
            'position': 'Senior Full Stack Developer',
            'type': 'Full Time',
            'location': 'San Francisco, CA (Remote)',
            'start_date': datetime(2022, 3, 1).date(),
            'end_date': None,
            'is_current': True,
            'description': '''Leading development of cloud-native SaaS applications serving 100K+ users.
            
• Architected and implemented microservices infrastructure using Django, FastAPI, and React
• Reduced API response time by 60% through optimization and caching strategies
• Mentored team of 5 junior developers and conducted code reviews
• Implemented CI/CD pipelines reducing deployment time from hours to minutes
• Led migration from monolithic to microservices architecture''',
            'order': 1,
        },
        {
            'company': 'StartupXYZ',
            'position': 'Full Stack Developer',
            'type': 'Full Time',
            'location': 'New York, NY',
            'start_date': datetime(2020, 1, 15).date(),
            'end_date': datetime(2022, 2, 28).date(),
            'is_current': False,
            'description': '''Built and scaled e-commerce platform from 0 to 50K monthly active users.
            
• Developed RESTful APIs using Django REST Framework
• Built responsive frontend using React and Next.js
• Integrated payment gateways (Stripe, PayPal) and shipping APIs
• Implemented real-time features using WebSockets
• Optimized database queries reducing load time by 40%''',
            'order': 2,
        },
        {
            'company': 'Digital Agency Pro',
            'position': 'Web Developer',
            'type': 'Full Time',
            'location': 'Boston, MA',
            'start_date': datetime(2018, 6, 1).date(),
            'end_date': datetime(2019, 12, 31).date(),
            'is_current': False,
            'description': '''Developed custom web applications for various clients across different industries.
            
• Created 15+ client websites using Django, WordPress, and custom solutions
• Implemented responsive designs and ensured cross-browser compatibility
• Integrated third-party APIs and services
• Provided technical support and maintenance for existing projects''',
            'order': 3,
        },
        {
            'company': 'Freelance',
            'position': 'Full Stack Developer',
            'type': 'Freelance',
            'location': 'Remote',
            'start_date': datetime(2017, 1, 1).date(),
            'end_date': datetime(2018, 5, 31).date(),
            'is_current': False,
            'description': '''Worked with various clients to deliver custom web solutions.
            
• Built 10+ web applications for small to medium businesses
• Specialized in Django backend and React frontend development
• Managed entire project lifecycle from requirements to deployment
• Maintained long-term client relationships with 90% retention rate''',
            'order': 4,
        },
    ]
    
    for exp_data in experiences_data:
        exp, created = Experience.objects.get_or_create(
            site=site,
            company=exp_data['company'],
            position=exp_data['position'],
            defaults=exp_data
        )
        if created:
            print(f"  ✓ Added experience: {exp_data['position']} at {exp_data['company']}")


def seed_projects(site):
    """Create portfolio projects with images"""
    projects_data = [
        {
            'title': 'E-Commerce Platform',
            'tagline': 'Full-featured online marketplace with real-time features',
            'description': 'A comprehensive e-commerce platform built with Django and React, featuring real-time inventory management, payment processing, and order tracking.',
            'content': '''## Overview
A modern e-commerce platform designed to handle high traffic and provide seamless shopping experience.

## Key Features
- Real-time inventory management
- Stripe payment integration
- Advanced search and filtering
- User reviews and ratings
- Admin dashboard with analytics
- Email notifications
- Mobile-responsive design

## Technical Stack
- **Backend**: Django, Django REST Framework, Celery
- **Frontend**: React, Redux, Material-UI
- **Database**: PostgreSQL, Redis
- **Infrastructure**: AWS (EC2, S3, RDS), Docker

## Challenges & Solutions
Implemented caching strategies to handle 10K+ concurrent users and optimized database queries for faster page loads.''',
            'project_url': 'https://ecommerce-demo.example.com',
            'github_url': 'https://github.com/fardeenes7/ecommerce-platform',
            'technologies': ['Django', 'React', 'PostgreSQL', 'Redis', 'AWS', 'Docker', 'Stripe'],
            'featured': True,
            'start_date': datetime(2022, 1, 1).date(),
            'end_date': datetime(2022, 6, 30).date(),
            'order': 1,
        },
        {
            'title': 'Task Management SaaS',
            'tagline': 'Collaborative project management tool for teams',
            'description': 'A SaaS application for team collaboration and project management with real-time updates and integrations.',
            'content': '''## Overview
A powerful task management platform designed for remote teams to collaborate effectively.

## Key Features
- Real-time collaboration with WebSockets
- Kanban boards and list views
- Time tracking and reporting
- File attachments and comments
- Third-party integrations (Slack, Google Drive)
- Role-based access control

## Technical Stack
- **Backend**: Django, Django Channels, Celery
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database**: PostgreSQL
- **Real-time**: WebSockets, Redis
- **Infrastructure**: Vercel, AWS

## Impact
Used by 500+ teams with 99.9% uptime and average response time under 200ms.''',
            'project_url': 'https://taskmanager.example.com',
            'github_url': 'https://github.com/fardeenes7/task-manager',
            'technologies': ['Django', 'Next.js', 'TypeScript', 'PostgreSQL', 'WebSockets', 'Redis'],
            'featured': True,
            'start_date': datetime(2021, 6, 1).date(),
            'end_date': datetime(2021, 12, 31).date(),
            'order': 2,
        },
        {
            'title': 'AI Content Generator',
            'tagline': 'GPT-powered content creation platform',
            'description': 'An AI-powered platform that helps content creators generate blog posts, social media content, and marketing copy.',
            'content': '''## Overview
Leveraging OpenAI's GPT models to help content creators produce high-quality content faster.

## Key Features
- Multiple content types (blogs, social media, ads)
- Template library
- SEO optimization suggestions
- Plagiarism checking
- Content scheduling
- Team collaboration

## Technical Stack
- **Backend**: FastAPI, Python
- **Frontend**: React, TypeScript
- **AI**: OpenAI GPT-4 API
- **Database**: MongoDB
- **Infrastructure**: AWS Lambda, API Gateway

## Results
Generated 100K+ pieces of content for 5K+ users with 95% satisfaction rate.''',
            'project_url': 'https://ai-content.example.com',
            'github_url': 'https://github.com/fardeenes7/ai-content-generator',
            'technologies': ['FastAPI', 'React', 'OpenAI', 'MongoDB', 'AWS Lambda'],
            'featured': True,
            'start_date': datetime(2023, 1, 1).date(),
            'end_date': datetime(2023, 5, 31).date(),
            'order': 3,
        },
        {
            'title': 'Real Estate Listing Platform',
            'tagline': 'Modern property search and listing platform',
            'description': 'A comprehensive real estate platform with advanced search, virtual tours, and agent management.',
            'content': '''## Overview
A feature-rich platform connecting property buyers, sellers, and real estate agents.

## Key Features
- Advanced property search with filters
- Interactive maps integration
- Virtual tour support
- Agent profiles and ratings
- Mortgage calculator
- Saved searches and alerts

## Technical Stack
- **Backend**: Django, Django REST Framework
- **Frontend**: Vue.js, Vuetify
- **Database**: PostgreSQL, PostGIS
- **Maps**: Google Maps API
- **Infrastructure**: DigitalOcean

## Scale
Hosting 50K+ property listings with 20K monthly active users.''',
            'project_url': 'https://realestate.example.com',
            'github_url': 'https://github.com/fardeenes7/realestate-platform',
            'technologies': ['Django', 'Vue.js', 'PostgreSQL', 'PostGIS', 'Google Maps'],
            'featured': False,
            'start_date': datetime(2020, 8, 1).date(),
            'end_date': datetime(2021, 2, 28).date(),
            'order': 4,
        },
        {
            'title': 'Social Media Analytics Dashboard',
            'tagline': 'Comprehensive analytics for social media managers',
            'description': 'A dashboard that aggregates data from multiple social media platforms to provide insights and analytics.',
            'content': '''## Overview
Unified analytics platform for managing multiple social media accounts and campaigns.

## Key Features
- Multi-platform integration (Twitter, Instagram, Facebook)
- Real-time analytics and reporting
- Competitor analysis
- Content scheduling
- Custom reports and exports
- Team collaboration

## Technical Stack
- **Backend**: Django, Celery
- **Frontend**: React, Chart.js, D3.js
- **Database**: PostgreSQL, TimescaleDB
- **APIs**: Twitter API, Instagram Graph API, Facebook Graph API
- **Infrastructure**: AWS

## Performance
Processing 1M+ social media posts daily with sub-second query times.''',
            'project_url': 'https://social-analytics.example.com',
            'technologies': ['Django', 'React', 'PostgreSQL', 'TimescaleDB', 'AWS'],
            'featured': False,
            'start_date': datetime(2022, 7, 1).date(),
            'end_date': datetime(2022, 11, 30).date(),
            'order': 5,
        },
    ]
    
    for proj_data in projects_data:
        project, created = Project.objects.get_or_create(
            site=site,
            title=proj_data['title'],
            defaults=proj_data
        )
        
        if created:
            print(f"  ✓ Added project: {proj_data['title']}")
            
            # Add project images
            content_type = ContentType.objects.get_for_model(Project)
            
            # Main project image
            main_img = generate_placeholder_image(
                1200, 800, 
                proj_data['title'],
                bg_color=(random.randint(30, 100), random.randint(80, 150), random.randint(100, 200))
            )
            media1 = Media.objects.create(
                content_type=content_type,
                object_id=project.id,
                image=main_img,
                alt=f"{proj_data['title']} - Main Screenshot",
                caption=f"Main interface of {proj_data['title']}",
                is_featured=True,
                order=1
            )
            print(f"    ✓ Added featured image for {proj_data['title']}")
            
            # Additional screenshots
            for i in range(2, 4):
                img = generate_placeholder_image(
                    1200, 800,
                    f"{proj_data['title']} - View {i}",
                    bg_color=(random.randint(40, 120), random.randint(60, 140), random.randint(80, 180))
                )
                media = Media.objects.create(
                    content_type=content_type,
                    object_id=project.id,
                    image=img,
                    alt=f"{proj_data['title']} - Screenshot {i}",
                    caption=f"Additional view of {proj_data['title']}",
                    order=i
                )
            print(f"    ✓ Added {2} additional images")


def seed_blog_posts(site):
    """Create blog posts with images"""
    blog_posts_data = [
        {
            'title': 'Building Scalable Django Applications: Best Practices',
            'excerpt': 'Learn how to build Django applications that can scale to millions of users with proper architecture and optimization techniques.',
            'content': '''# Building Scalable Django Applications: Best Practices

As your Django application grows, scalability becomes crucial. Here are the key practices I've learned from building applications serving millions of users.

## 1. Database Optimization

### Use Database Indexes Wisely
```python
class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
```

### Select Related and Prefetch Related
Always use `select_related()` and `prefetch_related()` to avoid N+1 queries:
```python
# Bad
articles = Article.objects.all()
for article in articles:
    print(article.author.name)  # N+1 queries!

# Good
articles = Article.objects.select_related('author').all()
for article in articles:
    print(article.author.name)  # Single query
```

## 2. Caching Strategies

Implement multi-level caching:
- **Database query caching** with Redis
- **Template fragment caching** for expensive renders
- **CDN caching** for static assets

## 3. Asynchronous Tasks

Use Celery for background tasks:
```python
@shared_task
def send_email_notification(user_id):
    user = User.objects.get(id=user_id)
    send_mail(...)
```

## 4. API Optimization

- Use pagination for list endpoints
- Implement proper serializer optimization
- Add rate limiting to prevent abuse

## Conclusion

Scalability is not just about handling more users—it's about maintaining performance and reliability as you grow. Start with these practices early, and your future self will thank you.''',
            'tags': ['Django', 'Python', 'Scalability', 'Best Practices', 'Backend'],
            'categories': ['Web Development', 'Backend'],
            'status': 'published',
            'is_featured': True,
            'published_at': timezone.now() - timedelta(days=7),
        },
        {
            'title': 'React Performance Optimization: A Complete Guide',
            'excerpt': 'Comprehensive guide to optimizing React applications for better performance and user experience.',
            'content': '''# React Performance Optimization: A Complete Guide

Performance is critical for user experience. Here's how to make your React apps blazing fast.

## 1. Use React.memo for Component Memoization

```jsx
const ExpensiveComponent = React.memo(({ data }) => {
  // Component only re-renders when data changes
  return <div>{/* render logic */}</div>;
});
```

## 2. useMemo and useCallback Hooks

```jsx
const MemoizedComponent = () => {
  const expensiveValue = useMemo(() => {
    return computeExpensiveValue(data);
  }, [data]);

  const handleClick = useCallback(() => {
    doSomething(id);
  }, [id]);

  return <div>...</div>;
};
```

## 3. Code Splitting with React.lazy

```jsx
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyComponent />
    </Suspense>
  );
}
```

## 4. Virtual Scrolling for Long Lists

Use libraries like `react-window` for rendering large lists efficiently.

## 5. Optimize Bundle Size

- Use tree shaking
- Analyze bundle with webpack-bundle-analyzer
- Remove unused dependencies

## Measuring Performance

Always measure before and after optimization using React DevTools Profiler.

## Conclusion

Performance optimization is an ongoing process. Focus on the bottlenecks that matter most to your users.''',
            'tags': ['React', 'JavaScript', 'Performance', 'Frontend', 'Optimization'],
            'categories': ['Web Development', 'Frontend'],
            'status': 'published',
            'is_featured': True,
            'published_at': timezone.now() - timedelta(days=14),
        },
        {
            'title': 'Microservices Architecture with Django and Docker',
            'excerpt': 'How to design and implement a microservices architecture using Django, Docker, and Kubernetes.',
            'content': '''# Microservices Architecture with Django and Docker

Moving from monolith to microservices? Here's what you need to know.

## Why Microservices?

- **Scalability**: Scale services independently
- **Flexibility**: Use different tech stacks per service
- **Resilience**: Failure in one service doesn't bring down the entire system
- **Team autonomy**: Teams can work independently

## Architecture Overview

```
API Gateway (nginx)
    ├── User Service (Django)
    ├── Product Service (Django)
    ├── Order Service (Django)
    └── Payment Service (FastAPI)
```

## Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app"]
```

## Service Communication

Use REST APIs or message queues (RabbitMQ, Kafka) for inter-service communication.

## Database Per Service

Each microservice should have its own database to maintain independence.

## Challenges

- **Distributed transactions**: Use saga pattern
- **Service discovery**: Use Kubernetes or Consul
- **Monitoring**: Implement centralized logging and tracing

## Conclusion

Microservices aren't a silver bullet. Start with a modular monolith and extract services as needed.''',
            'tags': ['Microservices', 'Django', 'Docker', 'Kubernetes', 'Architecture'],
            'categories': ['Architecture', 'DevOps'],
            'status': 'published',
            'is_featured': False,
            'published_at': timezone.now() - timedelta(days=21),
        },
        {
            'title': 'Modern Authentication with JWT and Django',
            'excerpt': 'Implementing secure authentication in Django using JSON Web Tokens (JWT) and best security practices.',
            'content': '''# Modern Authentication with JWT and Django

Security is paramount. Here's how to implement robust authentication in Django.

## Why JWT?

- Stateless authentication
- Works great with SPAs and mobile apps
- Easy to scale horizontally

## Implementation

```python
from rest_framework_simplejwt.views import TokenObtainPairView

# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

## Security Best Practices

1. **Use HTTPS only**
2. **Store tokens securely** (httpOnly cookies)
3. **Implement token refresh** mechanism
4. **Add rate limiting** to prevent brute force
5. **Use strong password policies**

## Token Refresh Flow

```javascript
async function refreshToken() {
  const response = await fetch('/api/token/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh: refreshToken }),
  });
  const data = await response.json();
  return data.access;
}
```

## Protecting Routes

```python
from rest_framework.permissions import IsAuthenticated

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Authenticated!'})
```

## Conclusion

JWT provides a modern, scalable approach to authentication. Combine it with proper security practices for a robust solution.''',
            'tags': ['Authentication', 'JWT', 'Django', 'Security', 'REST API'],
            'categories': ['Security', 'Backend'],
            'status': 'published',
            'is_featured': False,
            'published_at': timezone.now() - timedelta(days=28),
        },
        {
            'title': 'AWS Deployment Guide for Django Applications',
            'excerpt': 'Step-by-step guide to deploying Django applications on AWS with best practices for production.',
            'content': '''# AWS Deployment Guide for Django Applications

Deploying to production can be daunting. Here's a comprehensive guide for AWS.

## Architecture

```
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
EC2 Auto Scaling Group
    ↓
RDS PostgreSQL + ElastiCache Redis
```

## Services Used

- **EC2**: Application servers
- **RDS**: Managed PostgreSQL
- **ElastiCache**: Redis for caching
- **S3**: Static and media files
- **CloudFront**: CDN for global distribution
- **Route 53**: DNS management

## Deployment Steps

### 1. Setup RDS Database

```bash
aws rds create-db-instance \
    --db-instance-identifier myapp-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password secret
```

### 2. Configure S3 for Static Files

```python
# settings.py
AWS_STORAGE_BUCKET_NAME = 'myapp-static'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### 3. Setup EC2 with User Data

```bash
#!/bin/bash
apt-get update
apt-get install -y python3-pip nginx
pip3 install gunicorn
# ... setup application
```

### 4. Configure Load Balancer

Create an Application Load Balancer and configure health checks.

## Monitoring

- Use CloudWatch for logs and metrics
- Setup alarms for critical metrics
- Implement APM with tools like New Relic

## Cost Optimization

- Use Reserved Instances for predictable workloads
- Implement auto-scaling
- Use S3 lifecycle policies

## Conclusion

AWS provides robust infrastructure for Django applications. Start small and scale as needed.''',
            'tags': ['AWS', 'Django', 'Deployment', 'DevOps', 'Cloud'],
            'categories': ['DevOps', 'Cloud'],
            'status': 'published',
            'is_featured': False,
            'published_at': timezone.now() - timedelta(days=35),
        },
        {
            'title': 'Testing Django Applications: A Comprehensive Guide',
            'excerpt': 'Learn how to write effective tests for Django applications including unit tests, integration tests, and end-to-end tests.',
            'content': '''# Testing Django Applications: A Comprehensive Guide

Testing is not optional—it's essential. Here's how to test Django apps effectively.

## Types of Tests

### 1. Unit Tests

```python
from django.test import TestCase

class ArticleModelTest(TestCase):
    def test_article_creation(self):
        article = Article.objects.create(
            title="Test Article",
            content="Test content"
        )
        self.assertEqual(article.title, "Test Article")
```

### 2. Integration Tests

```python
class ArticleAPITest(TestCase):
    def test_create_article(self):
        response = self.client.post('/api/articles/', {
            'title': 'New Article',
            'content': 'Content'
        })
        self.assertEqual(response.status_code, 201)
```

### 3. End-to-End Tests

Use Selenium or Playwright for browser automation.

## Best Practices

1. **Test behavior, not implementation**
2. **Use factories** (factory_boy) for test data
3. **Mock external services**
4. **Aim for high coverage** but focus on critical paths
5. **Run tests in CI/CD**

## Test Organization

```
tests/
    ├── test_models.py
    ├── test_views.py
    ├── test_serializers.py
    └── test_integration.py
```

## Fixtures and Factories

```python
import factory

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
    
    title = factory.Faker('sentence')
    content = factory.Faker('paragraph')
```

## Performance Testing

Use tools like Locust for load testing:

```python
from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def load_homepage(self):
        self.client.get("/")
```

## Conclusion

Comprehensive testing gives you confidence to ship features faster. Invest in your test suite—it pays dividends.''',
            'tags': ['Testing', 'Django', 'Python', 'Quality Assurance', 'Best Practices'],
            'categories': ['Testing', 'Backend'],
            'status': 'draft',
            'is_featured': False,
            'published_at': None,
        },
    ]
    
    for post_data in blog_posts_data:
        post, created = BlogPost.objects.get_or_create(
            site=site,
            title=post_data['title'],
            defaults=post_data
        )
        
        if created:
            print(f"  ✓ Added blog post: {post_data['title']}")
            
            # Add blog post featured image
            content_type = ContentType.objects.get_for_model(BlogPost)
            
            img = generate_placeholder_image(
                1200, 630,
                post_data['title'][:30],
                bg_color=(random.randint(60, 120), random.randint(100, 160), random.randint(140, 200))
            )
            media = Media.objects.create(
                content_type=content_type,
                object_id=post.id,
                image=img,
                alt=f"{post_data['title']} - Featured Image",
                caption=f"Featured image for {post_data['title']}",
                is_featured=True,
                order=1
            )
            print(f"    ✓ Added featured image")


def main():
    """Main seeding function"""
    print("\n🌱 Starting data seeding for limefolio...\n")
    
    # Seed user
    print("👤 Creating user...")
    user = seed_user('fardeen.es7')
    
    # Seed site
    print("\n🏠 Creating portfolio site...")
    site = seed_site(user)
    
    # Seed social links
    print("\n🔗 Adding social links...")
    seed_social_links(site)
    
    # Seed skills
    print("\n💪 Adding skills...")
    seed_skills(site)
    
    # Seed experiences
    print("\n💼 Adding work experiences...")
    seed_experiences(site)
    
    # Seed projects
    print("\n🚀 Adding projects (with images)...")
    seed_projects(site)
    
    # Seed blog posts
    print("\n📝 Adding blog posts (with images)...")
    seed_blog_posts(site)
    
    print("\n✅ Data seeding completed successfully!")
    print(f"\n📊 Summary:")
    print(f"   • User: {user.username}")
    print(f"   • Site: {site.subdomain}.limefolio.com")
    print(f"   • Social Links: {site.social_links.count()}")
    print(f"   • Skills: {site.skills.count()}")
    print(f"   • Experiences: {site.experiences.count()}")
    print(f"   • Projects: {site.projects.count()}")
    print(f"   • Blog Posts: {site.blog_posts.count()}")
    print(f"   • Media Files: {Media.objects.count()}")
    print(f"\n🎉 Portfolio is ready at: {site.subdomain}.limefolio.com\n")


if __name__ == '__main__':
    main()
