# /apps/dashboard/forms.py

from django import forms
from apps.users.models import User
from apps.academics.models import Grade
from apps.quizzes.models import Badge
class AdminStudentCreationForm(forms.ModelForm):
    """
    A form for admins to create new student accounts.
    """
    password = forms.CharField(widget=forms.PasswordInput, help_text="Set a password for the student.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'grade']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.user_type = User.UserType.STUDENT
        if commit:
            user.save()
        return user

class AdminStudentUpdateForm(forms.ModelForm):
    """
    A form for admins to update an existing student's details.
    """
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep the current password.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'grade']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class BadgeForm(forms.ModelForm):
    """
    A form for creating and editing badges.
    """
    class Meta:
        model = Badge
        fields = ['name', 'slug', 'description', 'icon']
        help_texts = {
            'slug': "A unique key in English, e.g., 'perfect_score'. This cannot be changed later."
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            # FIX: Removed 'readonly' from here to allow adding a slug on creation
            'slug': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg bg-gray-100'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This logic correctly makes the slug field readonly ONLY when editing an existing badge
        if self.instance and self.instance.pk:
            self.fields['slug'].widget.attrs['readonly'] = True

