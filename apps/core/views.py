# /apps/core/views.py

from django.shortcuts import render

def home(request):
    """
    View function for the site's homepage.
    Renders the home.html template.
    """
    # The context dictionary can pass data to the template if needed.
    # For now, it's empty.
    context = {} 
    return render(request, 'core/home.html', context)
