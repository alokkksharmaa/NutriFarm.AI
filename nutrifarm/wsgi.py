import os
import sys

# Add your project directory to the sys.path
path = '/home/alokkumar23/NutriFarm.AI'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'nutrifarm.settings'

# Load the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()