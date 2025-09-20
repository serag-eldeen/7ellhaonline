# /apps/quizzes/urls.py

from django.urls import path
from .views import take_quiz_view, submit_quiz_view, quiz_result_view,certificate_view # Import the new view


app_name = 'quizzes'

urlpatterns = [
    # URL to take the quiz
    path('unit/<int:unit_id>/take/', take_quiz_view, name='take_quiz'),
    
    # URL to submit the quiz answers (API endpoint)
    path('unit/<int:unit_id>/submit/', submit_quiz_view, name='submit_quiz'),

    # URL to view the quiz result
    path('result/<int:result_id>/', quiz_result_view, name='quiz_result'),
    path('result/<int:result_id>/certificate/', certificate_view, name='certificate'),

]
