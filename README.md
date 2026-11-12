# NutriFarm AI

Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers.

NutriFarm AI is a farmer-focused Django platform for feed and silage sample
records. The current foundation includes a responsive public site, farmer
accounts, a private database-backed dashboard, and admin-managed sample data.
Farmer sample submission and quality assessment are planned for later work.

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

Open http://127.0.0.1:8000/ to view the homepage. Run `python manage.py check`
to validate the Django configuration.

For deployment, set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and
`DJANGO_ALLOWED_HOSTS` in the environment. The built-in secret fallback is for
local development only. Bootstrap 5 is loaded from jsDelivr; an internet
connection is required for its CDN assets.

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

Farmers can register at `/register/`, log in at `/login/`, and view their private dashboard at `/dashboard/`. Staff can manage sample records and test results at `/admin/`. Sample submission is planned for a later phase; administrators can currently create sample records.
