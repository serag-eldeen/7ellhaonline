# /apps/users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import StudentSignUpForm, StudentGradeUpdateForm
from .models import User

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

@login_required
def redirect_after_login_view(request):
    """
    Redirects users to the appropriate dashboard based on their user_type.
    """
    if request.user.user_type == 'ADMIN':
        return redirect('dashboard:home')
    else:
        return redirect('academics:unit_list')

class StudentGradeUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allows a student to update their own grade from their profile.
    """
    model = User
    form_class = StudentGradeUpdateForm
    template_name = 'users/update_grade.html'
    success_url = reverse_lazy('academics:student_profile') # Redirect back to profile page

    def get_object(self, queryset=None):
        # This ensures that students can only ever edit their own profile
        return self.request.user
