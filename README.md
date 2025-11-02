# Discussion_Hub

A modern, real-time discussion platform built with Django, featuring WebSocket-powered notifications, nested comment threading, and a comprehensive RESTful API.

## Overview

Discussion Hub is a full-stack web application that enables users to create discussion posts, engage in nested comment threads, and receive real-time notifications. Built with scalability and performance in mind, it leverages WebSocket technology for instant upda

## Features

### Core Functionality
- **Create & Manage Discussions** - Users can start new discussion topics
- **Nested Comment Threading** - Unlimited depth reply system with visual hierarchy
- **Voting System** - Upvote/downvote comments with live score updates
- **Time-Limited Editing** - Edit or delete your own comments within a time window
- **User Authentication** - Secure session-based authentication system

### Real-Time Features
- **WebSocket Notifications** - Instant alerts for new comments and replies
- **Live Vote Updates** - Real-time vote count synchronization
- **Typing Indicators** - See when other users are composing replies

### Performance & Scalability
- **Redis Caching** - Optimized data retrieval for frequently accessed content
- **Database Indexing** - Efficient query performance for large datasets
- **Pagination** - Smooth browsing experience with paginated comment threads
- **Query Optimization** - Minimized N+1 queries using select_related/prefetch_related

### API
- **RESTful API** - Complete API for mobile/web integration
- **Mobile-Ready** - Responsive design optimized for all devices
- **Role-Based Permissions** - Granular access control for users

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 5.0+
- **Real-Time:** Django Channels, WebSockets
- **API:** Django REST Framework
- **Message Broker:** Redis
- **Database:** SQLite (Development) / PostgreSQL (Production-ready)
- **ASGI Server:** Daphne

### Frontend
- **Languages:** HTML5, CSS3, JavaScript (ES6+)
- **Styling:** Custom CSS with responsive design
- **Icons:** Font Awesome
- **AJAX:** Vanilla JavaScript (fetch API)

### DevOps
- **Caching:** Redis
- **Version Control:** Git
- **Deployment:** Docker-ready (optional)

## Architecture
```
┌─────────────┐      WebSocket       ┌──────────────┐
│   Browser   │◄────────────────────►│    Daphne    │
│  (Client)   │                      │ ASGI Server  │
└─────────────┘                      └──────┬───────┘
                                            │
                                            ▼
                                     ┌──────────────┐
                                     │    Django    │
                                     │   Channels   │
                                     └──────┬───────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                 ▼                 ▼
                    ┌──────────┐      ┌─────────┐      ┌─────────┐
                    │  Redis   │      │ Django  │      │Database │
                    │(Cache +  │      │  REST   │      │(SQLite) │
                    │Pub/Sub)  │      │Framework│      │         │
                    └──────────┘      └─────────┘      └─────────┘
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Redis Server
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Discussion_Hub.git
cd Discussion_Hub
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Redis

**Windows:**
```bash
# Using Chocolatey
choco install redis
```
Download from: https://github.com/microsoftarchive/redis/releases

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

### Step 5: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata comments/fixtures/pages.json
```

### Step 6: Verify Redis is Running
```bash
redis-cli ping
# Should return: PONG
```

## 🚀 Usage

### Running the Development Server

**Terminal 1: Start Redis**
```bash
redis-server
```

**Terminal 2: Start Django with WebSocket Support**
```bash
daphne -b 0.0.0.0 -p 8000 comment_system.asgi:application
```

Or use the convenience script (if using regular runserver without WebSockets):
```bash
python manage.py runserver
```

### Accessing the Application
- **Web Interface:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Root:** http://127.0.0.1:8000/api/

### Testing WebSocket Notifications
1. Open the application in two different browser windows
2. Login as different users in each window
3. Navigate to the same discussion page
4. Post a comment from one window
5. Observe real-time notification in the other window

## 📡 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication
- **Type:** Session-based authentication
- **Login:** Use Django's built-in login endpoint

### Endpoints

#### Pages/Discussions

**List all discussions**
```http
GET /api/pages/
```

**Get specific discussion**
```http
GET /api/pages/{id}/
```

**Get comments for a discussion**
```http
GET /api/pages/{id}/comments/
```

#### Comments

**List all comments**
```http
GET /api/comments/
```

**Query Parameters:**
- `page`: Page number for pagination
- `parent`: Filter by parent comment ID
- `page_id`: Filter by discussion page ID

**Create a comment**
```http
POST /api/comments/
Content-Type: application/json

{
  "page": 1,
  "parent": null,
  "content": "Your comment text"
}
```

**Get specific comment**
```http
GET /api/comments/{id}/
```

**Update comment**
```http
PATCH /api/comments/{id}/
Content-Type: application/json

{
  "content": "Updated comment text"
}
```

**Delete comment (soft delete)**
```http
DELETE /api/comments/{id}/
```

**Get replies to a comment**
```http
GET /api/comments/{id}/replies/
```

**Vote on a comment**
```http
POST /api/comments/{id}/vote/
Content-Type: application/json

{
  "vote_type": 1  // 1 for upvote, -1 for downvote
}
```

### Response Examples

**Success Response (Comment List):**
```json
{
  "count": 13,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "page": 1,
      "author": {
        "id": 2,
        "username": "john_doe",
        "date_joined": "2025-07-21T10:42:31.038861Z"
      },
      "parent": null,
      "content": "This is a great discussion!",
      "created_at": "2025-07-21T16:09:44.650495Z",
      "updated_at": "2025-07-21T16:09:44.650574Z",
      "is_deleted": false,
      "upvotes": 5,
      "downvotes": 1,
      "net_votes": 4,
      "user_vote": 1,
      "replies_count": 3
    }
  ]
}
```

## Project Structure
```
Discussion_Hub/
├── comment_system/           # Django project settings
│   ├── __init__.py
│   ├── asgi.py              # ASGI configuration for WebSockets
│   ├── settings.py          # Project settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration
│
├── comments/                # Main application
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   │   ├── comments/
│   │   │   ├── base.html
│   │   │   ├── homepage.html
│   │   │   ├── page_detail.html
│   │   │   └── comment_display.html
│   │   └── registration/
│   │       ├── login.html
│   │       └── signup.html
│   ├── static/              # CSS, JS, images
│   │   └── comments/
│   │       └── style.css
│   ├── fixtures/            # Sample data
│   │   └── pages.json
│   ├── admin.py             # Admin panel configuration
│   ├── apps.py              # App configuration
│   ├── consumers.py         # WebSocket consumers
│   ├── forms.py             # Django forms
│   ├── models.py            # Database models
│   ├── routing.py           # WebSocket URL routing
│   ├── serializers.py       # DRF serializers
│   ├── api_views.py         # API viewsets
│   ├── api_urls.py          # API URL patterns
│   ├── views.py             # View functions
│   └── urls.py              # App URL patterns
│
├── db.sqlite3               # SQLite database
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for PostgreSQL in production)
DB_NAME=discussion_hub
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### Settings Highlights

**Cache Configuration:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**Channel Layers (WebSocket):**
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Check WebSocket Connection
```bash
# In Python
import asyncio
import websockets

async def test():
    async with websockets.connect("ws://127.0.0.1:8000/ws/comments/1/") as ws:
        print("Connected!")

asyncio.run(test())
```

## 🚢 Deployment

### Production Checklist
- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up environment variables
- [ ] Configure static file serving
- [ ] Set up SSL/TLS certificates
- [ ] Use production ASGI server (Daphne with systemd)
- [ ] Configure Redis persistence
- [ ] Set up monitoring and logging

```



---

⭐ **If you found this project helpful, please consider giving it a star!** ⭐

Made with ❤️ using Django
