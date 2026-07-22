from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)

    # Email verification (OTP)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_created_at = db.Column(db.DateTime, nullable=True)

    # Brute-force lockout
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---- Password helpers ----
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    # ---- Lockout helpers ----
    def is_locked(self):
        return self.locked_until is not None and self.locked_until > datetime.utcnow()

    def seconds_until_unlock(self):
        if not self.is_locked():
            return 0
        delta = self.locked_until - datetime.utcnow()
        return max(int(delta.total_seconds()), 0)

    def register_failed_attempt(self, max_attempts, lockout_duration):
        self.failed_attempts += 1
        if self.failed_attempts >= max_attempts:
            self.locked_until = datetime.utcnow() + lockout_duration
            self.failed_attempts = 0  # reset counter, lock has taken over

    def register_successful_login(self):
        self.failed_attempts = 0
        self.locked_until = None

    def __repr__(self):
        return f"<User {self.email}>"
