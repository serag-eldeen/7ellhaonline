# /apps/academics/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Unit, Grade
from apps.quizzes.models import QuizResult, StudentBadge # استيراد نموذج شارات الطالب
from apps.users.models import User
from collections import defaultdict
from django.db.models import Avg, Count, F, Q # Import Q object
from apps.quizzes.models import StudentAnswer
from collections import OrderedDict
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect

# /apps/academics/views.py

@login_required
def unit_list_view(request):
    """
    يعرض خريطة مغامرات للوحدات الدراسية الخاصة بالطالب.
    """
    student = request.user
    
    # جلب جميع الوحدات الخاصة بصف الطالب لإنشاء الخريطة
    all_units_for_grade = Unit.objects.filter(
        grade=student.grade
    ).select_related('grade').annotate(
        question_count=Count('questions')
    ).order_by('unit_number')
    
    # جلب الوحدات التي أكملها الطالب بالفعل
    completed_unit_ids = set(QuizResult.objects.filter(student=student).values_list('unit_id', flat=True))
    
    # تجهيز قائمة الوحدات مع تحديد حالتها
    adventure_map_units = []
    for unit in all_units_for_grade:
        status = ''
        if unit.id in completed_unit_ids:
            status = 'completed'
        elif unit.is_published and unit.question_count > 0:
            status = 'unlocked'
        else:
            status = 'locked'
            
        adventure_map_units.append({
            'unit': unit,
            'status': status
        })

    context = {
        'adventure_map_units': adventure_map_units,
        'grade': student.grade,
    }
    return render(request, 'academics/unit_list.html', context)



@login_required
def student_profile_view(request):
    """
    Displays the student's profile with their progress statistics for COMPLETED quizzes,
    and the badges they have earned.
    """
    student = request.user

    # FIX #1: The main query now ONLY fetches results for COMPLETED quizzes.
    results = QuizResult.objects.filter(
        student=student, 
        completed_at__isnull=False
    ).select_related('unit__grade').order_by('-completed_at')

    progress_by_grade = defaultdict(lambda: {'results': [], 'total_quizzes': 0, 'total_score': 0})

    for result in results:
        grade = result.unit.grade
        
        # FIX #2: A safety check to ensure the score is not None before adding.
        if result.score is not None:
            progress_by_grade[grade]['results'].append(result)
            progress_by_grade[grade]['total_quizzes'] += 1
            progress_by_grade[grade]['total_score'] += result.score

    # Calculate the average score for each grade
    for grade, data in progress_by_grade.items():
        if data['total_quizzes'] > 0:
            data['average_score'] = data['total_score'] / data['total_quizzes']
        else:
            data['average_score'] = 0
    
    # Fetch the student's badges
    student_badges = StudentBadge.objects.filter(student=student).select_related('badge').order_by('-awarded_at')

    context = {
        'student': student,
        'progress_by_grade': dict(progress_by_grade),
        'student_badges': student_badges,
    }
    return render(request, 'academics/student_profile.html', context)


@login_required
def leaderboard_selection_view(request):
    """
    Directs the student to the leaderboard for their specific grade.
    """
    student = request.user
    
    # Check if the user is a student and has a grade assigned
    if student.user_type == 'STUDENT' and student.grade:
        # If so, redirect them directly to the detail page for their grade's leaderboard
        return redirect(reverse('academics:leaderboard_detail', kwargs={'grade_id': student.grade.id}))
    else:
        # If they don't have a grade, send them back to their main dashboard
        return redirect('academics:unit_list')

@login_required
def leaderboard_view(request, grade_id):
    student = request.user
    if not student.grade or student.grade.id != int(grade_id):
        return redirect(reverse('academics:leaderboard_detail', kwargs={'grade_id': student.grade.id}))

    grade = get_object_or_404(Grade, id=grade_id)

    # --- FIX: Use 'quizresult' (singular) instead of 'quiz_results' ---
    students_in_grade = User.objects.filter(grade=grade, user_type='STUDENT').annotate(
        total_quizzes=Count('quizresult', filter=Q(quizresult__completed_at__isnull=False)),
        average_score=Avg('quizresult__score', filter=Q(quizresult__completed_at__isnull=False))
    ).filter(total_quizzes__gt=0)

    top_scorers = students_in_grade.order_by('-average_score', '-total_quizzes')[:10]
    most_active = students_in_grade.order_by('-total_quizzes', '-average_score')[:10]

    fastest_solvers = User.objects.filter(
        grade=grade,
        user_type='STUDENT',
        quizresult__score=100
    ).annotate(
        avg_time_seconds=Avg('quizresult__time_taken_seconds', filter=Q(quizresult__score=100))
    ).order_by('avg_time_seconds')[:10]

    context = {
        'grade': grade,
        'top_scorers': top_scorers,
        'most_active': most_active,
        'fastest_solvers': fastest_solvers,
    }
    return render(request, 'academics/leaderboard_detail.html', context)



@login_required
def review_mistakes_view(request):
    """
    Displays the review mistakes page, where all questions
    the student answered incorrectly are grouped by unit.
    """
    student = request.user
    
    # Fetch all of the student's incorrect answers
    incorrect_answers = StudentAnswer.objects.filter(
        quiz_result__student=student,  # <-- CORRECTED THIS LINE
        is_correct=False
    ).select_related('question__unit').order_by('question__unit__unit_number', 'question__order')

    # Group the answers by unit using an ordered dictionary
    mistakes_by_unit = OrderedDict()
    for answer in incorrect_answers:
        unit = answer.question.unit
        if unit not in mistakes_by_unit:
            mistakes_by_unit[unit] = []
        
        # Add details for review
        correct_answer_obj = answer.question.answers.filter(is_correct=True).first()
        mistakes_by_unit[unit].append({
            'question': answer.question,
            'student_answer': answer.text_answer or answer.selected_answer,
            'correct_answer': correct_answer_obj
        })

    context = {
        'mistakes_by_unit': mistakes_by_unit
    }
    return render(request, 'academics/review_mistakes.html', context)
