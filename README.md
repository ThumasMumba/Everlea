# Everlea Weddings — Wedding Plan Management System

Flask + MySQL app with two roles: **clients** who browse venues and request
bookings, and **admins** who manage venues and approve/reject requests.

## Project structure

```
wedding-planner/
├── app.py                  # Routes, app factory
├── config.py                # Env-driven configuration
├── extensions.py            # db / login_manager singletons
├── models.py                 # User, Venue, Appointment (SQLAlchemy)
├── auth.py                    # role_required() access-control decorator
├── seed.py                     # Interactive script to create the first admin
├── schema.sql                   # Raw SQL schema (optional, mirrors models.py)
├── requirements.txt
├── .env.example
├── static/
│   ├── css/style.css        # Design tokens + component styles
│   └── js/                    # (dashboard filtering is inline in the template)
└── templates/
    ├── base.html             # Contains the html boiler plate
    ├── index.html            # Landing page
    ├── signup.html           # Signup template
    ├── login.html            # Client login
    ├── admin_login.html      # Separate admin login
    ├── client_dashboard.html # Client dashboard
    ├── admin_dashboard.html  # Admin dashboard
    └── error.html
    └── venue_reviews.html    # Client - Review page

```

## Setup

1. **Create a MySQL database.**

   ```bash
   mysql -u root -p < schema.sql
   ```

   This creates the `wedding_planner` database, its tables, and a handful of
   seed venues. (You can skip this — `db.create_all()` in `app.py` will also
   create the tables automatically on first run, but it won't insert the
   sample venues.)

2. **Install dependencies.**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables.**

   ```bash
   cp .env.example .env
   ```

4. **Create the first admin account.**

   ```bash
   python seed.py
   ```

   This prompts for a name, email, and password, hashes the password, and
   inserts an admin row — so no plaintext credentials ever touch the
   database or source control.

5. **Run the app.**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000`.
   - Clients sign up / log in at `/signup` and `/login`.
   - Admins log in separately at `/admin/login`.

## Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash` /
  `check_password_hash` (pbkdf2:sha256) — never stored in plaintext.
- Every dashboard and mutating route is protected by Flask-Login's
  `@login_required` plus a custom `@role_required("client" | "admin")`
  decorator, so a client session can't reach `/admin/dashboard` and vice
  versa (a 403 page is shown instead).
- Session cookies are `HttpOnly` and `SameSite=Lax` by default; set
  `SESSION_COOKIE_SECURE=True` once you're serving over HTTPS.
- `.env` (with real secrets) Should be excluded from version control — only
  `.env.example` is committed.
