from django.urls import path

from . import views

app_name = 'testing'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.farmer_login, name='login'),
    path('logout/', views.farmer_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('samples/submit/', views.sample_create, name='sample_create'),
    path('samples/', views.sample_history, name='sample_history'),
    path('sample/<int:sample_id>/', views.sample_detail, name='sample_detail'),
    path('sample/<int:sample_id>/evaluate/', views.evaluate_sample, name='evaluate_sample'),
    path('sample/<int:sample_id>/result/', views.sample_result, name='sample_result'),
]
