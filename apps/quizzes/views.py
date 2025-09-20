# /apps/quizzes/views.py

import json
import random
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.academics.models import Unit
from .models import Question, Answer, QuizResult, StudentAnswer, MatchingPair, Badge, StudentBadge

@login_required
def take_quiz_view(request, unit_id):
    """
    Handles starting a new quiz, resuming an in-progress one, OR reviewing a completed one.
    """
    unit = get_object_or_404(Unit, id=unit_id, grade=request.user.grade, is_published=True)

    # 1. First, check if there is a COMPLETED attempt. If so, show the review page.
    completed_attempt = QuizResult.objects.filter(
        student=request.user, 
        unit=unit, 
        completed_at__isnull=False
    ).first()

    if completed_attempt:
        # --- REVIEW MODE ---
        detailed_answers = []
        student_answers_qs = completed_attempt.student_answers.select_related('question', 'selected_answer').order_by('question__order')
        for sa in student_answers_qs:
            # (This logic can be expanded to match your quiz_review.html template's needs)
            detailed_answers.append({'question': sa.question, 'student_answer': sa.text_answer or sa.selected_answer, 'is_correct': sa.is_correct})
        
        context = {
            'quiz_result': completed_attempt,
            'detailed_answers': detailed_answers,
        }
        return render(request, 'quizzes/quiz_review.html', context)

    # 2. If no completed attempt, handle the IN-PROGRESS quiz with the persistent timer.
    attempt, created = QuizResult.objects.get_or_create(
        student=request.user,
        unit=unit,
        completed_at__isnull=True
    )

    start_time = attempt.start_time
    duration = timedelta(minutes=unit.duration_minutes)
    end_time = start_time + duration

    if timezone.now() >= end_time:
        if attempt.score is None:
             attempt.score = 0
             attempt.completed_at = timezone.now()
             attempt.save()
             for question in unit.questions.all():
                 # CORRECTED: Use 'text_answer' instead of 'student_answer'
                 StudentAnswer.objects.get_or_create(quiz_result=attempt, question=question, defaults={'text_answer': "Time Out"})
        return redirect('quizzes:quiz_result', result_id=attempt.id)

    time_remaining = end_time - timezone.now()
    time_remaining_seconds = int(time_remaining.total_seconds())
    minutes_remaining = time_remaining_seconds // 60
    seconds_remaining = time_remaining_seconds % 60

    questions = unit.questions.prefetch_related('answers', 'matching_pairs').order_by('order')
    for question in questions:
        if question.question_type in ['MATCH', 'MATI']:
            matches = list(question.matching_pairs.all())
            random.shuffle(matches)
            question.shuffled_matches = matches
            
    context = {
        'unit': unit,
        'questions': questions,
        'time_remaining_seconds': time_remaining_seconds,
        'minutes_remaining': minutes_remaining,
        'seconds_remaining': seconds_remaining,
    }
    return render(request, 'quizzes/quiz.html', context)




@login_required
@require_POST
def submit_quiz_view(request, unit_id):
    """
    Receives quiz submissions, finds the in-progress attempt, updates it with the score,
    and saves all detailed answers.
    """
    try:
        data = json.loads(request.body)
        submitted_answers = data.get('answers', {})
        time_taken = data.get('time_taken_seconds', 0)
        unit = get_object_or_404(Unit, id=unit_id)

        # Find the in-progress quiz attempt. If it doesn't exist, something is wrong.
        result = get_object_or_404(QuizResult, student=request.user, unit=unit, completed_at__isnull=True)

        correct_answers_count = 0
        questions = unit.questions.prefetch_related('answers', 'matching_pairs').all()

        for question in questions:
            question_id_str = str(question.id)
            is_correct = False
            student_answer_obj = StudentAnswer(quiz_result=result, question=question)

            if question.question_type in ['MCQ', 'MCQI', 'TF']:
                answer_id = submitted_answers.get(question_id_str)
                if answer_id:
                    try:
                        selected_answer = Answer.objects.get(id=answer_id, question=question)
                        student_answer_obj.selected_answer = selected_answer
                        if selected_answer.is_correct:
                            is_correct = True
                    except Answer.DoesNotExist:
                        pass

            elif question.question_type in ['SA', 'FITB']:
                text_answer = submitted_answers.get(question_id_str, "").strip()
                student_answer_obj.text_answer = text_answer
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and text_answer.lower() == correct_answer.answer_text.lower():
                    is_correct = True

            elif question.question_type in ['MATCH', 'MATI']:
                matching_answers = submitted_answers.get(question_id_str, {})
                student_answer_obj.matching_answer = matching_answers
                correct_matches = sum(1 for prompt_id, match_id in matching_answers.items() if str(prompt_id) == str(match_id))
                if question.matching_pairs.count() > 0 and correct_matches == question.matching_pairs.count():
                    is_correct = True
            
            if is_correct:
                correct_answers_count += 1
            
            student_answer_obj.is_correct = is_correct
            student_answer_obj.save()

        total_questions = questions.count()
        score = (correct_answers_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Update the existing result object instead of creating a new one
        result.score = score
        result.completed_at = timezone.now()
        result.time_taken_seconds = time_taken
        result.save()

        check_and_award_badges(request.user, result)
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('quizzes:quiz_result', kwargs={'result_id': result.id})
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def quiz_result_view(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, student=request.user)
    return render(request, 'quizzes/quiz_result.html', {'result': result})


@login_required
def certificate_view(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, student=request.user)

    if result.score is None or result.score < 80:
        return HttpResponseForbidden("You are not authorized to view this certificate.")

    return render(request, 'quizzes/certificate.html', {'result': result})


def award_badge(student, badge_slug):
    """
    دالة مساعدة لمنح شارة للطالب أو زيادة عدّادها.
    """
    try:
        badge = Badge.objects.get(slug=badge_slug)
        student_badge, created = StudentBadge.objects.get_or_create(
            student=student,
            badge=badge
        )
        if not created:
            student_badge.count += 1
            student_badge.save()
    except Badge.DoesNotExist:
        pass

def check_and_award_badges(student, quiz_result):
    """
    الدالة الرئيسية التي تتحقق من جميع الشارات بعد تسليم الاختبار.
    """
    # 1. شارة "العلامة الكاملة"
    if quiz_result.score == 100:
        award_badge(student, 'perfect_score')

    # 2. شارة "المثابر" (عند إكمال 5 اختبارات)
    total_quizzes = QuizResult.objects.filter(student=student, completed_at__isnull=False).count()
    if total_quizzes == 5:
        award_badge(student, 'persistent_learner')

    # 3. شارة "المحترف" (عندما يتجاوز متوسط الدرجات 90%)
    avg_score = QuizResult.objects.filter(student=student, completed_at__isnull=False).aggregate(average=Avg('score'))['average']
    if avg_score and avg_score >= 90:
        try:
            badge = Badge.objects.get(slug='pro_student')
            StudentBadge.objects.get_or_create(student=student, badge=badge)
        except Badge.DoesNotExist:
            pass

    # 4. شارة "الصاروخ" (إذا أنهى الاختبار في أقل من نصف الوقت المحدد وحصل على 80% أو أعلى)
    if quiz_result.time_taken_seconds and quiz_result.unit.duration_minutes:
        time_limit_seconds = quiz_result.unit.duration_minutes * 60
        # --- THIS IS THE MODIFIED LOGIC ---
        if quiz_result.time_taken_seconds < (time_limit_seconds / 2) and quiz_result.score >= 80:
            award_badge(student, 'rocket_solver')
