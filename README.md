# NutriFarm AI

Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers.

NutriFarm AI is a Django foundation for a farmer-focused platform to manage feed
and silage sample testing. This first milestone includes a responsive public
homepage only; accounts, submissions, assessments, and reports are future work.

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
- `templates/` — shared base layout and reusable navigation/footer partials.
- `static/` — project CSS and JavaScript.
Smart Al-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers
