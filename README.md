# CodeBlog

A Django blogging platform with accounts, Google OAuth sign-in, user profiles and avatars, publishing/drafts, story image and video attachments, cover images, comments, likes, bookmarks, search, pagination, author pages, a saved light/dark theme toggle, and an admin area. SQLite is configured by default.

## 1. Run locally

```bash
# Windows PowerShell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. Register a user, publish a story, and visit `/admin/` for administration. Uploaded images and videos are stored in the local `media/` directory in development and in S3-compatible object storage in production.

## 2. Google OAuth setup

OAuth is wired through django-allauth and the Google provider. To activate it:

1. Create an OAuth 2.0 **Web application** client in Google Cloud Console and configure the OAuth consent screen.
2. Add `http://127.0.0.1:8000/accounts/google/login/callback/` as an authorized redirect URI.
3. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in your environment (or create a `.env` loader of your choice; Django does not read `.env` automatically).
4. In `/admin/`, open **Social applications**, add a Google application using the same client ID and secret, and associate it with the `example.com` Site (Site ID 1). Alternatively configure the provider app using environment values.

Google will not authenticate users until real credentials and the matching provider configuration are supplied. Never commit OAuth secrets.

## 3. Email MFA

After a successful sign-in, the app sends a 6-digit verification code to the user's email address before access is granted. The login page also provides a password-reset flow that emails a time-limited reset link to the address on the account. Google-only accounts can receive a reset link when their matching email address is verified by allauth; this lets them set a local password as an alternative to Google sign-in. Both features use Django's configured email backend. When SMTP credentials are missing or are recognized placeholders, the app falls back to the console backend for local testing; messages appear in the runserver terminal. For real delivery, set `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` in the environment. Set `PUBLIC_SITE_URL` to the public base URL (for example, `https://codeblog.example`) so reset links work for other users. Without it, DEBUG mode builds links from the host used to submit the reset form; a localhost link only works on the machine running Django.

## 4. Deploy to Render

The app keeps SQLite for local development and automatically uses PostgreSQL when `DATABASE_URL` is set. WhiteNoise serves collected static files. Uploaded images and videos use the local `media/` directory during development and S3-compatible object storage in production.

1. Push the project to a private GitHub repository. Do not commit `.env`, secrets, `db.sqlite3`, or uploaded media.
2. Create an S3-compatible bucket and access credentials for media uploads. Create a PostgreSQL database in Render, then create a Python web service connected to the repository.
3. Use these commands for the web service:

   ```text
   Build: pip install -r requirements.txt && python manage.py collectstatic --noinput
   Start: gunicorn codeblog.wsgi:application
   ```

4. Add these environment variables to the web service:

   - `DATABASE_URL`: the PostgreSQL **internal** connection URL from Render.
   - `DJANGO_SECRET_KEY`: a newly generated, strong secret (for example, generate one with `py -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`).
   - `DJANGO_DEBUG`: `False`.
   - `DJANGO_ALLOWED_HOSTS`: your Render hostname, such as `your-service.onrender.com` (comma-separated if using a custom domain too).
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: full HTTPS origins, such as `https://your-service.onrender.com` (comma-separated if needed).
   - `AWS_STORAGE_BUCKET_NAME`: the name of an S3-compatible bucket for uploaded images and videos.
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_S3_REGION_NAME`: credentials and region for that bucket.
   - `AWS_S3_ENDPOINT_URL`: only if your storage provider requires a custom S3-compatible endpoint (for example, Cloudflare R2).
   - Email settings from [Email MFA](#3-email-mfa), using real SMTP credentials.
   - Google OAuth credentials and `PUBLIC_SITE_URL` if those features are enabled.

   Production startup intentionally fails if the secret key, media bucket, or real email credentials are missing. Keep the bucket private and give the app credentials only for the required bucket operations; the storage backend generates time-limited URLs for media.
5. Run `python manage.py migrate` once the service has the production environment variables, then verify the site and create an admin user with `python manage.py createsuperuser`.
6. Existing files in local `media/` are not copied automatically and must be migrated separately if you need them.
7. Update the Google OAuth redirect URI to `https://YOUR-HOSTNAME/accounts/google/login/callback/` and test sign-in, MFA email, static files, and media uploads.

Before switching production traffic, run `python manage.py check --deploy` with the production environment variables. SQLite remains the local default; changing databases does not copy existing local data or uploaded files.
