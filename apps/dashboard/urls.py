# /apps/dashboard/urls.py

from django.urls import path
# This import style is correct
from .views import (
    dashboard_home_view,
    GradeListView, GradeCreateView, GradeUpdateView, GradeDeleteView,
    UnitListView, UnitCreateView, UnitUpdateView, UnitDeleteView,
    QuestionListView, QuestionCreateView, QuestionUpdateView, QuestionDeleteView,
    UserListView, create_student_view, create_student_success_view,
    StudentUpdateView, StudentDeleteView, student_progress_detail_view,
    quiz_attempt_detail_view, BadgeListView, BadgeCreateView, BadgeUpdateView, BadgeDeleteView, toggle_unit_publish_status
)

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_home_view, name='home'),
    path('units/<int:pk>/toggle-publish/', toggle_unit_publish_status, name='unit_toggle_publish'),

    # Grade URLs
    path('grades/', GradeListView.as_view(), name='grade_list'),
    path('grades/add/', GradeCreateView.as_view(), name='grade_add'),
    path('grades/<int:pk>/edit/', GradeUpdateView.as_view(), name='grade_edit'),
    path('grades/<int:pk>/delete/', GradeDeleteView.as_view(), name='grade_delete'),

    # Unit URLs
    path('units/', UnitListView.as_view(), name='unit_list'),
    path('units/add/', UnitCreateView.as_view(), name='unit_add'),
    path('units/<int:pk>/edit/', UnitUpdateView.as_view(), name='unit_edit'),
    path('units/<int:pk>/delete/', UnitDeleteView.as_view(), name='unit_delete'),

    # Question URLs
    path('questions/', QuestionListView.as_view(), name='question_list'),
    path('questions/add/', QuestionCreateView.as_view(), name='question_add'),
    path('questions/<int:pk>/edit/', QuestionUpdateView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question_delete'),

    # Student Management URLs
    path('students/', UserListView.as_view(), name='user_list'),
    path('students/add/', create_student_view, name='student_add'),
    path('students/add/success/', create_student_success_view, name='create_student_success'),
    path('students/<int:pk>/progress/', student_progress_detail_view, name='student_progress_detail'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('students/quiz-result/<int:pk>/', quiz_attempt_detail_view, name='quiz_attempt_detail'),

    # Badge URLs
    path('badges/', BadgeListView.as_view(), name='badge_list'),
    path('badges/add/', BadgeCreateView.as_view(), name='badge_add'),
    path('badges/<int:pk>/edit/', BadgeUpdateView.as_view(), name='badge_edit'),
    path('badges/<int:pk>/delete/', BadgeDeleteView.as_view(), name='badge_delete'),

]
