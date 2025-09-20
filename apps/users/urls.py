# /apps/users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import StudentSignUpView, redirect_after_login_view, StudentGradeUpdateView

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redirect/', redirect_after_login_view, name='redirect_after_login'),
    
    # New URL for updating grade
    path('update-grade/', StudentGradeUpdateView.as_view(), name='update_grade'),
]
