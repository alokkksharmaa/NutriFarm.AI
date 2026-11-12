import os
import sys

path = '/home/alokkumar23/NutriFarm.AI'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nutrifarm.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()