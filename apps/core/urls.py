# /apps/core/urls.py

# This file doesn't exist yet, so you'll need to create it.

from django.urls import path
from . import views

# This is a good practice for namespacing URLs
app_name = 'core'

urlpatterns = [
    # The homepage URL
    path('', views.home, name='home'),
]
