# Freelance Marketplace - Product Requirements Document (PRD)

## 🎯 Project Overview

**Project Name:** Freelance Marketplace  
**Technology Stack:** Python 3.11+ | Django 5.0 | MySQL 8.0  
**Target Agent:** Claude Opus 4.5 via Cursor IDE  
**Version:** 1.0  
**Last Updated:** January 2025

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Project Structure](#3-project-structure)
4. [Database Design](#4-database-design)
5. [API Endpoints](#5-api-endpoints)
6. [Core Modules](#6-core-modules)
7. [Authentication System](#7-authentication-system)
8. [Frontend Templates](#8-frontend-templates)
9. [Real-time Features](#9-real-time-features)
10. [Payment Integration](#10-payment-integration)
11. [Testing Strategy](#11-testing-strategy)
12. [Deployment Configuration](#12-deployment-configuration)
13. [Development Guidelines](#13-development-guidelines)
14. [Implementation Checklist](#14-implementation-checklist)

---

## 1. Executive Summary

### 1.1 Purpose
Build a full-featured freelance marketplace web application where:
- **Freelancers** can create profiles, showcase skills, and bid on projects
- **Clients** can post projects, review proposals, and hire talent
- **Administrators** can manage users, resolve disputes, and monitor platform activity

### 1.2 Key Features
- User authentication (Email + OAuth)
- Project posting and bidding system
- Real-time messaging (Django Channels)
- Escrow-based payment system (Stripe)
- Review and rating system
- Admin dashboard with analytics

### 1.3 Technical Requirements
```
Python >= 3.11
Django >= 5.0
MySQL >= 8.0
Redis >= 7.0 (for Channels & Celery)
Node.js >= 18 (for frontend build tools)
```

---

## 2. System Architecture

### 2.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Browser   │  │  Mobile Web │  │  Admin Panel│             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Django Application                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │  Views   │ │   APIs   │ │ Channels │ │  Celery  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    MySQL    │  │    Redis    │  │  S3/Cloud   │             │
│  │  (Primary)  │  │   (Cache)   │  │  (Storage)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack Details

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend Framework | Django 5.0 | Web application framework |
| API | Django REST Framework | RESTful API endpoints |
| Database | MySQL 8.0 | Primary data storage |
| ORM | Django ORM | Database abstraction |
| Cache | Redis 7.0 | Session & query caching |
| Task Queue | Celery 5.3 | Background job processing |
| WebSocket | Django Channels 4.0 | Real-time messaging |
| Authentication | django-allauth | OAuth & email auth |
| Payment | Stripe API | Payment processing |
| Storage | django-storages + S3 | File uploads |
| Email | Django Email + Celery | Async email delivery |

---

## 3. Project Structure

### 3.1 Directory Structure
```
freelance_marketplace/
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
│
├── config/                          # Project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base settings
│   │   ├── development.py          # Dev settings
│   │   ├── production.py           # Prod settings
│   │   └── testing.py              # Test settings
│   ├── urls.py                     # Root URL configuration
│   ├── asgi.py                     # ASGI config (Channels)
│   ├── wsgi.py                     # WSGI config
│   └── celery.py                   # Celery configuration
│
├── apps/                            # Django applications
│   ├── __init__.py
│   │
│   ├── accounts/                   # User management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── managers.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_api.py
│   │   ├── templates/
│   │   │   └── accounts/
│   │   │       ├── login.html
│   │   │       ├── register.html
│   │   │       ├── profile.html
│   │   │       └── ...
│   │   └── migrations/
│   │
│   ├── projects/                   # Project management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── filters.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── templates/
│   │   │   └── projects/
│   │   └── migrations/
│   │
│   ├── proposals/                  # Bidding system
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── templates/
│   │   │   └── proposals/
│   │   └── migrations/
│   │
│   ├── contracts/                  # Contract management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── templates/
│   │   │   └── contracts/
│   │   └── migrations/
│   │
│   ├── messaging/                  # Real-time chat
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── consumers.py            # WebSocket consumers
│   │   ├── routing.py              # WebSocket routing
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── templates/
│   │   │   └── messaging/
│   │   └── migrations/
│   │
│   ├── payments/                   # Payment processing
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py             # Stripe integration
│   │   ├── webhooks.py             # Stripe webhooks
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── templates/
│   │   │   └── payments/
│   │   └── migrations/
│   │
│   ├── reviews/                    # Review & rating system
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tests/
│   │   ├── templates/
│   │   │   └── reviews/
│   │   └── migrations/
│   │
│   ├── notifications/              # Notification system
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── consumers.py
│   │   ├── routing.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── admin_dashboard/            # Admin panel
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── templates/
│   │   │   └── admin_dashboard/
│   │   └── migrations/
│   │
│   └── core/                       # Shared utilities
│       ├── __init__.py
│       ├── models.py               # Abstract base models
│       ├── mixins.py               # View mixins
│       ├── permissions.py          # DRF permissions
│       ├── pagination.py           # Custom pagination
│       ├── exceptions.py           # Custom exceptions
│       ├── utils.py                # Helper functions
│       └── validators.py           # Custom validators
│
├── static/                         # Static files
│   ├── css/
│   │   ├── main.css
│   │   └── components/
│   ├── js/
│   │   ├── main.js
│   │   ├── websocket.js
│   │   └── components/
│   ├── images/
│   └── vendor/
│
├── templates/                      # Global templates
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   ├── includes/
│   │   ├── messages.html
│   │   ├── pagination.html
│   │   └── modals.html
│   ├── emails/
│   │   ├── base_email.html
│   │   ├── welcome.html
│   │   ├── verification.html
│   │   └── notification.html
│   └── errors/
│       ├── 404.html
│       ├── 500.html
│       └── 403.html
│
├── media/                          # User uploads (dev only)
│
├── logs/                           # Application logs
│
└── scripts/                        # Utility scripts
    ├── seed_data.py
    ├── create_superuser.py
    └── cleanup.py
```

### 3.2 Requirements Files

#### requirements.txt
```txt
# Django Core
Django>=5.0,<5.1
django-environ>=0.11.2
django-extensions>=3.2.3

# Database
mysqlclient>=2.2.0
django-mysql>=4.12.0

# REST API
djangorestframework>=3.14.0
django-filter>=23.5
django-cors-headers>=4.3.1
drf-spectacular>=0.27.0

# Authentication
django-allauth>=0.60.0
djangorestframework-simplejwt>=5.3.1

# Real-time
channels>=4.0.0
channels-redis>=4.2.0
daphne>=4.0.0

# Background Tasks
celery>=5.3.4
redis>=5.0.1
django-celery-beat>=2.5.0
django-celery-results>=2.5.1

# Storage & Media
Pillow>=10.1.0
django-storages>=1.14.2
boto3>=1.34.0

# Payment
stripe>=7.8.0

# Security
django-ratelimit>=4.1.0
django-csp>=3.8

# Utilities
python-slugify>=8.0.1
django-crispy-forms>=2.1
crispy-bootstrap5>=2023.10
django-htmx>=1.17.2

# Production
gunicorn>=21.2.0
whitenoise>=6.6.0
sentry-sdk>=1.38.0
```

#### requirements-dev.txt
```txt
-r requirements.txt

# Testing
pytest>=7.4.3
pytest-django>=4.7.0
pytest-cov>=4.1.0
factory-boy>=3.3.0
faker>=22.0.0

# Code Quality
black>=23.12.1
isort>=5.13.2
flake8>=6.1.0
mypy>=1.8.0
django-stubs>=4.2.7

# Debug
django-debug-toolbar>=4.2.0
ipython>=8.19.0
```

---

## 4. Database Design

### 4.1 Entity Relationship Overview

> **Reference:** See `Freelance_Marketplace_ER_Diagram.docx` for visual diagram

### 4.2 Models Definition

#### 4.2.1 Core Abstract Models (`apps/core/models.py`)
```python
from django.db import models
import uuid

class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model with UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """Combined abstract base model."""
    class Meta:
        abstract = True
```

#### 4.2.2 User Models (`apps/accounts/models.py`)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel, TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    """Custom user model."""
    
    class Role(models.TextChoices):
        FREELANCER = 'freelancer', 'Freelancer'
        CLIENT = 'client', 'Client'
        ADMIN = 'admin', 'Admin'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]


class FreelancerProfile(BaseModel):
    """Extended profile for freelancers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    title = models.CharField(max_length=100)
    bio = models.TextField(max_length=2000)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    skills = models.JSONField(default=list)  # ["Python", "Django", "React"]
    experience_years = models.PositiveIntegerField(default=0)
    portfolio_url = models.URLField(blank=True)
    availability = models.CharField(max_length=50, default='available')
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    completed_projects = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'freelancer_profiles'


class ClientProfile(BaseModel):
    """Extended profile for clients."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=200, blank=True)
    company_website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    projects_posted = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'client_profiles'


class Skill(BaseModel):
    """Skill tags for categorization."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'skills'
```

#### 4.2.3 Project Models (`apps/projects/models.py`)
```python
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User

class Category(BaseModel):
    """Project categories."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'


class Project(BaseModel):
    """Project listings."""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        UNDER_REVIEW = 'under_review', 'Under Review'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        DISPUTED = 'disputed', 'Disputed'
    
    class BudgetType(models.TextChoices):
        FIXED = 'fixed', 'Fixed Price'
        HOURLY = 'hourly', 'Hourly Rate'
        MILESTONE = 'milestone', 'Milestone Based'
    
    class ExperienceLevel(models.TextChoices):
        ENTRY = 'entry', 'Entry Level'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        EXPERT = 'expert', 'Expert'
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    skills_required = models.JSONField(default=list)
    
    budget_type = models.CharField(max_length=20, choices=BudgetType.choices)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)
    
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices)
    estimated_duration = models.CharField(max_length=50)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    deadline = models.DateField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    views_count = models.PositiveIntegerField(default=0)
    proposals_count = models.PositiveIntegerField(default=0)
    
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['-created_at']),
        ]


class ProjectAttachment(BaseModel):
    """File attachments for projects."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='project_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'project_attachments'
```

#### 4.2.4 Proposal Models (`apps/proposals/models.py`)
```python
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.projects.models import Project

class Proposal(BaseModel):
    """Freelancer proposals/bids on projects."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    
    cover_letter = models.TextField()
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.CharField(max_length=50)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'proposals'
        unique_together = ['project', 'freelancer']
        ordering = ['-created_at']


class ProposalAttachment(BaseModel):
    """Sample work attachments for proposals."""
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='proposal_attachments/')
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'proposal_attachments'
```

#### 4.2.5 Contract Models (`apps/contracts/models.py`)
```python
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.projects.models import Project
from apps.proposals.models import Proposal

class Contract(BaseModel):
    """Contracts created from accepted proposals."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        DISPUTED = 'disputed', 'Disputed'
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='contract')
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='contract')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_contracts')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='freelancer_contracts')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    terms_accepted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']


class Milestone(BaseModel):
    """Contract milestones."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        SUBMITTED = 'submitted', 'Submitted'
        REVISION_REQUESTED = 'revision', 'Revision Requested'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    order = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'milestones'
        ordering = ['order']


class Deliverable(BaseModel):
    """Work deliverables for milestones."""
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='deliverables')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='deliverables/')
    
    class Meta:
        db_table = 'deliverables'
```

#### 4.2.6 Messaging Models (`apps/messaging/models.py`)
```python
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.contracts.models import Contract

class Conversation(BaseModel):
    """Chat conversations between users."""
    participants = models.ManyToManyField(User, related_name='conversations')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'conversations'


class Message(BaseModel):
    """Individual chat messages."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']


class MessageAttachment(BaseModel):
    """File attachments for messages."""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'message_attachments'
```

#### 4.2.7 Payment Models (`apps/payments/models.py`)
```python
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.contracts.models import Contract, Milestone

class EscrowAccount(BaseModel):
    """Escrow account for contracts."""
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='escrow')
    total_funded = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_released = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'escrow_accounts'


class Transaction(BaseModel):
    """Payment transactions."""
    
    class Type(models.TextChoices):
        ESCROW_FUND = 'escrow_fund', 'Escrow Funding'
        MILESTONE_RELEASE = 'milestone_release', 'Milestone Release'
        WITHDRAWAL = 'withdrawal', 'Withdrawal'
        REFUND = 'refund', 'Refund'
        PLATFORM_FEE = 'platform_fee', 'Platform Fee'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, related_name='transactions')
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, related_name='transactions')
    
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_transfer_id = models.CharField(max_length=100, blank=True)
    
    description = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']


class FreelancerWallet(BaseModel):
    """Freelancer earnings wallet."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    stripe_account_id = models.CharField(max_length=100, blank=True)
    stripe_account_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'freelancer_wallets'


class WithdrawalRequest(BaseModel):
    """Freelancer withdrawal requests."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'
    
    wallet = models.ForeignKey(FreelancerWallet, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'withdrawal_requests'
```

#### 4.2.8 Review Models (`apps/reviews/models.py`)
```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel
from apps.accounts.models import User
from apps.contracts.models import Contract

class Review(BaseModel):
    """Reviews after project completion."""
    
    class Type(models.TextChoices):
        CLIENT_TO_FREELANCER = 'client_to_freelancer', 'Client to Freelancer'
        FREELANCER_TO_CLIENT = 'freelancer_to_client', 'Freelancer to Client'
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    
    type = models.CharField(max_length=25, choices=Type.choices)
    
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Category ratings (for client reviewing freelancer)
    quality_rating = models.PositiveIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.PositiveIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    timeliness_rating = models.PositiveIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism_rating = models.PositiveIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Category ratings (for freelancer reviewing client)
    clarity_rating = models.PositiveIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    payment_rating = models.PositiveIntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    comment = models.TextField()
    
    is_visible = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'reviews'
        unique_together = ['contract', 'reviewer']
```

#### 4.2.9 Notification Models (`apps/notifications/models.py`)
```python
from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User

class Notification(BaseModel):
    """User notifications."""
    
    class Type(models.TextChoices):
        NEW_PROPOSAL = 'new_proposal', 'New Proposal'
        PROPOSAL_ACCEPTED = 'proposal_accepted', 'Proposal Accepted'
        PROPOSAL_REJECTED = 'proposal_rejected', 'Proposal Rejected'
        NEW_MESSAGE = 'new_message', 'New Message'
        MILESTONE_APPROVED = 'milestone_approved', 'Milestone Approved'
        PAYMENT_RECEIVED = 'payment_received', 'Payment Received'
        REVIEW_RECEIVED = 'review_received', 'Review Received'
        CONTRACT_STARTED = 'contract_started', 'Contract Started'
        CONTRACT_COMPLETED = 'contract_completed', 'Contract Completed'
        DISPUTE_OPENED = 'dispute_opened', 'Dispute Opened'
        DISPUTE_RESOLVED = 'dispute_resolved', 'Dispute Resolved'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    action_url = models.CharField(max_length=255, blank=True)
    
    # Generic relation fields for linking to related objects
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
```

---

## 5. API Endpoints

### 5.1 URL Configuration

#### Root URLs (`config/urls.py`)
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.accounts.urls.api')),
        path('projects/', include('apps.projects.urls.api')),
        path('proposals/', include('apps.proposals.urls.api')),
        path('contracts/', include('apps.contracts.urls.api')),
        path('messages/', include('apps.messaging.urls.api')),
        path('payments/', include('apps.payments.urls.api')),
        path('reviews/', include('apps.reviews.urls.api')),
        path('notifications/', include('apps.notifications.urls.api')),
    ])),
    
    # Web Views
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls.web')),
    path('projects/', include('apps.projects.urls.web')),
    path('dashboard/', include('apps.admin_dashboard.urls')),
    
    # Django Allauth
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
```

### 5.2 API Endpoint Reference

#### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | User registration |
| POST | `/api/v1/auth/login/` | Login (JWT) |
| POST | `/api/v1/auth/logout/` | Logout |
| POST | `/api/v1/auth/token/refresh/` | Refresh JWT token |
| POST | `/api/v1/auth/password/reset/` | Request password reset |
| POST | `/api/v1/auth/password/reset/confirm/` | Confirm password reset |
| GET | `/api/v1/auth/user/` | Get current user |
| PATCH | `/api/v1/auth/user/` | Update current user |
| GET | `/api/v1/auth/profile/` | Get user profile |
| PUT | `/api/v1/auth/profile/` | Update user profile |

#### Project Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/` | List projects (with filters) |
| POST | `/api/v1/projects/` | Create project |
| GET | `/api/v1/projects/{id}/` | Get project detail |
| PUT | `/api/v1/projects/{id}/` | Update project |
| DELETE | `/api/v1/projects/{id}/` | Delete project |
| POST | `/api/v1/projects/{id}/publish/` | Publish project |
| GET | `/api/v1/projects/{id}/proposals/` | List project proposals |
| GET | `/api/v1/projects/categories/` | List categories |
| GET | `/api/v1/projects/my-projects/` | List user's projects |

#### Proposal Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/proposals/` | Submit proposal |
| GET | `/api/v1/proposals/{id}/` | Get proposal detail |
| PUT | `/api/v1/proposals/{id}/` | Update proposal |
| DELETE | `/api/v1/proposals/{id}/` | Withdraw proposal |
| POST | `/api/v1/proposals/{id}/accept/` | Accept proposal |
| POST | `/api/v1/proposals/{id}/reject/` | Reject proposal |
| GET | `/api/v1/proposals/my-proposals/` | List user's proposals |

#### Contract Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/contracts/` | List contracts |
| GET | `/api/v1/contracts/{id}/` | Get contract detail |
| POST | `/api/v1/contracts/{id}/milestones/` | Add milestone |
| PUT | `/api/v1/contracts/milestones/{id}/` | Update milestone |
| POST | `/api/v1/contracts/milestones/{id}/submit/` | Submit milestone |
| POST | `/api/v1/contracts/milestones/{id}/approve/` | Approve milestone |
| POST | `/api/v1/contracts/milestones/{id}/request-revision/` | Request revision |
| POST | `/api/v1/contracts/{id}/complete/` | Complete contract |

#### Messaging Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/messages/conversations/` | List conversations |
| POST | `/api/v1/messages/conversations/` | Start conversation |
| GET | `/api/v1/messages/conversations/{id}/` | Get conversation |
| GET | `/api/v1/messages/conversations/{id}/messages/` | Get messages |
| POST | `/api/v1/messages/conversations/{id}/messages/` | Send message |
| POST | `/api/v1/messages/{id}/read/` | Mark as read |

#### Payment Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/fund-escrow/` | Fund escrow |
| POST | `/api/v1/payments/release-milestone/` | Release milestone payment |
| GET | `/api/v1/payments/transactions/` | List transactions |
| GET | `/api/v1/payments/wallet/` | Get wallet balance |
| POST | `/api/v1/payments/withdraw/` | Request withdrawal |
| POST | `/api/v1/payments/webhook/stripe/` | Stripe webhook |

#### Review Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reviews/` | Submit review |
| GET | `/api/v1/reviews/user/{id}/` | Get user reviews |
| GET | `/api/v1/reviews/contract/{id}/` | Get contract reviews |

#### Notification Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | List notifications |
| POST | `/api/v1/notifications/{id}/read/` | Mark as read |
| POST | `/api/v1/notifications/read-all/` | Mark all as read |
| GET | `/api/v1/notifications/unread-count/` | Get unread count |

---

## 6. Core Modules

### 6.1 Permissions (`apps/core/permissions.py`)
```python
from rest_framework import permissions

class IsFreelancer(permissions.BasePermission):
    """Allow access only to freelancers."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'freelancer'


class IsClient(permissions.BasePermission):
    """Allow access only to clients."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'


class IsProjectOwner(permissions.BasePermission):
    """Allow access only to project owner."""
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class IsProposalOwner(permissions.BasePermission):
    """Allow access only to proposal owner."""
    def has_object_permission(self, request, view, obj):
        return obj.freelancer == request.user


class IsContractParticipant(permissions.BasePermission):
    """Allow access to contract participants."""
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.client, obj.freelancer]
```

### 6.2 Pagination (`apps/core/pagination.py`)
```python
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### 6.3 View Mixins (`apps/core/mixins.py`)
```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class FreelancerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin requiring freelancer role."""
    def test_func(self):
        return self.request.user.role == 'freelancer'


class ClientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin requiring client role."""
    def test_func(self):
        return self.request.user.role == 'client'


class ProfileCompleteMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin requiring completed profile."""
    def test_func(self):
        return self.request.user.is_profile_complete
```

---

## 7. Authentication System

### 7.1 JWT Configuration
```python
# config/settings/base.py

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
```

### 7.2 OAuth Configuration
```python
# config/settings/base.py

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'github': {
        'SCOPE': ['user:email'],
    },
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

### 7.3 Auth Views (`apps/accounts/api_views.py`)
```python
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    FreelancerProfileSerializer,
    ClientProfileSerializer,
)

class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send verification email
        from .tasks import send_verification_email
        send_verification_email.delay(user.id)
        
        return Response({
            'message': 'Registration successful. Please verify your email.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.user.role == 'freelancer':
            return FreelancerProfileSerializer
        return ClientProfileSerializer
    
    def get_object(self):
        user = self.request.user
        if user.role == 'freelancer':
            return user.freelancer_profile
        return user.client_profile
```

---

## 8. Frontend Templates

### 8.1 Base Template (`templates/base.html`)
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Freelance Marketplace{% endblock %}</title>
    
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'navbar.html' %}
    
    <main class="container my-4">
        {% include 'includes/messages.html' %}
        {% block content %}{% endblock %}
    </main>
    
    {% include 'footer.html' %}
    
    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 8.2 Key Template Files
```
templates/
├── base.html                    # Base layout
├── navbar.html                  # Navigation bar
├── footer.html                  # Footer
├── includes/
│   ├── messages.html           # Flash messages
│   └── pagination.html         # Pagination component
│
├── accounts/
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── dashboard.html
│   └── settings.html
│
├── projects/
│   ├── list.html               # Project listing
│   ├── detail.html             # Project detail
│   ├── create.html             # Create project form
│   └── edit.html               # Edit project
│
├── proposals/
│   ├── submit.html             # Submit proposal
│   ├── list.html               # Proposal list
│   └── detail.html             # Proposal detail
│
├── contracts/
│   ├── detail.html             # Contract detail
│   ├── milestones.html         # Milestone management
│   └── workspace.html          # Contract workspace
│
├── messaging/
│   ├── inbox.html              # Conversations list
│   └── conversation.html       # Chat interface
│
└── payments/
    ├── checkout.html           # Payment checkout
    ├── wallet.html             # Wallet overview
    └── transactions.html       # Transaction history
```

---

## 9. Real-time Features

### 9.1 Django Channels Configuration

#### ASGI Config (`config/asgi.py`)
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django_asgi_app = get_asgi_application()

from apps.messaging.routing import websocket_urlpatterns as messaging_ws
from apps.notifications.routing import websocket_urlpatterns as notification_ws

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            messaging_ws + notification_ws
        )
    ),
})
```

#### WebSocket Routing (`apps/messaging/routing.py`)
```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>[0-9a-f-]+)/$', consumers.ChatConsumer.as_asgi()),
]
```

#### Chat Consumer (`apps/messaging/consumers.py`)
```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Verify user is participant
        if not await self.is_participant():
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            message = await self.save_message(data['message'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': str(self.scope['user'].id),
                    'is_typing': data['is_typing'],
                }
            )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
        }))
    
    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'is_typing': event['is_typing'],
        }))
    
    @database_sync_to_async
    def is_participant(self):
        conversation = Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.scope['user']
        ).exists()
        return conversation
    
    @database_sync_to_async
    def save_message(self, content):
        message = Message.objects.create(
            conversation_id=self.conversation_id,
            sender=self.scope['user'],
            content=content
        )
        return {
            'id': str(message.id),
            'content': message.content,
            'sender_id': str(message.sender.id),
            'sender_name': message.sender.get_full_name(),
            'created_at': message.created_at.isoformat(),
        }
```

---

## 10. Payment Integration

### 10.1 Stripe Service (`apps/payments/services.py`)
```python
import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

PLATFORM_FEE_PERCENT = Decimal('10.00')  # 10% platform fee

class StripeService:
    @staticmethod
    def create_payment_intent(amount: Decimal, metadata: dict = None):
        """Create a Stripe PaymentIntent for escrow funding."""
        return stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            metadata=metadata or {},
        )
    
    @staticmethod
    def create_connected_account(user):
        """Create a Stripe Connect account for freelancer."""
        account = stripe.Account.create(
            type='express',
            country='US',
            email=user.email,
            capabilities={
                'transfers': {'requested': True},
            },
        )
        return account
    
    @staticmethod
    def create_account_link(account_id: str, refresh_url: str, return_url: str):
        """Create an account link for Stripe Connect onboarding."""
        return stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )
    
    @staticmethod
    def transfer_to_connected_account(amount: Decimal, account_id: str, metadata: dict = None):
        """Transfer funds to freelancer's connected account."""
        return stripe.Transfer.create(
            amount=int(amount * 100),
            currency='usd',
            destination=account_id,
            metadata=metadata or {},
        )
    
    @staticmethod
    def calculate_platform_fee(amount: Decimal) -> Decimal:
        """Calculate platform fee."""
        return (amount * PLATFORM_FEE_PERCENT / 100).quantize(Decimal('0.01'))
```

### 10.2 Webhook Handler (`apps/payments/webhooks.py`)
```python
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle events
    if event['type'] == 'payment_intent.succeeded':
        handle_payment_success(event['data']['object'])
    elif event['type'] == 'transfer.created':
        handle_transfer_created(event['data']['object'])
    elif event['type'] == 'account.updated':
        handle_account_updated(event['data']['object'])
    
    return HttpResponse(status=200)


def handle_payment_success(payment_intent):
    """Handle successful payment."""
    from .models import Transaction, EscrowAccount
    from apps.contracts.models import Contract
    
    contract_id = payment_intent.metadata.get('contract_id')
    if contract_id:
        contract = Contract.objects.get(id=contract_id)
        escrow = contract.escrow
        amount = Decimal(payment_intent.amount) / 100
        
        escrow.total_funded += amount
        escrow.balance += amount
        escrow.save()
        
        Transaction.objects.create(
            user=contract.client,
            contract=contract,
            type=Transaction.Type.ESCROW_FUND,
            amount=amount,
            net_amount=amount,
            status=Transaction.Status.COMPLETED,
            stripe_payment_intent_id=payment_intent.id,
        )
```

---

## 11. Testing Strategy

### 11.1 Test Configuration (`config/settings/testing.py`)
```python
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

### 11.2 Factory Setup (`apps/accounts/tests/factories.py`)
```python
import factory
from faker import Faker
from apps.accounts.models import User, FreelancerProfile, ClientProfile

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_verified = True
    is_profile_complete = True


class FreelancerFactory(UserFactory):
    role = 'freelancer'
    
    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if create:
            FreelancerProfileFactory(user=self, **kwargs)


class ClientFactory(UserFactory):
    role = 'client'
    
    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if create:
            ClientProfileFactory(user=self, **kwargs)


class FreelancerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FreelancerProfile
    
    user = factory.SubFactory(FreelancerFactory)
    title = factory.LazyAttribute(lambda _: fake.job())
    bio = factory.LazyAttribute(lambda _: fake.paragraph())
    hourly_rate = factory.LazyAttribute(lambda _: fake.pydecimal(min_value=25, max_value=200, right_digits=2))
    skills = ['Python', 'Django', 'JavaScript']
```

### 11.3 Test Examples
```python
# apps/projects/tests/test_api.py
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.tests.factories import ClientFactory, FreelancerFactory
from apps.projects.tests.factories import ProjectFactory

@pytest.mark.django_db
class TestProjectAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = ClientFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_create_project(self):
        data = {
            'title': 'Test Project',
            'description': 'Test description',
            'budget_type': 'fixed',
            'budget_min': '500.00',
            'budget_max': '1000.00',
            'experience_level': 'intermediate',
            'estimated_duration': '1-2 weeks',
            'category_id': str(CategoryFactory().id),
        }
        response = self.client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
    
    def test_list_projects(self):
        ProjectFactory.create_batch(5, status='open')
        response = self.client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
    
    def test_filter_projects_by_category(self):
        category = CategoryFactory()
        ProjectFactory.create_batch(3, category=category, status='open')
        ProjectFactory.create_batch(2, status='open')
        
        response = self.client.get(f'/api/v1/projects/?category={category.id}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
```

---

## 12. Deployment Configuration

### 12.1 Docker Configuration

#### Dockerfile
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=0
      - DATABASE_URL=mysql://user:password@db:3306/freelance_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=freelance_db
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
      - MYSQL_ROOT_PASSWORD=rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine

  celery:
    build: .
    command: celery -A config worker -l info
    environment:
      - DATABASE_URL=mysql://user:password@db:3306/freelance_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A config beat -l info
    environment:
      - DATABASE_URL=mysql://user:password@db:3306/freelance_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  mysql_data:
  static_volume:
  media_volume:
```

### 12.2 Environment Variables (`.env.example`)
```env
# Django
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=mysql://user:password@localhost:3306/freelance_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_STORAGE_BUCKET_NAME=xxx
AWS_S3_REGION_NAME=us-east-1
```

---

## 13. Development Guidelines

### 13.1 Code Style
- Follow PEP 8 standards
- Use Black for code formatting (line length: 100)
- Use isort for import sorting
- Type hints for all function signatures
- Docstrings for all classes and public methods

### 13.2 Git Workflow
```bash
# Branch naming
feature/feature-name
bugfix/bug-description
hotfix/critical-fix

# Commit messages
feat: add user registration endpoint
fix: resolve payment webhook issue
docs: update API documentation
test: add contract model tests
refactor: optimize database queries
```

### 13.3 API Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "errors": null
}
```

### 13.4 Error Response Format
```json
{
  "success": false,
  "data": null,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

---

## 14. Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup and configuration
- [ ] Database models implementation
- [ ] User authentication (registration, login, JWT)
- [ ] OAuth integration (Google, GitHub)
- [ ] Email verification system
- [ ] Basic templates and static files

### Phase 2: Core Features (Week 3-4)
- [ ] User profiles (Freelancer/Client)
- [ ] Project CRUD operations
- [ ] Category and skill management
- [ ] Project search and filtering
- [ ] Proposal submission system
- [ ] Proposal management (accept/reject)

### Phase 3: Contract & Messaging (Week 5-6)
- [ ] Contract creation from proposals
- [ ] Milestone management
- [ ] Deliverable uploads
- [ ] Real-time messaging (WebSocket)
- [ ] Conversation management
- [ ] File sharing in messages

### Phase 4: Payments (Week 7-8)
- [ ] Stripe integration setup
- [ ] Escrow funding system
- [ ] Milestone payment release
- [ ] Freelancer wallet
- [ ] Withdrawal requests
- [ ] Transaction history
- [ ] Stripe webhooks

### Phase 5: Reviews & Admin (Week 9)
- [ ] Review submission system
- [ ] Rating calculations
- [ ] Admin dashboard
- [ ] User management
- [ ] Dispute resolution
- [ ] Analytics and reports

### Phase 6: Polish & Deploy (Week 10)
- [ ] Notification system
- [ ] Email notifications
- [ ] Testing (unit, integration)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation
- [ ] Deployment

---

## 📚 Additional Resources

- **ER Diagram:** `Freelance_Marketplace_ER_Diagram.docx`
- **DFD Diagram:** `Freelance_Marketplace_DFD_Diagram.docx`
- **Database Schema:** `Freelance_Marketplace_DB_Schema.docx`
- **SRS Document:** `Freelance_Marketplace_SRS.docx`
- **Workflow Diagrams:** `Freelance_Marketplace_Workflow_Diagrams.html`

---

*This PRD is designed for Claude Opus 4.5 coding agent to develop the complete Freelance Marketplace application using Cursor IDE. Follow the implementation checklist and refer to the supporting documents for visual references.*
