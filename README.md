# NutriFarm AI

Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers.

NutriFarm AI is a farmer-focused Django platform for feed and silage sample
records. The application includes a responsive public site, farmer accounts,
private sample records and dashboard, admin management, and illustrative
rule-based assessment results.

## Requirements

- Python 3.12 or newer
- Django 6.1

## Local setup

From the project directory, create and activate a virtual environment, then
install dependencies and initialize the SQLite database:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For local environment overrides, copy `.env.example` to `.env` and set your
local values. `.env` is ignored by Git. The local `manage.py` workflow does not
require a production key; in production, the application requires an explicit
`DJANGO_SECRET_KEY` and allowed host configuration.

Open http://127.0.0.1:8000/ to view the homepage. Run `python manage.py check`
to validate the Django configuration.

Production settings require `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS` in
the server environment; the hosted WSGI entry point enforces
`DJANGO_DEBUG=False`. Local `manage.py` commands default to development mode.
Bootstrap 5 is loaded from jsDelivr; an internet connection is required for its
CDN assets.

## Project layout

- `nutrifarm/` — project settings and root URL/ASGI/WSGI configuration.
- `core/` — public homepage app and its URL/view.
- `testing/` — account views, feed sample and result models, admin, and tests.
- `templates/` — shared base layout and reusable navigation/footer partials.
- `static/` — project CSS and JavaScript.

## Database and farmer accounts

The project uses the built-in SQLite database and Django's User model. After updating the models, create and apply migrations:

```powershell
python manage.py makemigrations testing
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Farmers can register at `/register/`, log in at `/login/`, and view their private dashboard at `/dashboard/`. Authenticated farmers can submit samples at `/samples/submit/`, review their own history at `/samples/`, and open an owned sample from its detail link. Staff can manage sample records and test results at `/admin/`. Temperature validation uses `SAMPLE_TEMPERATURE_MIN_C` and `SAMPLE_TEMPERATURE_MAX_C` in Django settings.

## PythonAnywhere deployment checklist

1. Select a Python version supported by the installed Django release and create a virtual environment for the project.
2. Create a private `.env` file in the server project directory using `.env.example` as a key-name template, but generate a fresh `DJANGO_SECRET_KEY` and set the exact `DJANGO_ALLOWED_HOSTS` and HTTPS `DJANGO_CSRF_TRUSTED_ORIGINS`. Never commit `.env`.
3. Pull the approved source revision, then install only the project dependencies with `pip install -r requirements.txt` in the virtual environment.
4. In the PythonAnywhere Web tab's WSGI configuration file (the `/var/www/..._wsgi.py` file, not just this repository's `nutrifarm/wsgi.py`), point `sys.path` to this project and set `DJANGO_SETTINGS_MODULE` to `nutrifarm.settings`. Django settings load the private `.env` from the project directory; do not paste secret values into the Git-tracked WSGI file.
5. Back up the existing production database before changes. Keep it at the same configured project path to retain farmer records; do not overwrite it with the development `db.sqlite3`. Settings also load `.env` when running management commands from the project, so apply migrations with `python manage.py migrate --noinput` in the production virtual environment.
6. Run `python manage.py collectstatic --noinput`. In the PythonAnywhere Web tab, map URL `/static/` to the project's `staticfiles/` directory.
7. Reload the Web app, then test the homepage and authenticated workflow in a fresh browser session.
