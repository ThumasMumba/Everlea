"""
One-time helper to create the first admin account.

Usage:
    python seed.py

Run this after the database tables exist (either via schema.sql or
after app.py's db.create_all() has run once). It will prompt for an
admin name, email, and password, hash the password with Werkzeug,
and insert the row — so no plaintext or pre-computed hash ever needs
to be pasted into schema.sql or source control.
"""

import getpass

from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    db.create_all()

    print("=== Create the first admin account ===")
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password (min 8 chars): ")

    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters.")

    if User.query.filter_by(email=email).first():
        raise SystemExit(f"A user with email {email} already exists.")

    admin = User(name=name, email=email, role="admin")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"Admin account created for {email}. You can now log in at /admin/login.")
