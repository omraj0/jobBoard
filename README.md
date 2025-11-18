Job Board API Backend
=====================

This repository contains the complete Django REST Framework backend for a modern, scalable job board platform. It's designed for easy deployment on [Render](https://render.com/) and provides a full-featured API for a React/Vue/Angular frontend.

The platform allows administrators and staff to post and manage job listings, while regular users can search, filter, and track their job applications (Clicked, Bookmarked, Applied).

🚀 Core Features
----------------

-   **Role-Based Access Control:** Granular permissions for different user types:

    -   **Superuser:** Full control over the entire platform. Can manage all users and all job postings.

    -   **Staff/Admin:** Can post new jobs. Can only edit or delete jobs they personally posted. Can manage all job tags.

    -   **Authenticated User:** Can search/filter jobs, view job details, and track their application status (Bookmark, Apply, Click, etc.).

-   **Job Interaction Tracking:** A `UserJobMapping` model tracks each user's relationship with a job (e.g., `Bookmarked`, `Applied`, `Clicked`), enabling personalized dashboards.

-   **Dedicated User Endpoints:** Users can fetch lists of their own bookmarked and applied jobs.

-   **Dynamic Tagging System:** Jobs can be categorized with multiple tags (e.g., "AI", "Web Development", "Remote"), which are automatically created when jobs are posted.

-   **Powerful Filtering & Search:** The jobs filter endpoint (`/api/jobs/filter/`) supports:

    -   Filtering by `job_type`, `location`, `company`, `title`, and `tags`.
    
    -   Time-based filtering: `last_6` hours, `last_24` hours, `this_week`, `this_month`, or `all`.

    -   Returns available filter options along with filtered results.

-   **Full User Authentication:** Complete auth flow including Signup, Login, Logout, Password Reset (via email), and user profile verification.

-   **Email-Based Authentication:** Custom authentication backend that allows users to login using their email address instead of username.

🧱 Tech Stack
-------------

-   **Backend:** Django 4.2
-   **API:** Django REST Framework
-   **Database:** PostgreSQL
-   **Authentication:** Token Authentication (DRF)
-   **Email Service:** Yagmail (for password reset)
-   **Deployment:** Render (for Backend & DB)
-   **WSGI Server:** Gunicorn
-   **Static Files:** Whitenoise
-   **CORS:** django-cors-headers

🏗️ Project Structure
---------------------

```
jobBoard/
│
├── jobBoardProject/        (Project config folder)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── jobBoard/               (App for authentication & user management)
│   ├── models.py         (TimestampedModel, UserManager, User)
│   ├── serializers.py    (UserSerializer, EmailAuthTokenSerializer)
│   ├── views.py          (Signup, Login, Logout, Check, ForgotPassword, ResetPassword)
│   ├── urls.py
│   └── backends.py       (EmailBackend for email-based authentication)
│
├── jobs/                   (App for job listings, tags, applications)
│   ├── models.py         (Job, Tag, UserJobMapping)
│   ├── serializers.py    (JobListSerializer, JobDetailSerializer, JobManagementSerializer, FilterSerializer)
│   ├── views.py          (JobListView, JobFilterView, JobDetailView, MyJobsView, JobManagement views)
│   ├── urls.py
│   ├── permissions.py    (CanManageJobs)
│   └── admin.py
│
├── build.sh               (Build script for deployment)
├── server.py              (Waitress server for local production testing)
├── render.yaml            (Render deployment configuration)
├── manage.py
├── README.md
└── requirements.txt

```

🧱 Models Overview
------------------

### 1. **User (CustomUser)**
Extends Django's `AbstractBaseUser` and `PermissionsMixin`  
Uses email as the primary identifier (USERNAME_FIELD)  
Includes fields:
- `email` (unique, required)
- `first_name`, `last_name`
- `secret_key` (auto-generated)
- `is_staff`, `is_active`, `is_superuser`
- `created_at`, `updated_at` (from TimestampedModel)

### 2. **Job**
Stores all company job listings with fields:
- `posted_by` → ForeignKey(User)
- `title` (indexed)
- `company` (indexed)
- `location` (indexed, nullable)
- `description` (nullable)
- `application_link` (URLField)
- `job_type` → Choices: Full-time, Part-time, Contract, Internship (indexed)
- `is_active` (indexed, default=True)
- `tags` → ManyToManyField(Tag)
- `created_at`, `updated_at` (from TimestampedModel)

Indexed fields for performance:  
`title`, `company`, `location`, `job_type`, `is_active`, `updated_at` (conditional index for active jobs)

### 3. **Tag**
Categorizes jobs with fields:
- `name` (unique)
- `slug` (auto-generated from name)
- `created_at`, `updated_at` (from TimestampedModel)

### 4. **UserJobMapping**
Maintains the relationship between **User** and **Job**.
- `user` → ForeignKey(User)
- `job` → ForeignKey(Job)
- `status` → Choice(`Clicked`, `Applied`, `Bookmarked`)
- `created_at`, `updated_at` (from TimestampedModel)
- Unique constraint on (`user`, `job`)

🔗 API Endpoints
----------------

### 🔒 Auth Routes (`/api/auth/`)
| Method | Endpoint | Description | Auth Required |
|--------|-----------|-------------|---------------|
| POST | `/api/auth/signup/` | Register new user | No |
| POST | `/api/auth/login/` | Login user, get authentication token | No |
| GET | `/api/auth/check/` | Get logged-in user details | Yes |
| GET | `/api/auth/logout/` | Logout and delete token | Yes |
| POST | `/api/auth/forgot-password/` | Request password reset email | No |
| POST | `/api/auth/reset-password/<uidb64>/<token>/` | Reset password with token | No |

**Request/Response Examples:**

**Signup:**
```json
POST /api/auth/signup/
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Login:**
```json
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "securepassword"
}

Response:
{
  "message": "Login successful",
  "token": "abc123...",
  "email": "user@example.com"
}
```

---

### 💼 Job Routes (`/api/jobs/`)
| Method | Endpoint | Description | Auth Required |
|--------|-----------|-------------|---------------|
| GET | `/api/jobs/` | List all active jobs with available filters | Yes |
| POST | `/api/jobs/filter/` | Filter jobs by multiple criteria | Yes |
| GET | `/api/jobs/<id>/` | Retrieve job details | Yes |
| POST | `/api/jobs/<id>/` | Mark job as Clicked/Applied/Bookmarked | Yes |
| GET | `/api/jobs/my-jobs/` | List all bookmarked/applied jobs by the user | Yes |
| GET | `/api/jobs/manage/` | List all jobs (for staff/superuser) | Yes (Staff/Superuser) |
| POST | `/api/jobs/manage/` | Create new job (for staff/superuser) | Yes (Staff/Superuser) |
| GET | `/api/jobs/manage/<id>/` | Get job details (for staff/superuser) | Yes (Staff/Superuser) |
| POST | `/api/jobs/manage/<id>/` | Update or delete job (for staff/superuser) | Yes (Staff/Superuser) |

**Request/Response Examples:**

**Filter Jobs:**
```json
POST /api/jobs/filter/
{
  "tags": ["python", "django"],
  "job_type": ["Full-time"],
  "location": ["Remote", "New York"],
  "company": ["Tech Corp"],
  "title": ["Developer"],
  "time": "this_week"
}

Response:
{
  "filters": {
    "tags": ["python", "django", "react", ...],
    "title": ["Developer", "Manager", ...],
    "company": ["Tech Corp", ...],
    "location": ["Remote", "New York", ...],
    "job_type": ["Full-time", "Part-time", ...],
    "time": ["last_6", "last_24", "this_week", "this_month", "all"]
  },
  "jobs": [...]
}
```

**Job Action (Click/Apply/Bookmark):**
```json
POST /api/jobs/<id>/
{
  "action": "Bookmarked"  // or "Applied" or "Clicked"
}
```

**Create Job (Staff/Superuser):**
```json
POST /api/jobs/manage/
{
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "Remote",
  "description": "We are looking for...",
  "application_link": "https://example.com/apply",
  "job_type": "Full-time",
  "tags": ["python", "django", "remote"]
}
```

**Update/Delete Job (Staff/Superuser):**
```json
POST /api/jobs/manage/<id>/
{
  "action": "delete"  // to delete, or omit for update
  // ... other job fields for update
}
```

---

⚙️ Local Setup & Installation
-----------------------------

1.  **Clone the Repository**

    ```bash
    git clone <your-repository-url>
    cd jobBoard
    ```

2.  **Create and Activate a Virtual Environment**

    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables** 

    Create a `.env` file in the root directory and add your local configuration:

    ```env
    SECRET_KEY=your-django-secret-key-here
    DEBUG=True
    ENVIRONMENT=development
    ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1

    # Database Configuration
    DATABASE_URL=postgresql://user:password@localhost:5432/jobboard_db

    # Email Configuration (for password reset)
    YAGMAIL_USER=your-email@gmail.com
    YAGMAIL_PASSWORD=your-app-password
    RESET_URL=http://localhost:3000/reset-password
    ```

    *Note: You must have PostgreSQL running on your machine. For local development, you can use SQLite by modifying `settings.py` or use a local PostgreSQL instance.*

5.  **Run Migrations**

    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser** 

    This account will have full admin privileges.

    ```bash
    python manage.py createsuperuser
    ```

    *(Follow the prompts to set email and password. Note: Use email instead of username)*

7.  **Run the Development Server**

    ```bash
    python manage.py runserver
    ```

    The API will be available at `http://127.0.0.1:8000/`.

8.  **Access Admin Panel**

    Visit `http://127.0.0.1:8000/admin/` to access the Django admin interface.

🌐 Deployment on Render
-----------------------

This project is configured for easy deployment on Render using `render.yaml`.

### Option 1: Using render.yaml (Recommended)

1.  **Push your code to GitHub** and connect it to Render.

2.  **Render will automatically detect `render.yaml`** and create the services:
    - A PostgreSQL database named `jobboard-db`
    - A web service named `jobboard`

3.  **Add Environment Variables** in the Render dashboard for your web service:
    - `SECRET_KEY`: Generate using `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
    - `DEBUG`: `False`
    - `ENVIRONMENT`: `production`
    - `ALLOWED_HOSTS`: Your Render service URL (e.g., `your-app.onrender.com`)
    - `YAGMAIL_USER`: Your Gmail address for sending password reset emails
    - `YAGMAIL_PASSWORD`: Your Gmail app password
    - `RESET_URL`: Your frontend URL for password reset (e.g., `https://your-frontend.com/reset-password`)

4.  **The build process** (defined in `build.sh`) will:
    - Install dependencies
    - Collect static files
    - Run migrations

### Option 2: Manual Setup

1.  **Create a PostgreSQL Database:**
    - On your Render dashboard, create a new "PostgreSQL" service.
    - Copy the **"Internal Connection URL"** (you'll use this for `DATABASE_URL`).

2.  **Create a Web Service:**
    - Create a new "Web Service" and connect it to your GitHub repository.
    - **Environment:** `Python 3.11`
    - **Region:** Choose a region close to your database.
    - **Build Command:** `./build.sh` or `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
    - **Start Command:** `gunicorn jobBoardProject.wsgi:application`

3.  **Add Environment Variables:** In the "Environment" tab for your Web Service, add:
    - `SECRET_KEY`: Generate a new secret key
    - `DATABASE_URL`: Paste the "Internal Connection URL" from your Render database
    - `DEBUG`: `False`
    - `ENVIRONMENT`: `production`
    - `ALLOWED_HOSTS`: Your Render service URL
    - `YAGMAIL_USER`: Your Gmail address
    - `YAGMAIL_PASSWORD`: Your Gmail app password
    - `RESET_URL`: Your frontend password reset URL

Deploy the service. Your API will be live!

🔐 Authentication
-----------------

This project uses **Token Authentication** from Django REST Framework. After successful login or signup, you'll receive a token that must be included in subsequent requests.

**How to use:**
- Include the token in the `Authorization` header:
  ```
  Authorization: Token <your-token-here>
  ```

**Example with curl:**
```bash
curl -H "Authorization: Token abc123..." http://localhost:8000/api/jobs/
```

**Example with JavaScript (fetch):**
```javascript
fetch('http://localhost:8000/api/jobs/', {
  headers: {
    'Authorization': 'Token abc123...',
    'Content-Type': 'application/json'
  }
})
```

📝 Notes
--------

- All endpoints require authentication except signup, login, forgot-password, and reset-password.
- Job management endpoints (`/api/jobs/manage/`) require staff or superuser privileges.
- Staff users can only edit/delete jobs they posted, while superusers can manage all jobs.
- Tags are automatically created when jobs are posted (case-insensitive, converted to lowercase).
- Password reset uses Django's built-in token generator and sends emails via Yagmail.
- CORS is configured for `localhost:3000` and `localhost:5173` (common frontend dev ports).
