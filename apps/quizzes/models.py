# /apps/quizzes/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.academics.models import Unit

class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'MCQ', _('Multiple Choice (Text)')
        IMAGE_CHOICE = 'MCQI', _('Multiple Choice (Image)')
        TRUE_FALSE = 'TF', _('True/False')
        SHORT_ANSWER = 'SA', _('Short Answer')
        FILL_IN_THE_BLANK = 'FITB', _('Fill in the Blank')
        MATCHING = 'MATCH', _('Matching (Text)')
        MATCHING_IMAGE = 'MATI', _('Matching (Image/Mixed)')

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(_('Question Text'), max_length=500, help_text="For Fill in the Blank, use '___'. For Matching, describe the task, e.g., 'Match the number to the image.'")
    question_type = models.CharField(_('Question Type'), max_length=5, choices=QuestionType.choices)
    order = models.PositiveIntegerField(_('Order'), default=1)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(_('Answer Text'), max_length=500, blank=True, null=True, help_text="Use for text-based answers (MCQ, TF, SA, FITB).")
    answer_image = models.ImageField(_('Answer Image'), upload_to='answer_images/', blank=True, null=True, help_text="Use for image-based choice questions (MCQI).")
    is_correct = models.BooleanField(_('Is Correct'), default=False)

    def __str__(self):
        if self.answer_text:
            return self.answer_text
        elif self.answer_image:
            return self.answer_image.url
        return f"Answer for {self.question.id}"

# In apps/quizzes/models.py

class QuizResult(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    
    # MODIFIED: Score can be null until the quiz is completed
    score = models.FloatField(null=True, blank=True) 
    
    # NEW: The exact time the student started the quiz for the first time
    start_time = models.DateTimeField(auto_now_add=True)
    
    # MODIFIED: This will be set only upon successful submission
    completed_at = models.DateTimeField(null=True, blank=True)
    
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.unit.title}"


class StudentAnswer(models.Model):
    quiz_result = models.ForeignKey(QuizResult, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.CharField(max_length=500, blank=True, null=True)
    matching_answer = models.JSONField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quiz_result.student.username}'s answer for {self.question.question_text[:20]}"

class MatchingPair(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='matching_pairs')
    prompt_text = models.CharField(_('Prompt Text'), max_length=255, blank=True, null=True, help_text="Use for text prompts.")
    match_text = models.CharField(_('Correct Match Text'), max_length=255, blank=True, null=True, help_text="Use for text matches.")
    prompt_image = models.ImageField(_('Prompt Image'), upload_to='matching_images/', blank=True, null=True, help_text="Use for image prompts.")
    match_image = models.ImageField(_('Correct Match Image'), upload_to='matching_images/', blank=True, null=True, help_text="Use for image matches.")

    def __str__(self):
        prompt = self.prompt_text or (self.prompt_image.url if self.prompt_image else 'Image')
        match = self.match_text or (self.match_image.url if self.match_image else 'Image')
        return f"{prompt} -> {match}"

class Badge(models.Model):
    """
    يمثل شارة إنجاز يمكن للطالب الحصول عليها.
    يقوم المسؤول بإنشاء هذه الشارات من لوحة التحكم.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='badge_icons/', help_text="Upload an icon for the badge.")
    # مفتاح فريد لنتحقق من الشارة في الكود
    slug = models.SlugField(unique=True, help_text="A unique key for the badge, e.g., 'perfect_score'.")

    def __str__(self):
        return self.name

class StudentBadge(models.Model):
    """
    يربط بين الطالب والشارة التي حصل عليها، مع عدّاد.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1, help_text="Number of times this badge has been awarded.")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # يضمن أن كل طالب لديه شارة واحدة فقط من كل نوع
        unique_together = ('student', 'badge')

    def __str__(self):
        return f"{self.student.username} - {self.badge.name} (x{self.count})"
