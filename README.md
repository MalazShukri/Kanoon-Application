# Kanoon Project

A Django-based authentication system using phone number verification.

## Features

- Phone number-based authentication
- JWT token authentication
- User profile management with:
  - Full name
  - Gender
  - Birth date
  - Profile photo

## Setup

1. Clone the repository
```bash
git clone <repository-url>
cd kanoon
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run migrations
```bash
python manage.py migrate
```

4. Run the development server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/request-verification/` - Request phone verification code
- `POST /api/auth/verify-phone/` - Verify phone number and get tokens
- `POST /api/auth/complete-profile/` - Complete user profile

## Tech Stack

- Django
- Django REST Framework
- Simple JWT
- SQLite (default database)
