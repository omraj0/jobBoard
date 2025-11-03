Job Board API Backend
=====================

This repository contains the complete Django REST Framework backend for a modern, scalable job board platform. It's designed for easy deployment on [Render](https://render.com/ "null") and provides a full-featured API for a React/Vue/Angular frontend.

The platform allows administrators and staff to post and manage job listings, while regular users can search, filter, and track their job applications (Clicked, Bookmarked, Applied).

🚀 Core Features
----------------

-   **Role-Based Access Control:** Granular permissions for different user types:

    -   **Superuser:** Full control over the entire platform. Can manage all users and all job postings.

    -   **Staff/Admin:** Can post new jobs. Can only edit or delete jobs they personally posted. Can manage all job tags.

    -   **Authenticated User:** Can search/filter jobs, view job details, and track their application status (Bookmark, Apply, etc.).

    -   **Anonymous User:** Can search/filter and view public job listings.

-   **Job Interaction Tracking:** A `UserJobMapping` model tracks each user's relationship with a job (e.g., `Bookmarked`, `Applied`, `Clicked`), enabling personalized dashboards.

-   **Dedicated User Endpoints:** Users can fetch lists of their own bookmarked and applied jobs.

-   **Dynamic Tagging System:** Jobs can be categorized with multiple tags (e.g., "AI", "Web Development", "Remote"), which are also manageable via the API.

-   **Powerful Filtering & Search:** The jobs list endpoint (`/api/jobs/`) supports:

    -   Filtering by `job_type`, `location`, `company`, `title`, and `tags`.

    -   Keyword search across `title`, `company`, `description`, and `tags`.

    -   Ordering by `updated_at`, `created_at`, etc.

-   **Full User Authentication:** Complete auth flow including Signup, Login, Logout, and Password Reset.

-   **Pagination:** Standardized `PageNumberPagination` for all list-based endpoints.

🧱 Tech Stack
-------------

-   **Backend:** Django

-   **API:** Django REST Framework

-   **Database:** PostgreSQL

-   **Filtering:** `django-filter`

-   **Deployment:** Render (for Backend & DB)

-   **WSGI Server:** Gunicorn

-   **Static Files:** Whitenoise

🏗️ Project Structure
---------------------

```
jobBoard/
│
├── jobBoardProject/        (Project config folder)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── jobBoard/               (App for authentication & user management)
│   ├── models.py         (TimestampedModel, UserManager, User)
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py    (IsAdminOrReadOnly, IsJobOwnerOrSuperuser)
│   └── utils.py
│
├── jobs/                   (App for job listings, tags, applications)
│   ├── models.py         (Job, Tag, UserJobMapping)
│   ├── serializers.py
│   ├── views.py
│   ├── filters.py
│   ├── urls.py
│   ├── pagination.py
│   └── admin.py
│
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt

```

🧱 Models Overview
------------------

### 1. **User (CustomUser)**
Extends Django’s `AbstractUser`  
Includes fields:
- `email`, `first_name`, `last_name`, `is_staff`, `date_joined`, etc.

### 2. **Job**
Stores all company job listings with fields:
- `company_name`
- `role`
- `ctc`
- `stipend`
- `job_type`
- `location`
- `description`
- `is_active`
- `created_at` (auto-added from `TimeStampedModel`)

Indexed fields for performance:  
`company_name`, `role`, `location`, `created_at`, `is_active`

### 3. **UserJobMapping**
Maintains the relationship between **User** and **Job**.
- `user` → ForeignKey(User)
- `job` → ForeignKey(Job)
- `status` → Choice(`applied`, `bookmarked`)
- `created_at` → Timestamp

```

🔗 API Endpoints
----------------

### 🔒 Auth Routes (`/api/auth/`)
| Method | Endpoint | Description |
|--------|-----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login user, get JWT tokens |
| GET | `/api/auth/profile/` | Get logged-in user details |
| POST | `/api/auth/logout/` | Logout and blacklist tokens |

---

### 💼 Job Routes (`/api/jobs/`)
| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/api/jobs/` | List all active jobs (search, sort, filter supported) |
| GET | `/api/jobs/<id>/` | Retrieve job details |
| POST | `/api/jobs/` | Create new job (Admin only) |
| PUT | `/api/jobs/<id>/` | Update job (Admin only) |
| DELETE | `/api/jobs/<id>/` | Delete job (Admin only) |

---

### ⭐ User Job Mapping (`/api/jobs/user-jobs/`)
| Method | Endpoint | Description |
|--------|-----------|-------------|
| POST | `/api/jobs/apply/<job_id>/` | Mark job as applied |
| POST | `/api/jobs/bookmark/<job_id>/` | Bookmark a job |
| GET | `/api/jobs/my-jobs/` | List all bookmarked/applied jobs by the user |

---

## 🧩 Tech Stack

### **Backend**
- Django 5.x
- Django REST Framework
- PostgreSQL
- SimpleJWT (for authentication)

### **Deployment**
- **Render** for backend hosting
- **Gunicorn** as the WSGI server
- **Whitenoise** for static file management

```

⚙️ Local Setup & Installation
-----------------------------

1.  **Clone the Repository**

    ```
    git clone [https://github.com/](https://github.com/)<your-username>/jobBoard.git
    cd jobBoard

    ```

2.  **Create and Activate a Virtual Environment**

    ```
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate

    ```

3.  **Install Dependencies**

    ```
    pip install -r requirements.txt

    ```

4.  **Set Up Environment Variables** Create a `.env` file in the root directory and add your local configuration:

    ```
    SECRET_KEY=your-django-secret-key
    DEBUG=True

    # Local PostgreSQL Database
    DATABASE_NAME=jobboard_db
    DATABASE_USER=your_db_user
    DATABASE_PASSWORD=your_db_password
    DATABASE_HOST=localhost
    DATABASE_PORT=5432

    ```

    *Note: You must have PostgreSQL running on your machine.*

5.  **Run Migrations**

    ```
    python manage.py migrate

    ```

6.  **Create a Superuser** This account will have full admin privileges.

    ```
    python manage.py createsuperuser

    ```

    *(Follow the prompts to set email and password)*

7.  **Run the Development Server**

    ```
    python manage.py runserver

    ```

    The API will be available at `http://127.0.0.1:8000/`.

🌐 Deployment on Render
-----------------------

This project is configured for easy deployment on Render.

1.  **Create a PostgreSQL Database:**

    -   On your Render dashboard, create a new "PostgreSQL" service.

    -   Copy the **"Internal Connection URL"** (you'll use this for `DATABASE_URL`).

2.  **Create a Web Service:**

    -   Create a new "Web Service" and connect it to your GitHub repository.

    -   **Environment:** `Python`

    -   **Region:** Choose a region close to your database.

    -   **Build Command:** `pip install -r requirements.txt && python manage.py migrate`

    -   **Start Command:** `gunicorn jobBoardProject.wsgi`

3.  **Add Environment Variables:** In the "Environment" tab for your Web Service, add the following:

    -   `SECRET_KEY`: Generate a new secret key (`python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)

    -   `DATABASE_URL`: Paste the "Internal Connection URL" from your Render database.

    -   `DEBUG`: `False`

    -   `PYTHON_VERSION`: `3.11.0` (or your desired version)

Deploy the service. Your API will be live!
