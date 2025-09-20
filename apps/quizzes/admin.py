from django.contrib import admin
from .models import Question, Answer, QuizResult

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

# This registers the Question model
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'unit', 'question_type', 'order')
    list_filter = ('unit__grade', 'unit', 'question_type')
    search_fields = ('question_text',)
    inlines = [AnswerInline] # This lets you add answers directly on the question page

# This registers the QuizResult model
@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit', 'score', 'completed_at')
    list_filter = ('unit__grade', 'unit')
    search_fields = ('student__username', 'unit__title')
    # Results should not be editable by admins
    readonly_fields = ('student', 'unit', 'score', 'completed_at')