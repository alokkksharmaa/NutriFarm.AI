# NutriFarm AI

A Django web application for recording and reviewing dairy feed and silage samples.

Farmers can create an account, save sample measurements and observations, view
their private sample history, and run a basic sample assessment.

## Features

- Farmer registration, login, and a private dashboard
- Feed and silage sample records, including pH, moisture, temperature, smell,
  visible mold, and notes
- Per-farmer sample history and detail pages
- Configurable, rule-based sample assessments
- Django admin for managing sample and result records

> **Assessment scope:** Results use illustrative prototype checks. They are not
> produced by a trained AI model, are not scientifically validated, and do not
> certify feed quality or safety. Use appropriate laboratory testing and
> qualified agricultural advice for real decisions.

## Requirements

- Python 3.12 or newer
- Dependencies listed in `requirements.txt` (Django and python-dotenv)

## Run locally

From the project directory, create a virtual environment, install dependencies,
apply database migrations, and start the development server:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

To access the Django admin, create an administrator account:

```powershell
python manage.py createsuperuser
```

Then sign in at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Run tests

```powershell
python manage.py test
```

## Main pages

| Page | URL |
| --- | --- |
| Register | `/register/` |
| Log in | `/login/` |
| Farmer dashboard | `/dashboard/` |
| Submit a sample | `/samples/submit/` |
| Sample history | `/samples/` |
| Django admin | `/admin/` |

Sample and assessment pages require login. Each farmer can access only their own
sample records.

## Project structure

- `nutrifarm/` — Django settings and application entry points
- `core/` — public homepage
- `testing/` — accounts, sample records, assessments, and tests
- `templates/` — page templates
- `static/` — CSS and JavaScript
