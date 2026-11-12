
import os
import sys

# Project directory
path = '/home/alokkumar23/NutriFarm.AI'

if path not in sys.path:
    sys.path.insert(0, path)

# Environment variables MUST be set before Django initializes
os.environ['DJANGO_SETTINGS_MODULE'] = 'nutrifarm.settings'
os.environ['DJANGO_SECRET_KEY'] = 'ni0gasw6-CRaae2-fpfjWC8CIPZ8l9VpjK6FZLgjw6yXi-5kG3t9SJZpEvLtxQGK7pA'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'alokkumar23.pythonanywhere.com'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
