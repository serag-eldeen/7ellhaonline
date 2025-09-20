import json
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academics.models import Grade, Unit
from apps.quizzes.models import Question, Answer, MatchingPair

class Command(BaseCommand):
    help = 'Imports grades, units, and questions from JSON files into the database.'

    def add_arguments(self, parser):
        # We define arguments to accept file paths from the command line
        parser.add_argument('--structure-file', type=str, help='The path to the JSON file with grades and units.')
        parser.add_argument('--questions-file', type=str, help='The path to the JSON file with questions.')

    @transaction.atomic # This ensures that all database operations are done in one transaction. If anything fails, everything is rolled back.
    def handle(self, *args, **options):
        structure_file_path = options['structure_file']
        questions_file_path = options['questions_file']

        # Import Grades and Units first if the file is provided
        if structure_file_path:
            self.stdout.write(self.style.SUCCESS(f'Starting import from {structure_file_path}...'))
            with open(structure_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Import Grades
                for grade_data in data.get('grades', []):
                    grade, created = Grade.objects.update_or_create(
                        name=grade_data['name'],
                        defaults={'description': grade_data.get('description', '')}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created Grade: "{grade.name}"'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Updated Grade: "{grade.name}"'))
                
                # Import Units
                for unit_data in data.get('units', []):
                    try:
                        # Find the grade object based on the name provided in the JSON
                        grade = Grade.objects.get(name=unit_data['grade_name'])
                        unit, created = Unit.objects.update_or_create(
                            grade=grade,
                            unit_number=unit_data['unit_number'],
                            defaults={
                                'title': unit_data['title'],
                                'description': unit_data.get('description', ''),
                                'duration_minutes': unit_data.get('duration_minutes', 10)
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'  - Created Unit: "{unit.title}" for {grade.name}'))
                        else:
                             self.stdout.write(self.style.WARNING(f'  - Updated Unit: "{unit.title}" for {grade.name}'))
                    except Grade.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Grade "{unit_data["grade_name"]}" not found. Skipping unit "{unit_data["title"]}".'))
        
        # Import Questions if the file is provided
        if questions_file_path:
            self.stdout.write(self.style.SUCCESS(f'\nStarting question import from {questions_file_path}...'))
            with open(questions_file_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)

                for q_data in questions_data:
                    try:
                        # Find the related unit. We are matching based on the "topic" field from the JSON.
                        # This assumes the 'topic' field starts with the Unit title.
                        unit_title = q_data['topic']
                        unit = Unit.objects.get(title=unit_title)

                        # Create the question object
                        question = Question.objects.create(
                            unit=unit,
                            question_text=q_data['question_text'],
                            question_type=q_data['question_type'],
                            order=Question.objects.filter(unit=unit).count() + 1 # Auto-increment order
                        )

                        # Create related Answer objects
                        for answer_data in q_data.get('answers', []):
                            Answer.objects.create(
                                question=question,
                                answer_text=answer_data['answer_text'],
                                is_correct=answer_data['is_correct']
                            )
                        
                        # Create related MatchingPair objects
                        for pair_data in q_data.get('matching_pairs', []):
                            MatchingPair.objects.create(
                                question=question,
                                prompt_text=pair_data['prompt_text'],
                                match_text=pair_data['match_text']
                            )

                        self.stdout.write(f'    - Imported question: "{question.question_text[:50]}..."')
                    except Unit.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Unit with title "{q_data["topic"]}" not found. Skipping question.'))

        self.stdout.write(self.style.SUCCESS('\nImport process finished.'))