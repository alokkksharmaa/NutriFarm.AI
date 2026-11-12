"""WSGI config for the NutriFarm AI PythonAnywhere deployment."""

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutrifarm.settings')
# This module is used by the hosted WSGI app. Local development uses manage.py.
os.environ['DJANGO_DEBUG'] = 'False'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
