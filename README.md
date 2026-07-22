Steps to run this code
1. Create virtual environment
```bash
python3 -m venv venv
```

Activate it:
- **Mac/Linux:**     `source venv/bin/activate`
- **Windows:**       `venv\Scripts\activate`

------------------------------------------------------------------------------------------------

2. install all dependencies
```bash
pip install -r requirements.txt
```

--------------------------------------------------------------------------------------------------

3. Set up your email credentials
Copy the example env file:

```bash
cp .env.example .env
```

--------------------------------------------------------------------------------------------------------

4. Open .env (not .env.example-- don't touch it)
and change

SECRET_KEY=          (replace with a long random string)
MAIL_USERNAME=       (your actual email@gmail.com)

**Important:** `MAIL_PASSWORD` is NOT your normal Gmail password. You need a Google **App Password**:

i. Turn on 2-Step Verification: https://myaccount.google.com/signinoptions/two-step-verification
ii. Generate an App Password: https://myaccount.google.com/apppasswords
iii. Copy the 16-character code Google gives you (remove the spaces when pasting into `.env`)
iv. also create an folder
```bash
mkdir instance
```

note:- enter the email in MAIL_USERNAME from which you have generated app password

-----------------------------------------------------------------------------------------------------------------

5. Run the app
```bash
python app.py
```
6. Open it in your browser
```
http://127.0.0.1:5000
```


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
