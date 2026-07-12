from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(role):
    """
    Restrict a route to a single role ('client' or 'admin').
    Must be stacked with @login_required (Flask-Login) above it,
    or used after confirming current_user.is_authenticated, since
    this decorator only checks *which* role — not whether someone
    is logged in at all.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to continue.", "error")
                return redirect(url_for("login"))
            if current_user.role != role:
                # Authenticated, but wrong role for this area of the site.
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
