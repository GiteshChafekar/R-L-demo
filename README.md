# 🏦 SecureBank — Login & Registration System

A Flask-based banking web app starter with **email OTP verification** during registration and **automatic account lockout** after repeated failed login attempts. Built as a learning project / internship submission demonstrating core web security concepts.

---

## 📋 What this project does

- **Register** with name, email, and password
- Get a **6-digit OTP sent to your email** to verify you own that address
- **Log in** with your verified account
- If you enter the wrong password **3 times in a row**, your account **locks for 30 minutes** — with a live countdown timer shown on screen
- Land on a simple **dashboard** after logging in

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Database | SQLite (via Flask-SQLAlchemy) |
| Frontend | Plain HTML, CSS, vanilla JavaScript |
| Templating | Jinja2 (built into Flask) |
| Email sending | Flask-Mail over SMTP (Gmail) |
| Password security | Werkzeug password hashing (PBKDF2) |
| Config/secrets | python-dotenv (`.env` file) |

---

## 📁 Project Structure

```
bankapp/
├── app.py              # All routes: register, verify-otp, login, dashboard, logout
├── config.py            # App settings — DB path, mail server, OTP expiry, lockout rules
├── extensions.py        # Shared SQLAlchemy + Flask-Mail instances
├── models.py             # User table + OTP/lockout logic
├── email_utils.py       # Generates OTP codes and sends the email
├── requirements.txt     # Python dependencies
├── .env.example          # Template for your secrets — copy this to .env
├── .gitignore
├── templates/             # HTML pages (Jinja2)
│   ├── base.html
│   ├── register.html
│   ├── verify_otp.html
│   ├── login.html
│   └── dashboard.html
└── static/
    └── css/style.css
```

When you run the app, it also creates:
```
instance/
└── bank.db             # Auto-created SQLite database (not in git)
```

---

## 🚀 How to run this project (step-by-step)

### 1. Get the code
```bash
git clone <your-repo-url>
cd bankapp
```

### 2. Create a virtual environment
This keeps this project's Python packages separate from everything else on your computer.

```bash
python3 -m venv venv
```

Activate it:
- **Mac/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

You'll know it worked if you see `(venv)` at the start of your terminal line.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your email credentials

Copy the example env file:
```bash
cp .env.example .env
```

Open `.env` in your code editor and fill in:

```
SECRET_KEY=any-random-string-you-like
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=youractualemail@gmail.com
MAIL_PASSWORD=your16digitapppassword
```

**Important:** `MAIL_PASSWORD` is NOT your normal Gmail password. You need a Google **App Password**:

1. Turn on 2-Step Verification: https://myaccount.google.com/signinoptions/two-step-verification
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character code Google gives you (remove the spaces when pasting into `.env`)

### 5. Run the app
```bash
python app.py
```

### 6. Open it in your browser
```
http://127.0.0.1:5000
```

You should land on the login page. Click "Register" to create an account, check your email for the OTP, verify, and log in.

---

## 🔒 How the security features work

**OTP Email Verification**
- On registration, a random 6-digit code is generated and stored with a timestamp
- The code is emailed to the user via Gmail SMTP
- The code expires after **10 minutes** (`OTP_EXPIRY_MINUTES` in `config.py`)
- Accounts stay "unverified" and can't log in until the correct code is entered

**Login Lockout**
- Each user record tracks `failed_attempts` and `locked_until`
- Every wrong password adds 1 to `failed_attempts`
- On the **3rd wrong attempt**, `locked_until` is set to *now + 30 minutes*, and the counter resets
- While locked, the login form is disabled and a JavaScript countdown timer shows time remaining
- A correct login resets everything back to zero

This logic lives mainly in `models.py` (see `register_failed_attempt`, `is_locked`, `seconds_until_unlock`) and is used inside the `/login` route in `app.py`.

---

## 🛠️ Common Issues

**"Could not send OTP email... Username and Password not accepted"**
This means Gmail rejected your credentials. Check:
- You're using an **App Password**, not your regular Gmail password
- No leading/trailing spaces in `MAIL_PASSWORD` in `.env`
- No typos or duplicated text in `MAIL_USERNAME` (e.g. `you@gmail.com@gmail.com`)
- You restarted the server after editing `.env` (env variables are only read at startup)

**Nothing happens / app won't start**
- Make sure your virtual environment is activated (you should see `(venv)` in your terminal)
- Make sure you ran `pip install -r requirements.txt` inside that virtual environment

**Want to start fresh / clear all test accounts?**
Stop the server, then delete the database file:
```bash
rm instance/bank.db
```
It'll be recreated empty next time you run `python app.py`.

---

## 📌 Notes for reviewers / instructors

- Passwords are never stored in plain text — only their PBKDF2 hash (via Werkzeug)
- Login error messages are intentionally generic ("Invalid email or password") so an attacker can't tell whether an email is registered in the system
- `.env` and the database file are excluded from git via `.gitignore` — they contain secrets and personal data and should never be committed
- This is a learning/demo project. A production banking app would additionally need: HTTPS, CSRF protection (Flask-WTF), rate limiting, a proper task queue for sending emails asynchronously, and a hosted database instead of SQLite.

---

## 🔮 Possible next steps

- Password reset via email
- Account balance, deposits, withdrawals, transaction history
- Two-factor authentication at login (not just registration)
- Admin panel to view/manage users
