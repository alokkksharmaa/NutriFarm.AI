from django.urls import path

from . import views

app_name = 'testing'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),
    path('sample/<int:sample_id>/', views.sample_detail, name='sample_detail'),
]
