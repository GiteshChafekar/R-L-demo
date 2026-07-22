import random
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)

from config import Config
from extensions import db, mail
from models import User
from email_utils import generate_otp, send_otp_email


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def register_routes(app):

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    # ---------------- REGISTER ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not full_name or not email or not password:
                flash("All fields are required.", "error")
                return redirect(url_for("register"))

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return redirect(url_for("register"))

            if len(password) < 8:
                flash("Password must be at least 8 characters long.", "error")
                return redirect(url_for("register"))

            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.is_verified:
                flash("An account with this email already exists. Please log in.", "error")
                return redirect(url_for("login"))

            otp_code = generate_otp()

            if existing_user and not existing_user.is_verified:
                # Re-registration attempt before verifying: update details & resend OTP
                user = existing_user
                user.full_name = full_name
                user.set_password(password)
            else:
                account_number = str(random.randint(10**11, 10**12 - 1))  # 12-digit acct #
                user = User(
                    full_name=full_name,
                    email=email,
                    account_number=account_number,
                )
                user.set_password(password)
                db.session.add(user)

            user.otp_code = otp_code
            user.otp_created_at = datetime.utcnow()
            db.session.commit()

            try:
                send_otp_email(email, full_name, otp_code, app.config["OTP_EXPIRY_MINUTES"])
            except Exception as e:
                flash(f"Could not send OTP email. Check mail configuration. ({e})", "error")
                return redirect(url_for("register"))

            session["pending_email"] = email
            flash("A verification code has been sent to your email.", "success")
            return redirect(url_for("verify_otp"))

        return render_template("register.html")

    # ---------------- VERIFY OTP ----------------
    @app.route("/verify-otp", methods=["GET", "POST"])
    def verify_otp():
        email = session.get("pending_email")
        if not email:
            flash("Please register first.", "error")
            return redirect(url_for("register"))

        if request.method == "POST":
            entered_otp = request.form.get("otp", "").strip()
            user = User.query.filter_by(email=email).first()

            if not user:
                flash("Account not found. Please register again.", "error")
                return redirect(url_for("register"))

            expiry_time = user.otp_created_at + timedelta(
                minutes=app.config["OTP_EXPIRY_MINUTES"]
            )

            if datetime.utcnow() > expiry_time:
                flash("OTP has expired. Please request a new one.", "error")
                return redirect(url_for("verify_otp"))

            if entered_otp != user.otp_code:
                flash("Invalid OTP. Please try again.", "error")
                return redirect(url_for("verify_otp"))

            user.is_verified = True
            user.otp_code = None
            user.otp_created_at = None
            db.session.commit()

            session.pop("pending_email", None)
            flash("Email verified successfully! You can now log in.", "success")
            return redirect(url_for("login"))

        return render_template("verify_otp.html", email=email)

    @app.route("/resend-otp")
    def resend_otp():
        email = session.get("pending_email")
        if not email:
            flash("Please register first.", "error")
            return redirect(url_for("register"))

        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for("register"))

        otp_code = generate_otp()
        user.otp_code = otp_code
        user.otp_created_at = datetime.utcnow()
        db.session.commit()

        try:
            send_otp_email(email, user.full_name, otp_code, app.config["OTP_EXPIRY_MINUTES"])
            flash("A new OTP has been sent to your email.", "success")
        except Exception as e:
            flash(f"Could not send OTP email. ({e})", "error")

        return redirect(url_for("verify_otp"))

    # ---------------- LOGIN ----------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()

            # Generic message to avoid revealing whether the email exists
            generic_error = "Invalid email or password."

            if not user:
                flash(generic_error, "error")
                return redirect(url_for("login"))

            if user.is_locked():
                minutes_left = (user.seconds_until_unlock() // 60) + 1
                flash(
                    f"Account locked due to multiple failed attempts. "
                    f"Try again in about {minutes_left} minute(s).",
                    "error"
                )
                return render_template(
                    "login.html",
                    locked_seconds=user.seconds_until_unlock()
                )

            if not user.is_verified:
                session["pending_email"] = email
                flash("Please verify your email before logging in.", "error")
                return redirect(url_for("verify_otp"))

            if not user.check_password(password):
                user.register_failed_attempt(
                    app.config["MAX_LOGIN_ATTEMPTS"], app.config["LOCKOUT_DURATION"]
                )
                db.session.commit()

                if user.is_locked():
                    flash(
                        "Too many failed attempts. Your account is locked for 30 minutes.",
                        "error"
                    )
                    return render_template(
                        "login.html",
                        locked_seconds=user.seconds_until_unlock()
                    )
                else:
                    remaining = app.config["MAX_LOGIN_ATTEMPTS"] - user.failed_attempts
                    flash(f"{generic_error} {remaining} attempt(s) remaining.", "error")
                    return redirect(url_for("login"))

            # Success
            user.register_successful_login()
            db.session.commit()
            session["user_id"] = user.id
            session["user_name"] = user.full_name
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("dashboard"))

        return render_template("login.html", locked_seconds=0)

    # ---------------- DASHBOARD ----------------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = User.query.get(session["user_id"])
        return render_template("dashboard.html", user=user)

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
