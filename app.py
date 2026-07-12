from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from config import Config
from extensions import db, login_manager
from models import User, Venue, Appointment
from auth import role_required

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access that page."
    login_manager.login_message_category = "error"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(
            minutes=app.config["PERMANENT_SESSION_LIFETIME_MINUTES"]
        )

    return app

app = create_app()

login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access that page."
login_manager.login_message_category = "error"

@login_manager.user_loader
def load_user(user_id):
        return db.session.get(User, int(user_id))

@app.before_request
def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(
            minutes=app.config["PERMANENT_SESSION_LIFETIME_MINUTES"]
        )

    # ------------------------------------------------------------------
    # Public routes
    # ------------------------------------------------------------------

@app.route("/")
def index():
        if current_user.is_authenticated:
            return redirect(
                url_for("admin_dashboard") if current_user.is_admin else url_for("dashboard")
            )
        return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")

            errors = []
            if not name or not email or not password:
                errors.append("All fields are required.")
            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")
            if password != confirm:
                errors.append("Passwords do not match.")
            if User.query.filter_by(email=email).first():
                errors.append("An account with that email already exists.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template("signup.html", name=name, email=email)

            user = User(name=name, email=email, role="client")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash("Account created — you can now log in.", "success")
            return redirect(url_for("login"))

        return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    email = " "
    if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

    if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email, role="client").first()

            if not user:
                flash("No client account found with that email.", "error")
            elif not user.check_password(password):
                flash("Incorrect password. Please try again.", "error")
            else:
                login_user(user)
                flash(f"Welcome back, {user.name.split(' ')[0]}.", "success")
                return redirect(url_for("dashboard"))

    return render_template("login.html", email=email)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for("admin_dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            admin = User.query.filter_by(email=email, role="admin").first()

            if not admin:
                flash("No administrator account found with that email.", "error")
            elif not admin.check_password(password):
                flash("Incorrect password. Please try again.", "error")
            else:
                login_user(admin)
                flash("Welcome back, administrator.", "success")
                return redirect(url_for("admin_dashboard"))

            return render_template("admin_login.html", email=email)

        return render_template("admin_login.html")

@app.route("/logout")
@login_required
def logout():
        logout_user()
        flash("Logout successfully.", "success")
        return redirect(url_for("login"))

    # ------------------------------------------------------------------
    # Client dashboard
    # ------------------------------------------------------------------

@app.route("/dashboard")
@login_required
@role_required("client")
def dashboard():
        venues = Venue.query.filter_by(is_active=True).order_by(Venue.name).all()
        appointments = (
            Appointment.query.filter_by(user_id=current_user.id)
            .order_by(Appointment.created_at.desc())
            .all()
        )
        return render_template(
            "client_dashboard.html", venues=venues, appointments=appointments
        )

@app.route("/book", methods=["POST"])
@login_required
@role_required("client")
def book_appointment():
        venue_id = request.form.get("venue_id", type=int)
        event_date_raw = request.form.get("event_date", "")
        guest_count = request.form.get("guest_count", type=int)
        notes = request.form.get("notes", "").strip()

        venue = db.session.get(Venue, venue_id) if venue_id else None
        if not venue:
            flash("Please choose a valid venue.", "error")
            return redirect(url_for("dashboard"))

        try:
            event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Please choose a valid event date.", "error")
            return redirect(url_for("dashboard"))

        if event_date < datetime.utcnow().date():
            flash("Event date cannot be in the past.", "error")
            return redirect(url_for("dashboard"))

        appointment = Appointment(
            user_id=current_user.id,
            venue_id=venue.id,
            event_date=event_date,
            guest_count=guest_count,
            notes=notes,
            status="pending",
        )
        db.session.add(appointment)
        db.session.commit()

        flash(f"Booking request sent for {venue.name}. We'll notify you once it's reviewed.", "success")
        return redirect(url_for("dashboard"))

    # ------------------------------------------------------------------
    # Admin dashboard
    # ------------------------------------------------------------------

@app.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
        users = (
            User.query.filter_by(role="client").order_by(User.created_at.desc()).all()
        )
        venues = Venue.query.order_by(Venue.name).all()
        appointments = (
            Appointment.query.order_by(Appointment.created_at.desc()).all()
        )
        pending_count = sum(1 for a in appointments if a.status == "pending")

        return render_template(
            "admin_dashboard.html",
            users=users,
            venues=venues,
            appointments=appointments,
            pending_count=pending_count,
        )

@app.route("/admin/appointments/<int:appointment_id>/approve", methods=["POST"])
@login_required
@role_required("admin")
def approve_appointment(appointment_id):
        appointment = db.session.get(Appointment, appointment_id)
        if not appointment:
            flash("Appointment not found.", "error")
        else:
            appointment.status = "confirmed"
            db.session.commit()
            flash("Booking confirmed. The client has been notified.", "success")
        return redirect(url_for("admin_dashboard"))

@app.route("/admin/appointments/<int:appointment_id>/reject", methods=["POST"])
@login_required
@role_required("admin")
def reject_appointment(appointment_id):
        appointment = db.session.get(Appointment, appointment_id)
        if not appointment:
            flash("Appointment not found.", "error")
        else:
            appointment.status = "rejected"
            db.session.commit()
            flash("Booking request rejected.", "success")
        return redirect(url_for("admin_dashboard"))

@app.route("/admin/venues", methods=["POST"])
@login_required
@role_required("admin")
def add_venue():
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        capacity = request.form.get("capacity", type=int) or 0
        price = request.form.get("price_per_event", type=float) or 0
        image_url = request.form.get("image_url", "").strip()

        if not name or not location:
            flash("Venue name and location are required.", "error")
            return redirect(url_for("admin_dashboard"))

        venue = Venue(
            name=name,
            location=location,
            description=description,
            capacity=capacity,
            price_per_event=price,
            image_url=image_url or None,
        )
        db.session.add(venue)
        db.session.commit()
        flash(f"{name} added to the venue list.", "success")
        return redirect(url_for("admin_dashboard"))

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------

@app.errorhandler(403)
def forbidden(e):
        return render_template("error.html", code=403, message="You don't have access to that page."), 403

@app.errorhandler(404)
def not_found(e):
        return render_template("error.html", code=404, message="That page doesn't exist."), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
