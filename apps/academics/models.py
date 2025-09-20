# /apps/academics/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class Grade(models.Model):
    """
    Represents a grade level in the school (e.g., Grade 1, Grade 2).
    This is the top-level grouping for academic content.
    """
    name = models.CharField(
        _('Grade Name'),
        max_length=100, 
        unique=True,
        help_text=_("e.g., Grade 1, Grade 2")
    )
    description = models.TextField(
        _('Description'),
        blank=True, 
        null=True,
        help_text=_("A brief description of the grade level.")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Grade')
        verbose_name_plural = _('Grades')
        ordering = ['name'] # Ensures grades are ordered consistently.

class Unit(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='units')
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True, null=True)
    unit_number = models.PositiveIntegerField(_('Unit Number'), default=1)
    
    # حقل جديد لتحديد مدة الاختبار
    duration_minutes = models.PositiveIntegerField(
        _('Quiz Duration (minutes)'), 
        default=10, 
        help_text="Set the time limit for this unit's quiz in minutes."
    )
    is_published = models.BooleanField(
    default=False,
    help_text="Check this box to make the unit visible to students.")
    
    def __str__(self):
        return f"{self.grade.name}: {self.title}"

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')
        ordering = ['grade', 'unit_number']
