# /apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User Model for the application.
    Extends Django's default user to add roles (UserType) and a link to a student's grade.
    """
    class UserType(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        ADMIN = 'ADMIN', _('Admin')

    # This field determines if the user is a student or an admin.
    user_type = models.CharField(
        _('User Type'),
        max_length=10,
        choices=UserType.choices,
        default=UserType.STUDENT
    )
    
    # This links a student user to their grade. It's nullable for admins.
    # Using a string 'academics.Grade' prevents circular import errors.
    grade = models.ForeignKey(
        'academics.Grade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # Admins won't have a grade, so this can be blank.
        related_name='students',
        verbose_name=_('Grade')
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

