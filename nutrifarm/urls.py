from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('testing.urls')),
]

handler404 = 'testing.views.page_not_found'
