# /apps/academics/urls.py

from django.urls import path
from .views import (
    unit_list_view, 
    student_profile_view,
    leaderboard_selection_view,
    leaderboard_view,review_mistakes_view  # <-- أضف هذا

)

app_name = 'academics'

urlpatterns = [
    path('dashboard/', unit_list_view, name='unit_list'),
    path('my-progress/', student_profile_view, name='student_profile'),
    
    # New URLs for leaderboards
    path('leaderboards/', leaderboard_selection_view, name='leaderboard_selection'),
    path('leaderboards/grade/<int:grade_id>/', leaderboard_view, name='leaderboard_detail'),
    path('my-mistakes/', review_mistakes_view, name='review_mistakes'), # <-- أضف هذا السطر
]
