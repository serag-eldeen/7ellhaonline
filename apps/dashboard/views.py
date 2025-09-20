
from django.shortcuts import get_object_or_404
from apps.users.models import User # Make sure User is imported
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django import forms
# /apps/dashboard/views.py
from django.db.models import Avg, Count, F, Q, ExpressionWrapper, FloatField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Avg, Count
from django.db import transaction
from django.forms import inlineformset_factory
from collections import defaultdict
from django.db.models import Avg, Count, Q, F, FloatField, ExpressionWrapper
from apps.academics.models import Grade, Unit
from apps.quizzes.models import Question, Answer, QuizResult, MatchingPair
from apps.users.models import User
from .forms import AdminStudentCreationForm, AdminStudentUpdateForm
from apps.quizzes.models import Badge
from .forms import BadgeForm # استيراد النموذج الجديد
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
# Make sure Unit is imported if it's not already
from apps.academics.models import Unit
# --- Helper Functions & Mixins ---

def is_admin(user):
    """Checks if a user is an authenticated admin."""
    return user.is_authenticated and user.user_type == 'ADMIN'

class AdminRequiredMixin(UserPassesTestMixin):
    """A mixin for class-based views to ensure the user is an admin."""
    def test_func(self):
        return is_admin(self.request.user)

# --- Main Dashboard View ---

# /apps/dashboard/views.py

# /apps/dashboard/views.py
@user_passes_test(is_admin)
def dashboard_home_view(request):
    """
    An advanced dashboard with summary cards, management tools, and nested analytics.
    """
    # --- Platform-wide Summary Stats ---
    total_students = User.objects.filter(user_type='STUDENT').count()
    total_quizzes_taken = QuizResult.objects.filter(completed_at__isnull=False).count()
    overall_average_score = QuizResult.objects.filter(completed_at__isnull=False).aggregate(average=Avg('score'))['average'] or 0

    # --- Content Analytics (grouped by Grade) ---
    content_analytics_by_grade = []
    all_grades = Grade.objects.prefetch_related('units').order_by('name')

    for grade in all_grades:
        # FIX: Changed 'quiz_results' to 'quizresult' in the two lines below
        difficult_units_qs = Unit.objects.filter(grade=grade, is_published=True).annotate(
            average_score=Avg('quizresult__score'),
            attempts=Count('quizresult')
        ).filter(attempts__gt=0).order_by('average_score')[:3]

        # For each of those difficult units, find its top 5 difficult questions
        units_with_questions_data = []
        for unit in difficult_units_qs:
            difficult_questions_qs = Question.objects.filter(unit=unit).annotate(
                total_attempts=Count('studentanswer'),
                correct_attempts=Count('studentanswer', filter=Q(studentanswer__is_correct=True))
            ).filter(total_attempts__gt=0).annotate(
                success_rate=ExpressionWrapper(
                    (F('correct_attempts') * 100.0 / F('total_attempts')),
                    output_field=FloatField()
                )
            ).order_by('success_rate')[:5]

            if difficult_questions_qs.exists():
                units_with_questions_data.append({
                    'unit': unit,
                    'questions': difficult_questions_qs
                })

        if units_with_questions_data:
            content_analytics_by_grade.append({
                'grade': grade,
                'units_data': units_with_questions_data
            })

    # --- Student Analytics ---
    students_per_grade = Grade.objects.annotate(
        student_count=Count('students', filter=Q(students__user_type='STUDENT'))
    ).order_by('name')

    # FIX: Changed 'quiz_results' to 'quizresult' in the line below
    most_active_students = User.objects.filter(user_type='STUDENT').annotate(
        quiz_count=Count('quizresult')
    ).filter(quiz_count__gt=0).order_by('-quiz_count')[:5]

    context = {
        'total_students': total_students,
        'total_quizzes_taken': total_quizzes_taken,
        'overall_average_score': overall_average_score,
        'content_analytics_by_grade': content_analytics_by_grade,
        'students_per_grade': students_per_grade,
        'most_active_students': most_active_students,
    }
    return render(request, 'dashboard/home.html', context)
# --- Grade Management Views ---

class GradeListView(AdminRequiredMixin, ListView):
    model = Grade
    template_name = 'dashboard/grade_list.html'
    context_object_name = 'grades'

class GradeCreateView(AdminRequiredMixin, CreateView):
    model = Grade
    template_name = 'dashboard/grade_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('dashboard:grade_list')

class GradeUpdateView(AdminRequiredMixin, UpdateView):
    model = Grade
    template_name = 'dashboard/grade_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('dashboard:grade_list')

class GradeDeleteView(AdminRequiredMixin, DeleteView):
    model = Grade
    template_name = 'dashboard/grade_confirm_delete.html'
    success_url = reverse_lazy('dashboard:grade_list')

# --- Unit Management Views ---

class UnitListView(AdminRequiredMixin, ListView):
    model = Unit
    template_name = 'dashboard/unit_list.html'
    context_object_name = 'units' # سنستخدم اسمًا جديدًا في السياق

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # جلب جميع الوحدات مع ترتيبها حسب الصف ثم رقم الوحدة
        all_units = Unit.objects.select_related('grade').order_by('grade__name', 'unit_number')

        # إنشاء قاموس منظم لتجميع الوحدات
        units_by_grade = OrderedDict()
        for unit in all_units:
            grade = unit.grade
            if grade not in units_by_grade:
                units_by_grade[grade] = []
            units_by_grade[grade].append(unit)

        # إضافة القاموس المجمع إلى السياق ليستخدمه القالب
        context['units_by_grade'] = units_by_grade
        return context

class UnitCreateView(AdminRequiredMixin, CreateView):
    model = Unit
    template_name = 'dashboard/unit_form.html'
    # Add 'is_published' to this list
    fields = ['grade', 'title', 'description', 'unit_number', 'duration_minutes', 'is_published']
    success_url = reverse_lazy('dashboard:unit_list')

class UnitUpdateView(AdminRequiredMixin, UpdateView):
    model = Unit
    template_name = 'dashboard/unit_form.html'
    # Add 'is_published' to this list too
    fields = ['grade', 'title', 'description', 'unit_number', 'duration_minutes', 'is_published']
    success_url = reverse_lazy('dashboard:unit_list')

class UnitDeleteView(AdminRequiredMixin, DeleteView):
    model = Unit
    template_name = 'dashboard/unit_confirm_delete.html'
    success_url = reverse_lazy('dashboard:unit_list')

# --- Question Management Views (Updated) ---

AnswerFormSet = inlineformset_factory(
    Question, Answer,
    fields=('answer_text', 'answer_image', 'is_correct'),
    extra=5,
    can_delete=True
)

MatchingPairFormSet = inlineformset_factory(
    Question, MatchingPair,
    fields=('prompt_text', 'prompt_image', 'match_text', 'match_image'),
    extra=5,
    can_delete=True
)

class QuestionListView(AdminRequiredMixin, ListView):
    model = Question
    template_name = 'dashboard/question_list.html'
    context_object_name = 'questions' # This name is for the original flat list, which we'll replace in the context

    def get_context_data(self, **kwargs):
        # Start with the default context
        context = super().get_context_data(**kwargs)

        # Get all questions, pre-loading related data for efficiency and ordering them logically
        all_questions = Question.objects.select_related('unit__grade').order_by('unit__grade__name', 'unit__unit_number', 'order')

        # Create an ordered dictionary to hold questions grouped by grade
        questions_by_grade = OrderedDict()
        for question in all_questions:
            # Check if the question is properly linked to a grade
            if question.unit and question.unit.grade:
                grade = question.unit.grade
                if grade not in questions_by_grade:
                    questions_by_grade[grade] = []
                questions_by_grade[grade].append(question)

        # Add our new, grouped dictionary to the context for the template to use
        context['questions_by_grade'] = questions_by_grade
        return context

class QuestionCreateView(AdminRequiredMixin, CreateView):
    model = Question
    template_name = 'dashboard/question_form.html'
    fields = ['unit', 'question_text', 'question_type', 'order']
    success_url = reverse_lazy('dashboard:question_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['answer_formset'] = AnswerFormSet(self.request.POST, self.request.FILES, prefix='answers')
            data['matching_formset'] = MatchingPairFormSet(self.request.POST, self.request.FILES, prefix='matching')
        else:
            data['answer_formset'] = AnswerFormSet(prefix='answers')
            data['matching_formset'] = MatchingPairFormSet(prefix='matching')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        answer_formset = context['answer_formset']
        matching_formset = context['matching_formset']
        question_type = form.cleaned_data.get('question_type')

        with transaction.atomic():
            self.object = form.save()
            if question_type in ['MCQ', 'MCQI', 'TF', 'SA', 'FITB']:
                if answer_formset.is_valid():
                    answer_formset.instance = self.object
                    answer_formset.save()
            elif question_type in ['MATCH', 'MATI']:
                if matching_formset.is_valid():
                    matching_formset.instance = self.object
                    matching_formset.save()
        return super().form_valid(form)

class QuestionUpdateView(AdminRequiredMixin, UpdateView):
    model = Question
    template_name = 'dashboard/question_form.html'
    fields = ['unit', 'question_text', 'question_type', 'order']
    success_url = reverse_lazy('dashboard:question_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['answer_formset'] = AnswerFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='answers')
            data['matching_formset'] = MatchingPairFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='matching')
        else:
            data['answer_formset'] = AnswerFormSet(instance=self.object, prefix='answers')
            data['matching_formset'] = MatchingPairFormSet(instance=self.object, prefix='matching')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        answer_formset = context['answer_formset']
        matching_formset = context['matching_formset']
        question_type = form.cleaned_data.get('question_type')

        with transaction.atomic():
            self.object = form.save()
            if question_type in ['MCQ', 'MCQI', 'TF', 'SA', 'FITB']:
                if answer_formset.is_valid():
                    answer_formset.instance = self.object
                    answer_formset.save()
            elif question_type in ['MATCH', 'MATI']:
                if matching_formset.is_valid():
                    matching_formset.instance = self.object
                    matching_formset.save()
        return super().form_valid(form)

class QuestionDeleteView(AdminRequiredMixin, DeleteView):
    model = Question
    template_name = 'dashboard/question_confirm_delete.html'
    success_url = reverse_lazy('dashboard:question_list')

# --- Student Management Views ---

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/user_list.html'
    context_object_name = 'students'
    def get_queryset(self):
        return User.objects.filter(user_type='STUDENT').select_related('grade').order_by('username')

@user_passes_test(is_admin)
def create_student_view(request):
    if request.method == 'POST':
        form = AdminStudentCreationForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data['password']
            user = form.save()
            request.session['new_student_credentials'] = {'username': user.username, 'password': raw_password}
            return redirect('dashboard:create_student_success')
    else:
        form = AdminStudentCreationForm()
    return render(request, 'dashboard/student_add_form.html', {'form': form})

@user_passes_test(is_admin)
def create_student_success_view(request):
    credentials = request.session.pop('new_student_credentials', None)
    if not credentials:
        return redirect('dashboard:user_list')
    return render(request, 'dashboard/create_student_success.html', {'credentials': credentials})

class StudentUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = AdminStudentUpdateForm
    template_name = 'dashboard/student_update_form.html'
    success_url = reverse_lazy('dashboard:user_list')
    def get_queryset(self):
        return User.objects.filter(user_type='STUDENT')

class StudentDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'dashboard/student_confirm_delete.html'
    success_url = reverse_lazy('dashboard:user_list')
    def get_queryset(self):
        return User.objects.filter(user_type='STUDENT')

@user_passes_test(is_admin)
def student_progress_detail_view(request, pk):
    student = get_object_or_404(User, pk=pk, user_type='STUDENT')
    results = QuizResult.objects.filter(student=student).select_related('unit__grade').order_by('-completed_at')

    progress_by_grade = defaultdict(lambda: {'results': [], 'total_quizzes': 0, 'total_score': 0})
    for result in results:
        grade = result.unit.grade
        progress_by_grade[grade]['results'].append(result)
        progress_by_grade[grade]['total_quizzes'] += 1
        progress_by_grade[grade]['total_score'] += result.score

    for grade, data in progress_by_grade.items():
        if data['total_quizzes'] > 0:
            data['average_score'] = data['total_score'] / data['total_quizzes']
        else:
            data['average_score'] = 0

    context = {
        'student': student,
        'progress_by_grade': dict(progress_by_grade),
    }
    return render(request, 'dashboard/student_progress_detail.html', context)

@user_passes_test(is_admin)
def quiz_attempt_detail_view(request, pk):
    """
    Displays a detailed breakdown of a student's answers for a specific quiz attempt,
    handling all question types with corrected logic.
    """
    quiz_result = get_object_or_404(
        QuizResult.objects.select_related('student', 'unit'),
        pk=pk
    )

    student_answers_qs = quiz_result.student_answers.select_related(
        'question', 'selected_answer'
    ).order_by('question__order')

    detailed_answers = []
    for sa in student_answers_qs:
        question = sa.question
        answer_detail = {
            'question': question,
            'is_correct': sa.is_correct,
            'student_answer': None,
            'correct_answer': None,
            'paired_answers': None, # For matching questions
        }

        if question.question_type in ['MCQ', 'MCQI', 'TF']:
            answer_detail['student_answer'] = sa.selected_answer
            answer_detail['correct_answer'] = question.answers.filter(is_correct=True).first()

        elif question.question_type in ['SA', 'FITB']:
            answer_detail['student_answer'] = sa.text_answer
            answer_detail['correct_answer'] = question.answers.filter(is_correct=True).first().answer_text

        elif question.question_type in ['MATCH', 'MATI']:
            prompts = list(question.matching_pairs.all())
            student_matches_map = {int(k): int(v) for k, v in sa.matching_answer.items()} if sa.matching_answer else {}

            student_ordered_matches = []
            for prompt in prompts:
                student_match_id = student_matches_map.get(prompt.id)
                match_obj = None
                if student_match_id:
                    try:
                        match_obj = MatchingPair.objects.get(id=student_match_id)
                    except MatchingPair.DoesNotExist:
                        pass # Keep it as None if not found
                student_ordered_matches.append(match_obj)

            # Zip the lists together for easy iteration in the template
            answer_detail['paired_answers'] = zip(prompts, student_ordered_matches)

        detailed_answers.append(answer_detail)

    context = {
        'quiz_result': quiz_result,
        'detailed_answers': detailed_answers,
    }
    return render(request, 'dashboard/quiz_attempt_detail.html', context)


# --- Unit Management Views ---

class UnitCreateView(AdminRequiredMixin, CreateView):
    model = Unit
    template_name = 'dashboard/unit_form.html'
    # إضافة الحقل الجديد للنموذج
    fields = ['grade', 'title', 'description', 'unit_number', 'duration_minutes']
    success_url = reverse_lazy('dashboard:unit_list')

class UnitUpdateView(AdminRequiredMixin, UpdateView):
    model = Unit
    template_name = 'dashboard/unit_form.html'
    # إضافة الحقل الجديد للنموذج
    fields = ['grade', 'title', 'description', 'unit_number', 'duration_minutes']
    success_url = reverse_lazy('dashboard:unit_list')

class BadgeListView(AdminRequiredMixin, ListView):
    model = Badge
    template_name = 'dashboard/badge_list.html'
    context_object_name = 'badges'
    ordering = ['name']

class BadgeCreateView(AdminRequiredMixin, CreateView):
    model = Badge
    form_class = BadgeForm
    template_name = 'dashboard/badge_form.html'
    success_url = reverse_lazy('dashboard:badge_list')

class BadgeUpdateView(AdminRequiredMixin, UpdateView):
    model = Badge
    form_class = BadgeForm
    template_name = 'dashboard/badge_form.html'
    success_url = reverse_lazy('dashboard:badge_list')

class BadgeDeleteView(AdminRequiredMixin, DeleteView):
    model = Badge
    template_name = 'dashboard/badge_confirm_delete.html'
    success_url = reverse_lazy('dashboard:badge_list')

@require_POST # Ensures this view only accepts POST requests for security
def toggle_unit_publish_status(request, pk):
    # A simple check to ensure only admins can perform this action
    if not request.user.is_authenticated or not request.user.is_staff: # A better check for admin status
        return redirect('core:home')

    unit = get_object_or_404(Unit, pk=pk)
    # Flip the boolean value (True becomes False, and False becomes True)
    unit.is_published = not unit.is_published
    unit.save()
    # Redirect the admin back to the list of units
    return redirect('dashboard:unit_list')

