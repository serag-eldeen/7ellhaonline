# /apps/users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from apps.academics.models import Grade

class StudentSignUpForm(UserCreationForm):
    """
    A form for creating new student users. This version fixes the bug
    that was causing the password fields to be ignored.
    """
    # Define our custom fields that we want to add to the form
    grade = forms.ModelChoiceField(
        queryset=Grade.objects.all(),
        required=True,
        empty_label="-- Select your grade --",
        label="Grade"
    )
    first_name = forms.CharField(max_length=150, required=False, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")

    class Meta(UserCreationForm.Meta):
        model = User
        # FIX: This line now correctly includes the default fields from UserCreationForm
        # (like username) and adds our new custom fields to the list.
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'grade')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define the common CSS classes for a professional look
        widget_attrs = {
            'class': 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition'
        }
        
        # This loop now correctly finds all fields (including passwords) and applies the style
        for field in self.fields.values():
            field.widget.attrs.update(widget_attrs)
            # Also remove the default Django help texts for a cleaner look
            field.help_text = None

        # Customize the password confirmation field's label
        self.fields['password2'].label = "Confirm Password"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.UserType.STUDENT
        user.grade = self.cleaned_data['grade']
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user

class StudentGradeUpdateForm(forms.ModelForm):
    """
    A form for students to update their own grade.
    """
    class Meta:
        model = User
        fields = ['grade'] # Only include the grade field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].queryset = Grade.objects.all()
        self.fields['grade'].empty_label = "-- Select a new grade --"
        self.fields['grade'].label = "New Grade"
        self.fields['grade'].widget.attrs.update({
            'class': 'w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition'
        })
