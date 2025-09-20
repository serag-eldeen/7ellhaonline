from django.contrib import admin
from .models import Grade, Unit

# This tells the admin site to show the Grade model
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# This tells the admin site to show the Unit model
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'grade', 'unit_number')
    list_filter = ('grade',)
    search_fields = ('title', 'description')
    ordering = ('grade', 'unit_number')